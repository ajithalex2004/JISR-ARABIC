"""Single composition point for the existing public API."""
from fastapi import APIRouter

from backend.routes import (
    auth, curriculum, payments, attempts, tutor, parent,
    admin, audio, ai, learning_modules, mastery, gamification,
    feedback, tasks,
)

router = APIRouter()
for adapter in (
    auth, curriculum, payments, attempts, tutor, parent,
    admin, audio, ai, learning_modules, mastery, gamification,
    feedback, tasks,
):
    router.include_router(adapter.router)
