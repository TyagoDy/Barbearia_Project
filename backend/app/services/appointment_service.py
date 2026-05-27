from sqlalchemy.orm import Session
from app import models
from app.schemas.appointments import AppointmentCreate

def create_appointment(db: Session, appointment: AppointmentCreate):
    # Verificar se o barbeiro existe
    barber = db.query(models.Barber).filter(models.Barber.id == appointment.barber_id).first()
    if not barber:
        raise ValueError("Barber not found")

    # Verificar se o cliente existe
    client = db.query(models.Client).filter(models.Client.id == appointment.client_id).first()
    if not client:
        raise ValueError("Client not found")

    # Verificar conflito de horário
    conflict = db.query(models.Appointment).filter(
        models.Appointment.barber_id == appointment.barber_id,
        models.Appointment.date == appointment.date
    ).first()
    if conflict:
        raise ValueError("Barber is already booked at this time")

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