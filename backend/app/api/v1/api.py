"""Main API router."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, trips, users, bookings

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(trips.router, prefix="/trips", tags=["trips"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
