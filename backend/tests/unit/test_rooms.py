from models import Room


def test_add_new_room(client, db_session, seeded_entities):
    payload = {
        "name": "A-102",
        "building": "A",
        "floor": 1,
        "seat_count": 45,
        "description": "Room created by the test suite",
        "equipment": [seeded_entities["projector"].id, seeded_entities["whiteboard"].id],
        "type_id": seeded_entities["lecture_type"].id,
    }

    response = client.post("/rooms", json=payload)

    assert response.status_code == 200
    created_room = response.json()
    assert created_room["name"] == payload["name"]
    assert created_room["seat_count"] == payload["seat_count"]

    saved_room = db_session.query(Room).filter(Room.id == created_room["id"]).first()
    assert saved_room is not None
    assert saved_room.building == payload["building"]
    assert saved_room.floor == payload["floor"]


def test_edit_room_data(client, db_session, seeded_entities, auth_as_admin):
    room_id = seeded_entities["room_a"].id
    payload = {
        "name": "A-101-UPDATED",
        "building": "A",
        "floor": 2,
        "seat_count": 36,
        "description": "Updated from test",
        "equipment": [seeded_entities["whiteboard"].id],
        "type_id": seeded_entities["lecture_type"].id,
    }

    response = client.put(f"/rooms/{room_id}", json=payload)

    assert response.status_code == 200
    updated_room = response.json()
    assert updated_room["name"] == payload["name"]
    assert updated_room["floor"] == payload["floor"]
    assert updated_room["seat_count"] == payload["seat_count"]

    updated_room = db_session.query(Room).filter(Room.id == room_id).first()
    assert updated_room is not None
    assert updated_room.name == payload["name"]
    assert updated_room.floor == payload["floor"]
    assert updated_room.seat_count == payload["seat_count"]
