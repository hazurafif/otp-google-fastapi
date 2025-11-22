from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, String

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    google_id = Column(String, unique=True)
    otp = Column(String)
    otp_expires = Column(DateTime)


class VerifyOTPRequest(BaseModel):
    email: str
    otp: str
