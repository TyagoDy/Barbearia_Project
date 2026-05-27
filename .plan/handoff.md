# Barbearia Project — Handoff Document

## How to use this document
You are continuing a project with a student who is learning Python + FastAPI + React from scratch. Your job is to:
- Tell them what needs to be built next
- Build the code for them
- Explain every line of what you built and why
- Never say "try it yourself" or "give it a shot" — you build it, you explain it
- Teach concepts before showing code when a new concept appears
- Ask one question at a time max when you need to check understanding

---

## The Project
A **Barber Shop Appointment Manager** built with:
- **Backend:** Python + FastAPI + SQLAlchemy
- **Database:** PostgreSQL (running in Docker)
- **Frontend:** React + Vite
- **Containers:** Docker + docker-compose

---

## What has been built — Backend (COMPLETE)

### File structure
```
Barbearia_Project/
├── .env
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── app/
│       ├── __init__.py
│       ├── database.py
│       ├── models.py
│       ├── main.py
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── barbers.py
│       │   ├── clients.py
│       │   └── appointments.py
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── barber.py
│       │   ├── client.py
│       │   └── appointments.py
│       └── services/
│           ├── __init__.py
│           ├── barber_service.py
│           ├── client_service.py
│           └── appointment_service.py
└── frontend/
    └── (React app — IN PROGRESS)
```

---

### `database.py`
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass
```

### `models.py`
```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from app.database import Base
from datetime import datetime

class Barber(Base):
    __tablename__ = "barbers"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    specialty: Mapped[str] = mapped_column()

class Client(Base):
    __tablename__ = "clients"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    phone: Mapped[str] = mapped_column()

class Appointment(Base):
    __tablename__ = "appointments"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    barber_id: Mapped[int] = mapped_column(ForeignKey("barbers.id"))
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    date: Mapped[datetime] = mapped_column()
    payment_method: Mapped[str] = mapped_column()
```

### `main.py`
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app import models
from app.routes import barbers, clients, appointments

Base.metadata.create_all(bind=engine)

app = FastAPI(title="barber API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(barbers.router)
app.include_router(clients.router)
app.include_router(appointments.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}
```

### `routes/barbers.py`
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.barber import BarberCreate
from app import models
from app.services import barber_service

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/barbers")
def get_barbers(db: Session = Depends(get_db)):
    return db.query(models.Barber).all()

@router.post("/barbers")
def create_barber(barber: BarberCreate, db: Session = Depends(get_db)):
    return barber_service.create_barber(db, barber)
```

### `routes/clients.py`
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.client import ClientCreate
from app import models
from app.services import client_service

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/clients")
def get_clients(db: Session = Depends(get_db)):
    return db.query(models.Client).all()

@router.post("/clients")
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    return client_service.create_client(db, client)
```

### `routes/appointments.py`
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.appointments import AppointmentCreate
from app import models
from app.services import appointment_service

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/appointments")
def get_appointments(db: Session = Depends(get_db)):
    return db.query(models.Appointment).all()

@router.post("/appointments")
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    return appointment_service.create_appointment(db, appointment)

@router.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if appointment:
        db.delete(appointment)
        db.commit()
        return {"message": "Appointment deleted"}
    return {"message": "Appointment not found"}
```

### `schemas/barber.py`
```python
from pydantic import BaseModel, ConfigDict

class BarberBase(BaseModel):
    name: str
    specialty: str

class BarberCreate(BarberBase):
    pass

class Barber(BarberBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
```

### `schemas/client.py`
```python
from pydantic import BaseModel, ConfigDict

class ClientBase(BaseModel):
    name: str
    phone: str

class ClientCreate(ClientBase):
    pass

class Client(ClientBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
```

### `schemas/appointments.py`
```python
from pydantic import BaseModel, ConfigDict

class AppointmentBase(BaseModel):
    date: str
    barber_id: int
    client_id: int
    payment_method: str

class AppointmentCreate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
```

### `services/barber_service.py`
```python
from sqlalchemy.orm import Session
from app import models
from app.schemas.barber import BarberCreate

def create_barber(db: Session, barber: BarberCreate):
    db_barber = models.Barber(name=barber.name, specialty=barber.specialty)
    db.add(db_barber)
    db.commit()
    db.refresh(db_barber)
    return db_barber
```

### `services/client_service.py`
```python
from sqlalchemy.orm import Session
from app import models
from app.schemas.client import ClientCreate

def create_client(db: Session, client: ClientCreate):
    db_client = models.Client(name=client.name, phone=client.phone)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client
```

### `services/appointment_service.py`
```python
from sqlalchemy.orm import Session
from app import models
from app.schemas.appointments import AppointmentCreate

def create_appointment(db: Session, appointment: AppointmentCreate):
    db_appointment = models.Appointment(
        date=appointment.date,
        barber_id=appointment.barber_id,
        client_id=appointment.client_id,
        payment_method=appointment.payment_method
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment
```

---

## What the student knows — React concepts

The student just learned these 4 concepts for the first time:

**Components** — JavaScript functions that return JSX (HTML-like code).

**useState** — how React stores data that can change. Pattern: `const [value, setValue] = useState(initialValue)`

**useEffect** — runs code when the component loads. Used to fetch data from the API. Pattern: `useEffect(() => { fetch(...) }, [])`

**fetch** — how React calls the API. GET and POST both covered.

**props** — how parent components pass data to child components.

---

## What is next — Days 8-9 Frontend

The student needs to build the React frontend. Start here:

### Step 1 — `src/App.jsx`
Build a component that fetches `GET /barbers` and displays the list. Here is what to build and explain:

```jsx
import { useState, useEffect } from "react"

function App() {
  const [barbers, setBarbers] = useState([])

  useEffect(() => {
    fetch("http://localhost:8000/barbers")
      .then(response => response.json())
      .then(data => setBarbers(data))
  }, [])

  return (
    <div>
      <h1>Barbearia</h1>
      <ul>
        {barbers.map(barber => (
          <li key={barber.id}>{barber.name} — {barber.specialty}</li>
        ))}
      </ul>
    </div>
  )
}

export default App
```

### Step 2 — Booking form
A form with inputs for barber, client, date, payment method that calls `POST /appointments`.

### Step 3 — Cancel appointment
A button next to each appointment that calls `DELETE /appointments/{id}`.

---

## Roadmap status
- ✅ Days 1-3 — Project structure, Docker, database connection
- ✅ Days 3-7 — Routes, schemas, services — full backend working
- 🔲 Days 8-9 — React frontend (IN PROGRESS — student just learned the 4 core concepts)
- ⏳ Days 10-11 — pytest tests
- ⏳ Day 12 — Logging
- ⏳ Day 13 — End-to-end debug
- ⏳ Day 14 — Deploy to Render + Vercel + Neon

---

## Important notes about this student
- Complete beginner — explain everything from scratch when a new concept appears
- Learns by doing but needs the code shown first with explanation, not "try it yourself"
- Gets frustrated when told to do something without being taught the syntax first
- Responds well to analogies and real-world comparisons
- One concept at a time — never dump multiple new things at once
- Keep answers focused and direct — no unnecessary padding
