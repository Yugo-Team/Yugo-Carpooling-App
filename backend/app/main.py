from dotenv import load_dotenv
load_dotenv()  # must run before any app module reads os.environ at import time

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.limiter import limiter
from app.routes import auth, users, rides, messages
from app.routes.map import router as map_router
from app.db.mongo import connect_to_mongo, close_mongo_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

tags_metadata = [
    {
        "name": "Auth",
        "description": "Login, logout, profile retrieval, and driver license upload.",
    },
{
        "name": "Users",
        "description": "View and manage user profiles, follows, and ratings.",
    },
    {
        "name": "Posts",
        "description": "Create and browse ride offers (drivers) and ride requests (passengers).",
    },
    {
        "name": "Messages",
        "description": "Group chat rooms created when a passenger matches with a driver.",
    },
]

app = FastAPI(
    title="Yugo API",
    description="College-only rideshare platform. Students post ride offers and requests matched by school email.",
    version="0.1.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    # Native apps (React Native / Expo) send no Origin header, so CORS does not
    # apply to them. These origins only matter for browser-based clients: the
    # web app and Expo web during development.
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8081",  # Expo web / Metro dev server
        "https://athletic-vision-production-2749.up.railway.app",
    ],
    # Auth is header-based (Bearer token), not cookie-based, so credentialed
    # CORS is unnecessary. Keeping this False also allows wildcard origins later.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,   prefix="/api/v1/auth",  tags=["Auth"])
app.include_router(users.router,  prefix="/api/v1/users", tags=["Users"])
app.include_router(rides.router,  prefix="/api/v1/posts", tags=["Posts"])
app.include_router(map_router,          prefix="/api/v1/map",      tags=["Map"])
app.include_router(messages.router,     prefix="/api/v1/messages",  tags=["Messages"])


@app.get("/", tags=["Health"])
def root():
    return {"message": "status ok!"}
