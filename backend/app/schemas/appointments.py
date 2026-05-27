from pydantic import BaseModel, ConfigDict
from datetime import datetime

class AppointmentBase(BaseModel):
    date: datetime
    barber_id: int
    client_id: int
    payment_method: str

class AppointmentCreate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
