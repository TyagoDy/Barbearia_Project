from sqlalchemy.orm import Session
from app import models
from app.schemas.client import ClientCreate

def create_client(db: Session, client: ClientCreate):
    db_client = models.Client(name=client.name, phone=client.phone)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client