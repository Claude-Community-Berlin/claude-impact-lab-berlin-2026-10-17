"""App wiring. SHARED FILE: every router is already registered here, so feature branches
should not need to edit it."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import init_db
from app.errors import register_error_handlers
from app.routers import (
    ask, draft, feedback, kitas, meta, staff_announcements, staff_auth, staff_documents,
    staff_insights, week,
)
from app.services import announcements
from app.services.documents import documents_block

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

API_PREFIX = "/api/v1"

ROUTERS = (
    meta.router, kitas.router, ask.router, feedback.router, draft.router, week.router,
    staff_auth.router, staff_announcements.router, staff_documents.router, staff_insights.router,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    documents_block()  # fail fast if the document pack is missing
    init_db()
    announcements.seed_if_empty()
    task = asyncio.create_task(week.prewarm())
    yield
    task.cancel()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Kita Companion API",
        version="1.0.0",
        description="Backend for Kita Companion. Answers come only from the Kita's own documents.",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    register_error_handlers(app)
    for r in ROUTERS:
        app.include_router(r, prefix=API_PREFIX)
    return app


app = create_app()
