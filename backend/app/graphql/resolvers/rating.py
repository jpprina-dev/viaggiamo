"""Rating resolvers: submitRating mutation + myRatings query."""

import strawberry
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from strawberry.types import Info

from app.graphql.auth import require_auth
from app.graphql.context import Context
from app.graphql.types.rating import RatingType
from app.models.booking import Booking
from app.models.rating import Rating
from app.models.trip import Trip

TERMINAL_STATUSES = {"rejected", "cancelled", "revoked"}


@strawberry.type
class RatingQueries:
    @strawberry.field
    async def my_ratings(self, info: Info[Context, None]) -> list[RatingType]:
        """Return all ratings submitted by the current user."""
        context = info.context
        user = require_auth(context)

        result = await context.db.execute(
            select(Rating).where(Rating.rater_id == user.id)
        )
        ratings = result.scalars().all()
        return [
            RatingType(
                id=r.id,
                booking_id=r.booking_id,
                rater_id=r.rater_id,
                ratee_id=r.ratee_id,
                score=r.score,
                comment=r.comment,
                created_at=r.created_at,
            )
            for r in ratings
        ]


@strawberry.type
class RatingMutations:
    @strawberry.mutation
    async def submit_rating(
        self,
        info: Info[Context, None],
        booking_id: int,
        score: int,
        comment: str | None = None,
    ) -> RatingType:
        """Submit a rating for the other party in a booking."""
        context = info.context
        user = require_auth(context)

        if score < 1 or score > 5:
            raise ValueError("Score must be between 1 and 5")

        # Fetch the booking
        result = await context.db.execute(
            select(Booking).where(Booking.id == booking_id)
        )
        booking = result.scalar_one_or_none()
        if not booking:
            raise ValueError("Booking not found")

        # Determine role and ratee
        trip_result = await context.db.execute(
            select(Trip).where(Trip.id == booking.trip_id)
        )
        trip = trip_result.scalar_one_or_none()
        if not trip:
            raise ValueError("Trip not found")

        is_passenger = booking.passenger_id == user.id
        is_driver = trip.driver_id == user.id

        if not is_passenger and not is_driver:
            raise ValueError("FORBIDDEN")

        # Must be in a terminal/completed state
        is_terminal = booking.status in TERMINAL_STATUSES
        is_completed = trip.is_completed
        if not is_terminal and not is_completed:
            raise ValueError("UNPROCESSABLE")

        # Determine ratee
        ratee_id = trip.driver_id if is_passenger else booking.passenger_id

        rating = Rating(
            booking_id=booking_id,
            rater_id=user.id,
            ratee_id=ratee_id,
            score=score,
            comment=comment,
        )
        context.db.add(rating)

        try:
            await context.db.flush()
        except IntegrityError as err:
            await context.db.rollback()
            raise ValueError("ALREADY_RATED") from err

        await context.db.commit()
        await context.db.refresh(rating)

        return RatingType(
            id=rating.id,
            booking_id=rating.booking_id,
            rater_id=rating.rater_id,
            ratee_id=rating.ratee_id,
            score=rating.score,
            comment=rating.comment,
            created_at=rating.created_at,
        )
