from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import os

User_db = os.getenv("DATABASE_URL")

engine = create_engine(User_db)

SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass
