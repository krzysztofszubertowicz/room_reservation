from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import RoomCreate, RoomUpdate,RoomResponse
from database import get_db
from dependencies import get_current_user
from models import Room, User, Equipment
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Room, Equipment, RoomType
from sqlalchemy import inspect


router = APIRouter(
    tags=["rooms"]
)

#FILTROWANIE SALI

@router.get("/rooms/filter", response_model=List[RoomResponse])
def filter_rooms(
    building: Optional[str] = None,
    room_type: Optional[str] = None,
    equipment: Optional[List[str]] = Query(None),
    min_seat_count: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Room)

    if building:
        query = query.filter(Room.building == building)

    if min_seat_count:
        query = query.filter(Room.seat_count >= min_seat_count)

    if room_type:
        query = query.join(Room.room_type).filter(RoomType.name == room_type)

    if equipment:
        for equip in equipment:
            query = query.filter(Room.equipment.any(Equipment.name == equip))

    rooms = query.all()

    return rooms

# CREATE NEW ROOM
@router.post("/rooms")
async def create_room(room: RoomCreate, db: Session = Depends(get_db)):
    equipment_objs = db.query(Equipment).filter(Equipment.id.in_(room.wyposazenie or [])).all()
    db_room = Room(
        name=room.nazwa,
        building=room.budynek,
        floor=room.pietro,
        seat_count=room.liczba_miejsc,
        description=room.opis,
        type_id=room.id_typu,
    )
    db_room.equipment = equipment_objs

    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

# GET ALL ROOMS
@router.get("/rooms", response_model=list[RoomResponse])
def get_rooms(db: Session = Depends(get_db)):
    return db.query(Room).all()

# GET SINGLE ROOM BY ID
@router.get("/rooms/{room_id}", response_model=RoomResponse)
def get_room(room_id: int, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

# UPDATE ROOM BY ID
@router.put("/rooms/{room_id}", response_model=RoomResponse)
def update_room(
    room_id: int,
    room: RoomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["opiekun", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    db_room = db.query(Room).filter(Room.id == room_id).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")

    try:
        # Update basic fields
        db_room.name = room.name
        db_room.building = room.building
        db_room.floor = room.floor
        db_room.seat_count = room.seat_count
        db_room.description = room.description

        # Update type if provided
        if room.type_id is not None:
            db_room.type_id = room.type_id

        # Update equipment relationship if provided
        if room.equipment is not None:
            equipment_objs = db.query(Equipment).filter(Equipment.id.in_(room.equipment)).all()
            
            # Validate all equipment IDs exist
            if len(equipment_objs) != len(room.equipment):
                raise HTTPException(status_code=400, detail="Some equipment IDs not found")
            
            db_room.equipment = equipment_objs

        state = inspect(db_room)
        print("Is modified?", state.modified)
        print("Dirty attributes:", state.attrs.items())
        db.flush()  # try flushing before commit
        # ✅ Commit the transaction
        db.commit()

        # ✅ Refresh to get updated data
        db.refresh(db_room)
        
        print(f"Updated room {room_id} with: {room}")
        return db_room

    except Exception as e:
        # ✅ Rollback on error
        print(f"Error updating room {room_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update room: {str(e)}")
