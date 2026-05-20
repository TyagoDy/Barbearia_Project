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