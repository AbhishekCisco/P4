from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr
from sqlalchemy import Column, Float, Integer, String

from database.connection import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True)
    department = Column(String(100), nullable=False)
    salary = Column(Float, nullable=False)


class EmployeeCreate(BaseModel):
    name: str
    email: EmailStr
    department: str
    salary: float


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    salary: Optional[float] = None


class EmployeeResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    department: str
    salary: float

    model_config = ConfigDict(from_attributes=True)