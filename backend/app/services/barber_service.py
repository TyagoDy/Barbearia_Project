from sqlalchemy.orm import Session
from app import models
from app.schemas.barber import BarberCreate

def create_barber(db: Session, barber: BarberCreate):
    db_barber = models.Barber(name=barber.name, specialty=barber.specialty)
    db.add(db_barber)
    db.commit()
    db.refresh(db_barber)
    return db_barber