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