from pydantic import BaseModel, EmailStr, Field
from datetime import date, time
from typing import Optional, List

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    role: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None

class EquipmentSchema(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        orm_mode = True

class TypeSchema(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        orm_mode = True

class RoomCreate(BaseModel):
    name: str
    seat_count: int
    description: Optional[str] = None
    building: str
    floor: Optional[str] = None
    equipment: Optional[List[int]] = Field(default=None, alias="equipment")
    type_id: Optional[int] = Field(default=None, alias="type_id")

class RoomUpdate(BaseModel):
    name: Optional[str] = None
    seat_count: Optional[int] = None
    description: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[str] = None
    equipment: Optional[List[int]] = Field(default=None, alias="equipment")
    type_id: Optional[int] = Field(default=None, alias="type_id")

class RoomResponse(BaseModel):
    id: int
    name: str
    building: str
    floor: Optional[str]
    seat_count: int
    equipment: List[EquipmentSchema] = Field(default_factory=list, alias="equipment")
    type_id: Optional[int] = Field(default=None, alias="type_id")
    type: Optional[TypeSchema] = Field(None, alias="room_type")
    status: Optional[str] = None

    class Config:
        orm_mode = True

class ReservationCreate(BaseModel):
    room_id: int
    user_id: int
    date: date
    time_from: time
    time_to: time
    purpose: str
    notification: Optional[bool] = False

class ReservationResponse(ReservationCreate):
    id: int
    notification: bool

    class Config:
        orm_mode = True

class RoomDetailResponse(BaseModel):
    id: int
    name: str
    seat_count: int
    building: str
    floor: int
    description: Optional[str]
    equipment: List[EquipmentSchema]

    class Config:
        orm_mode = True

class ScheduleEntry(BaseModel):
    cel: str
    prowadzacy: EmailStr
    sala: str
    budynek: str
    data: date
    godzina_od: time
    godzina_do: time
    liczba_studentow: int