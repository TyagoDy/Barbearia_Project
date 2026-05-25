from fastapi import FastAPI
from app.database import Base, engine
from app import routes
from app.routes import barbers, clients, appointments
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)

app = FastAPI(title="barber API")

app.include_router(barbers.router)
app.include_router(clients.router)
app.include_router(appointments.router)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}