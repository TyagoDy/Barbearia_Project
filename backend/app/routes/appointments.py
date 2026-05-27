from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.appointments import AppointmentCreate
from app import models
from app.services import appointment_service

router = APIRouter()

@router.get("/appointments")
def get_appointments(db: Session = Depends(get_db)):
    return db.query(models.Appointment).all()

@router.post("/appointments")
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    try:
        return appointment_service.create_appointment(db, appointment)
    except ValueError as e:
        err_msg = str(e)
        if "not found" in err_msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err_msg)
        if "already booked" in err_msg:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)

@router.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if appointment:
        db.delete(appointment)
        db.commit()
        return {"message": "Appointment deleted"}
    return {"message": "Appointment not found"}