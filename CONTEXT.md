# Viajamos

Plataforma de carpooling que conecta conductores que publican viajes con pasajeros que los reservan. El modelo central es la relación Driver → Trip → Booking → Passenger.

## Language

### Actores

**Driver** (Conductor):
Un **User** en el rol de conductor: crea **Trips**, acepta o rechaza **Bookings** y puede revocar reservas aceptadas.
_Avoid_: host, owner, creator

**Passenger** (Pasajero):
Un **User** en el rol de pasajero: solicita una **Booking** en un **Trip** publicado por un **Driver**.
_Avoid_: rider, client, traveler

**User**:
Cuenta registrada en la plataforma; puede actuar como **Driver**, como **Passenger**, o como ambos en distintos viajes simultáneamente.
_Avoid_: account, member, profile

### Viajes

**Trip**:
Un viaje publicado por un **Driver** con origen, destino, fecha/hora de salida, precio por asiento y capacidad. Un **Trip** tiene estado implícito derivado de `is_active` + `is_completed`: activo (upcoming), completado o cancelado/inactivo.
_Avoid_: ride, journey, route

**Locality**:
Una localidad geográfica del catálogo georef-ar (provincia, departamento, nombre). Los **Trips** referencian dos **Localities** (origen y destino) mediante Foreign Key; el nombre se desnormaliza como snapshot inmutable al momento de creación.
_Avoid_: city, location, place, destination (como sustantivo independiente)

**Snapshot** (de localidad):
Copia inmutable del nombre de la **Locality** almacenada en el **Trip** (`origin_name`, `destination_name`). Si georef-ar renombra la localidad, el snapshot no cambia.

### Reservas

**Booking**:
Solicitud de un **Passenger** para ocupar asientos en un **Trip**. Atraviesa una máquina de estados: `pending → accepted | rejected` (por el **Driver**), `pending | accepted → cancelled` (por el **Passenger**), `accepted → revoked` (por el **Driver**).
_Avoid_: reservation, request (solo en contexto de código interno)

**BookingStatus**:
Estado de una **Booking**: `pending`, `accepted`, `rejected`, `cancelled`, `revoked`. Los estados terminales (`rejected`, `cancelled`, `revoked`) no pueden transicionarse.

**Seat Delta**:
Cambio en `available_seats` del **Trip** al transicionar una **Booking**. Solo `accepted` holds seats; transicionar hacia `accepted` consume asientos (−N), transicionar fuera libera asientos (+N).

### Valoraciones

**Rating**:
Valoración (score 1–5 + comentario opcional) que un **User** deja sobre otro tras un **Booking** aceptado. Existe una por par `(booking_id, rater_id)`.
_Avoid_: review, score (como sustantivo independiente)

### Auditoría

**BookingAuditLog**:
Registro append-only de cada transición de estado de una **Booking**, con el actor que la ejecutó y su rol (`driver` | `passenger`). Nunca se modifica.

**RequestDecisionEvent**:
Registro de cada decisión sobre una **Booking** que incluye el delta de asientos aplicado. Coexiste con **BookingAuditLog**; ambos rastrean transiciones desde perspectivas distintas.

### Vehículos

**Vehicle**:
Automóvil registrado por un **User** con capacidad (`seats`), placa y datos de marca/modelo. Un **Driver** asocia un **Vehicle** a cada **Trip** que publica.

## Relationships

- Un **User** puede publicar muchos **Trips** (como **Driver**) y tener muchas **Bookings** (como **Passenger**)
- Un **Trip** tiene exactamente una **Locality** de origen y una de destino (snapshot inmutable)
- Un **Trip** tiene muchas **Bookings**; cada **Booking** pertenece a un único **Passenger**
- Un **Vehicle** pertenece a un **User** y puede usarse en múltiples **Trips**
- Un **Rating** pertenece a exactamente una **Booking** y a un par (rater, ratee)
- Cada transición de **BookingStatus** genera un **BookingAuditLog** y un **RequestDecisionEvent**

## Allowed booking transitions

```
pending  ──[driver]──▶  accepted
pending  ──[driver]──▶  rejected        (terminal)
pending  ──[passenger]▶ cancelled       (terminal)
accepted ──[passenger]▶ cancelled       (terminal)
accepted ──[driver]──▶  revoked         (terminal)
```

## Example dialogue

> **Dev:** "Si el conductor cancela el viaje, ¿qué pasa con las Bookings?"
> **Domain expert:** "El conductor no 'cancela' un Trip directamente. Puede revocar cada Booking aceptada — eso libera los asientos. El Trip queda inactivo (`is_active=false`) por decisión del conductor. No hay una transición automática en cascada."

> **Dev:** "¿Un Passenger puede re-reservar después de cancelar?"
> **Domain expert:** "Sí. Cancelled, rejected y revoked son terminales para esa Booking, pero el índice único solo bloquea duplicados en estados no-terminales — el Passenger puede crear una nueva Booking en el mismo Trip."

### Chat

**Thread**:
Hilo de mensajes 1:1 entre un **Passenger** y el **Driver** de un **Trip** específico. La clave natural es `(trip_id, passenger_user_id)`. Existe independientemente de si hay una **Booking**: puede abrirse antes de reservar, sobrevive a bookings rechazadas o canceladas, y si el **Passenger** crea una nueva **Booking** en el mismo **Trip**, el hilo continúa siendo el mismo. Se crea via `get_or_create` en dos momentos: al enviar el primer mensaje (consulta previa) o al crear una **Booking** (para alojar el system message `seat_requested`).
_Avoid_: conversation, chat, room, channel

**Message**:
Entrada en un **Thread**. Tiene un campo `kind: user | system`. Los mensajes `user` tienen `sender_id` (FK a **User**). Los mensajes `system` tienen `sender_id` null y un `event_type` que identifica el evento de dominio que los originó. Ambos tipos se ordenan cronológicamente en la misma lista.
_Avoid_: post, event (para mensajes de usuario), notification (para mensajes de sistema dentro del hilo)

**ThreadState** (derivado, no almacenado):
Estado de un **Thread** calculado en runtime. `open` si el **Trip** está activo y `now ≤ trip.departure_time + 24h`. `closed` si `trip.is_active = false` (cancelado) o si `now > trip.departure_time + 24h` (ventana de post-viaje expirada). No existe un campo `closed_at` — el estado se deriva del **Trip**.
_Avoid_: status (como campo explícito en la tabla Thread)

**ThreadAccess**:
Reglas de autorización sobre un **Thread**. Solo el **Passenger** puede abrir un Thread nuevo (el **Driver** no inicia hilos). Ambos participantes pueden leer y enviar mensajes en un Thread existente. Solo el **Driver** puede listar todos los Threads de su **Trip**. Solo el **Passenger** puede listar sus propios Threads como pasajero.

**ThreadReadState**:
Registro del último momento en que un **User** leyó un **Thread**. Clave `(thread_id, user_id)` con campo `last_read_at`. Al abrir el **Thread** se hace upsert con `last_read_at = now`. El unread count se calcula como `COUNT(messages WHERE created_at > last_read_at AND sender_id ≠ current_user AND kind = 'user')`. Los mensajes de sistema nunca generan badge de no leído.
_Avoid_: read_receipt, seen_at

**SystemEventType**:
Enum de tipos de mensajes de sistema que puede contener un **Thread**. Alcance v1: `seat_requested` (Booking creada), `booking_accepted` (Driver acepta), `booking_rejected` (Driver rechaza), `trip_cancelled` (Trip cancelado), `contact_warning` (datos de contacto detectados). Fuera de scope v1 por requerir background jobs: `trip_reminder`, `trip_finished`, `rate_prompt`.
_Avoid_: notification_type, message_type (como nombre del campo)

## Flagged ambiguities

- **"cancelar"** puede referirse a `cancelled` (acción del Passenger) o a `revoked` (acción del Driver). En el código se mantienen distintos por actor; en la UI se puede mostrar "cancelado" para ambos pero el motivo especifica quién lo hizo.
- **"destination"** se usa como campo de búsqueda (`TripSearchInput.destination`) y como atributo del Trip (`destination_name`). No son sinónimos: el primero es texto de búsqueda libre; el segundo es el snapshot de la Locality.
