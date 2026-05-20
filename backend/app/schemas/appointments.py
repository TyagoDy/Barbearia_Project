from pydantic import BaseModel
from pydantic import ConfigDict

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
