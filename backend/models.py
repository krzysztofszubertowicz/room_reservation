from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Time, Text, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

room_equipment = Table(
    "sala_wyposazenie", Base.metadata,
    Column("id_sali", Integer, ForeignKey("sala.id_sali"), primary_key=True),
    Column("id_wyposazenia", Integer, ForeignKey("wyposazenie.id_wyposazenia"), primary_key=True)
)

class User(Base):
    __tablename__ = "uzytkownik"
    id = Column("id_uzytkownika", Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column("imie", String(255))
    last_name = Column("nazwisko", String(255))
    email = Column(String(255), unique=True, index=True)
    password = Column("haslo", String(255))
    role = Column("rola", String(255))
    notifications = relationship("Notification", back_populates="user")
    reservations = relationship("Reservation", back_populates="user")
    classes = relationship("Class", back_populates="instructor")

class Notification(Base):
    __tablename__ = "powiadomienie"
    id = Column("id_powiadomienia", Integer, primary_key=True, index=True)
    user_id = Column("id_uzytkownika", Integer, ForeignKey("uzytkownik.id_uzytkownika"))
    content = Column("tresc", Text)
    sent_at = Column("data_wyslania", DateTime)
    read = Column("przeczytane", Boolean, default=False)
    user = relationship("User", back_populates="notifications")

class RoomType(Base):
    __tablename__ = "typ_sali"
    id = Column("id_typu", Integer, primary_key=True, index=True)
    name = Column("nazwa", String(255))
    description = Column("opis", Text)
    rooms = relationship("Room", back_populates="room_type")

class Room(Base):
    __tablename__ = "sala"
    id = Column("id_sali", Integer, primary_key=True, index=True)
    name = Column("nazwa", String)
    building = Column("budynek", String)
    floor = Column("pietro", Integer)
    seat_count = Column("liczba_miejsc", Integer)
    description = Column("opis", String)
    type_id = Column("id_typu", Integer, ForeignKey("typ_sali.id_typu"))
    # ...

    room_type = relationship("RoomType", back_populates="rooms")
    equipment = relationship("Equipment", secondary=room_equipment, back_populates="rooms")
    reservations = relationship("Reservation", back_populates="room")
    malfunctions = relationship("Malfunction", back_populates="room")
    class_assignments = relationship("ClassAssignment", back_populates="room")

class Equipment(Base):
    __tablename__ = "wyposazenie"
    id = Column("id_wyposazenia", Integer, primary_key=True, index=True)
    name = Column("nazwa", String(255))
    description = Column("opis", Text)
    rooms = relationship("Room", secondary=room_equipment, back_populates="equipment")

class Reservation(Base):
    __tablename__ = "rezerwacja"
    id = Column("id_rezerwacji", Integer, primary_key=True, index=True)
    room_id = Column("id_sali", Integer, ForeignKey("sala.id_sali"))
    user_id = Column("id_uzytkownika", Integer, ForeignKey("uzytkownik.id_uzytkownika"))
    date = Column("data", Date)
    time_from = Column("godzina_od", Time)
    time_to = Column("godzina_do", Time)
    purpose = Column("cel", Text)
    notification = Column("powiadomienie", Boolean, default=False)
    room = relationship("Room", back_populates="reservations")
    user = relationship("User", back_populates="reservations")

class Malfunction(Base):
    __tablename__ = "awaria"
    id = Column("id_awarii", Integer, primary_key=True, index=True)
    room_id = Column("id_sali", Integer, ForeignKey("sala.id_sali"))
    description = Column("opis", Text)
    reported_date = Column("data_zgloszenia", Date)
    status = Column(String(255))
    room = relationship("Room", back_populates="malfunctions")

class Class(Base):
    __tablename__ = "zajecia"
    id = Column("id_zajec", Integer, primary_key=True, index=True)
    name = Column("nazwa", String(255))
    instructor_id = Column("id_prowadzacego", Integer, ForeignKey("uzytkownik.id_uzytkownika"))
    student_count = Column("liczba_studentow", Integer)
    instructor = relationship("User")
    assignments = relationship("ClassAssignment", back_populates="class_")

class ClassAssignment(Base):
    __tablename__ = "przypisanie_zajec"
    id = Column("id_przypisania", Integer, primary_key=True, index=True)
    class_id = Column("id_zajec", Integer, ForeignKey("zajecia.id_zajec"))
    room_id = Column("id_sali", Integer, ForeignKey("sala.id_sali"))
    weekday = Column("dzien_tygodnia", String(255))
    time_from = Column("godzina_od", Time)
    time_to = Column("godzina_do", Time)
    class_ = relationship("Class", back_populates="assignments")
    room = relationship("Room", back_populates="class_assignments")
    