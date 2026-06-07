"""Tests for ChatService — TDD vertical-slice."""

from datetime import timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.datetime_utils import utcnow
from app.graphql.exceptions import ForbiddenError
from app.models.chat import (
    Message,
    MessageKind,
    SystemEventType,
    ThreadReadState,
)
from app.models.trip import Trip
from app.models.user import User
from app.models.vehicle import Vehicle
from app.services.chat_service import CHAT_OPEN_WINDOW_HOURS, ChatService


async def _make_user(
    db: AsyncSession, *, email: str = "u@test.com", name: str = "Test"
) -> User:
    user = User(
        email=email,
        name=name,
        last_name="User",
        username=email.split("@")[0],
        hashed_password="x",
        phone="1111111111",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def _make_trip(
    db: AsyncSession,
    driver_id: int,
    *,
    departure_time=None,
    is_active: bool = True,
) -> Trip:
    vehicle = Vehicle(
        user_id=driver_id,
        make="Toyota",
        model="Corolla",
        year=2020,
        license_plate=f"ABC{driver_id}",
        seats=4,
    )
    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)

    trip = Trip(
        driver_id=driver_id,
        vehicle_id=vehicle.id,
        origin_name="A",
        destination_name="B",
        departure_time=departure_time or utcnow() + timedelta(hours=2),
        total_seats=4,
        available_seats=4,
        price_per_seat=1000,
        origin_locality_id="060700",
        destination_locality_id="060710",
        is_active=is_active,
        trip_legal_compliance_ack=True,
    )
    db.add(trip)
    await db.commit()
    await db.refresh(trip)
    return trip


async def _fetch_warnings(db: AsyncSession, thread_id: int) -> list[Message]:
    result = await db.execute(
        select(Message).where(
            Message.thread_id == thread_id,
            Message.event_type == SystemEventType.contact_warning,
        )
    )
    return list(result.scalars().all())


async def _fetch_read_states(
    db: AsyncSession, thread_id: int, user_id: int
) -> list[ThreadReadState]:
    result = await db.execute(
        select(ThreadReadState).where(
            ThreadReadState.thread_id == thread_id,
            ThreadReadState.user_id == user_id,
        )
    )
    return list(result.scalars().all())


@pytest.mark.asyncio
async def test_get_or_create_thread_creates_new(db_session: AsyncSession) -> None:
    driver = await _make_user(db_session, email="driver@test.com")
    passenger = await _make_user(db_session, email="pax@test.com")
    trip = await _make_trip(db_session, driver.id)

    service = ChatService(db_session)
    thread = await service.get_or_create_thread(trip.id, passenger.id)

    assert thread.id is not None
    assert thread.trip_id == trip.id
    assert thread.passenger_user_id == passenger.id


@pytest.mark.asyncio
async def test_get_or_create_thread_is_idempotent(db_session: AsyncSession) -> None:
    driver = await _make_user(db_session, email="driver@test.com")
    passenger = await _make_user(db_session, email="pax@test.com")
    trip = await _make_trip(db_session, driver.id)

    service = ChatService(db_session)
    first = await service.get_or_create_thread(trip.id, passenger.id)
    second = await service.get_or_create_thread(trip.id, passenger.id)

    assert first.id == second.id


@pytest.mark.asyncio
async def test_send_user_message_persists(db_session: AsyncSession) -> None:
    driver = await _make_user(db_session, email="driver@test.com")
    passenger = await _make_user(db_session, email="pax@test.com")
    trip = await _make_trip(db_session, driver.id)

    service = ChatService(db_session)
    thread = await service.get_or_create_thread(trip.id, passenger.id)
    message = await service.send_user_message(
        thread.id, passenger.id, "Hola, sale el viaje?"
    )

    assert message.id is not None
    assert message.thread_id == thread.id
    assert message.kind == MessageKind.user
    assert message.sender_id == passenger.id
    assert message.body == "Hola, sale el viaje?"
    assert message.event_type is None


@pytest.mark.asyncio
async def test_send_user_message_inserts_contact_warning(
    db_session: AsyncSession,
) -> None:
    driver = await _make_user(db_session, email="driver@test.com")
    passenger = await _make_user(db_session, email="pax@test.com")
    trip = await _make_trip(db_session, driver.id)

    service = ChatService(db_session)
    thread = await service.get_or_create_thread(trip.id, passenger.id)
    user_message = await service.send_user_message(
        thread.id, passenger.id, "escribime a juan@gmail.com"
    )

    # The user message is delivered without blocking.
    assert user_message.kind == MessageKind.user
    assert user_message.body == "escribime a juan@gmail.com"

    warnings = await _fetch_warnings(db_session, thread.id)
    assert len(warnings) == 1
    assert warnings[0].kind == MessageKind.system
    assert warnings[0].sender_id is None
    assert (
        warnings[0].body
        == "Compartir datos personales fuera de Viajamos reduce tu protección."
    )


@pytest.mark.asyncio
async def test_send_user_message_does_not_duplicate_warning(
    db_session: AsyncSession,
) -> None:
    driver = await _make_user(db_session, email="driver@test.com")
    passenger = await _make_user(db_session, email="pax@test.com")
    trip = await _make_trip(db_session, driver.id)

    service = ChatService(db_session)
    thread = await service.get_or_create_thread(trip.id, passenger.id)
    await service.send_user_message(thread.id, passenger.id, "mail: a@b.com")
    await service.send_user_message(thread.id, passenger.id, "otro: c@d.com")

    warnings = await _fetch_warnings(db_session, thread.id)
    assert len(warnings) == 1


@pytest.mark.asyncio
async def test_send_user_message_without_contact_has_no_warning(
    db_session: AsyncSession,
) -> None:
    driver = await _make_user(db_session, email="driver@test.com")
    passenger = await _make_user(db_session, email="pax@test.com")
    trip = await _make_trip(db_session, driver.id)

    service = ChatService(db_session)
    thread = await service.get_or_create_thread(trip.id, passenger.id)
    await service.send_user_message(thread.id, passenger.id, "Nos vemos en la plaza")

    warnings = await _fetch_warnings(db_session, thread.id)
    assert warnings == []


@pytest.mark.asyncio
async def test_get_messages_orders_chronologically(db_session: AsyncSession) -> None:
    driver = await _make_user(db_session, email="driver@test.com")
    passenger = await _make_user(db_session, email="pax@test.com")
    trip = await _make_trip(db_session, driver.id)

    service = ChatService(db_session)
    thread = await service.get_or_create_thread(trip.id, passenger.id)
    await service.send_user_message(thread.id, passenger.id, "primero")
    await service.send_user_message(thread.id, driver.id, "segundo")

    # Both participants can read.
    for reader_id in (passenger.id, driver.id):
        messages = await service.get_messages(thread.id, reader_id)
        bodies = [m.body for m in messages]
        assert bodies == ["primero", "segundo"]


@pytest.mark.asyncio
async def test_get_messages_forbidden_for_non_participant(
    db_session: AsyncSession,
) -> None:
    driver = await _make_user(db_session, email="driver@test.com")
    passenger = await _make_user(db_session, email="pax@test.com")
    outsider = await _make_user(db_session, email="outsider@test.com")
    trip = await _make_trip(db_session, driver.id)

    service = ChatService(db_session)
    thread = await service.get_or_create_thread(trip.id, passenger.id)

    with pytest.raises(ForbiddenError):
        await service.get_messages(thread.id, outsider.id)


@pytest.mark.asyncio
async def test_mark_read_upserts_last_read_at(db_session: AsyncSession) -> None:
    driver = await _make_user(db_session, email="driver@test.com")
    passenger = await _make_user(db_session, email="pax@test.com")
    trip = await _make_trip(db_session, driver.id)

    service = ChatService(db_session)
    thread = await service.get_or_create_thread(trip.id, passenger.id)

    await service.mark_read(thread.id, passenger.id)
    states = await _fetch_read_states(db_session, thread.id, passenger.id)
    assert len(states) == 1
    assert states[0].last_read_at is not None

    # Second call updates in place — no duplicate row.
    await service.mark_read(thread.id, passenger.id)
    states = await _fetch_read_states(db_session, thread.id, passenger.id)
    assert len(states) == 1
    assert states[0].last_read_at is not None


@pytest.mark.asyncio
async def test_get_unread_count_excludes_system_messages(
    db_session: AsyncSession,
) -> None:
    driver = await _make_user(db_session, email="driver@test.com")
    passenger = await _make_user(db_session, email="pax@test.com")
    trip = await _make_trip(db_session, driver.id)

    service = ChatService(db_session)
    thread = await service.get_or_create_thread(trip.id, passenger.id)

    # No read state yet: counts all incoming user messages for the passenger.
    await service.send_user_message(thread.id, driver.id, "hola pasajero")
    await service.insert_system_message(thread.id, SystemEventType.booking_accepted)

    count = await service.get_unread_count(thread.id, passenger.id)
    assert count == 1


@pytest.mark.asyncio
async def test_insert_system_message_sets_fixed_body(
    db_session: AsyncSession,
) -> None:
    driver = await _make_user(db_session, email="driver@test.com")
    passenger = await _make_user(db_session, email="pax@test.com")
    trip = await _make_trip(db_session, driver.id)

    service = ChatService(db_session)
    thread = await service.get_or_create_thread(trip.id, passenger.id)
    message = await service.insert_system_message(
        thread.id, SystemEventType.seat_requested
    )

    assert message.kind == MessageKind.system
    assert message.sender_id is None
    assert message.event_type == SystemEventType.seat_requested
    assert message.body  # non-empty fixed text


@pytest.mark.asyncio
async def test_get_unread_count_excludes_own_messages(
    db_session: AsyncSession,
) -> None:
    driver = await _make_user(db_session, email="driver@test.com")
    passenger = await _make_user(db_session, email="pax@test.com")
    trip = await _make_trip(db_session, driver.id)

    service = ChatService(db_session)
    thread = await service.get_or_create_thread(trip.id, passenger.id)

    # Passenger sends two; driver sends one. From the passenger's POV only the
    # driver's message is unread.
    await service.send_user_message(thread.id, passenger.id, "uno")
    await service.send_user_message(thread.id, passenger.id, "dos")
    await service.send_user_message(thread.id, driver.id, "respuesta")

    count = await service.get_unread_count(thread.id, passenger.id)
    assert count == 1


@pytest.mark.asyncio
async def test_get_unread_count_respects_last_read_at(
    db_session: AsyncSession,
) -> None:
    driver = await _make_user(db_session, email="driver@test.com")
    passenger = await _make_user(db_session, email="pax@test.com")
    trip = await _make_trip(db_session, driver.id)

    service = ChatService(db_session)
    thread = await service.get_or_create_thread(trip.id, passenger.id)
    await service.send_user_message(thread.id, driver.id, "antes")
    await service.mark_read(thread.id, passenger.id)

    # After marking read, nothing pending.
    assert await service.get_unread_count(thread.id, passenger.id) == 0


@pytest.mark.asyncio
async def test_is_closed_when_trip_inactive(db_session: AsyncSession) -> None:
    driver = await _make_user(db_session, email="driver@test.com")
    passenger = await _make_user(db_session, email="pax@test.com")
    trip = await _make_trip(db_session, driver.id, is_active=False)

    service = ChatService(db_session)
    thread = await service.get_or_create_thread(trip.id, passenger.id)
    full_thread = await service._get_thread_with_trip(thread.id)

    assert service._is_closed(full_thread) is True


@pytest.mark.asyncio
async def test_is_closed_when_past_window(db_session: AsyncSession) -> None:
    driver = await _make_user(db_session, email="driver@test.com")
    passenger = await _make_user(db_session, email="pax@test.com")
    past = utcnow() - timedelta(hours=CHAT_OPEN_WINDOW_HOURS + 1)
    trip = await _make_trip(db_session, driver.id, departure_time=past)

    service = ChatService(db_session)
    thread = await service.get_or_create_thread(trip.id, passenger.id)
    full_thread = await service._get_thread_with_trip(thread.id)

    assert service._is_closed(full_thread) is True


@pytest.mark.asyncio
async def test_is_open_within_window(db_session: AsyncSession) -> None:
    driver = await _make_user(db_session, email="driver@test.com")
    passenger = await _make_user(db_session, email="pax@test.com")
    trip = await _make_trip(db_session, driver.id)

    service = ChatService(db_session)
    thread = await service.get_or_create_thread(trip.id, passenger.id)
    full_thread = await service._get_thread_with_trip(thread.id)

    assert service._is_closed(full_thread) is False
