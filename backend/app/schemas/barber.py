from pydantic import BaseModel
from pydantic import ConfigDict

class BarberBase(BaseModel):
    name: str
    specialty: str

class BarberCreate(BarberBase):
    pass

class Barber(BarberBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

