from fastapi import FastAPI
from app.database import Base, engine
from app import routes
from app.routes import barbers, clients, appointments

Base.metadata.create_all(bind=engine)

app = FastAPI(title="barber API")

app.include_router(barbers.router)
app.include_router(clients.router)
app.include_router(appointments.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}