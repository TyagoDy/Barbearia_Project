import logging
import os
import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routes import barbers, clients, appointments

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("barbearia")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="barber API")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start_time = time.time()
    try:
        response = await call_next(request)
        duration = (time.time() - start_time) * 1000
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "[%s] %s %s - status=%s duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )
        return response
    except Exception:
        duration = (time.time() - start_time) * 1000
        logger.exception(
            "[%s] %s %s - unhandled_error duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            duration,
        )
        raise

default_origins = "http://localhost:5173,http://127.0.0.1:5173"
cors_origins_env = os.getenv("CORS_ORIGINS", default_origins)
allowed_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

app.include_router(barbers.router)
app.include_router(clients.router)
app.include_router(appointments.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/health")
def health_check():
    return {"status": "ok"}