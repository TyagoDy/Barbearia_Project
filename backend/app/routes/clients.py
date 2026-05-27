from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.client import ClientCreate
from app import models
from app.services import client_service

router = APIRouter()

@router.get("/clients")
def get_clients(db: Session = Depends(get_db)):
    return db.query(models.Client).all()

@router.post("/clients")
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    return client_service.create_client(db, client)

