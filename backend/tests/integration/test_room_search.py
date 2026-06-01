from models import Room


def test_room_search_returns_matching_rooms_from_database(client, db_session, seeded_entities):
    room_b = Room(
        name="B-201",
        building="B",
        floor=2,
        seat_count=40,
        description="Different building",
        type_id=seeded_entities["lecture_type"].id,
    )
    room_b.equipment = [seeded_entities["projector"]]

    room_small = Room(
        name="A-103",
        building="A",
        floor=1,
        seat_count=10,
        description="Too small",
        type_id=seeded_entities["lecture_type"].id,
    )
    room_small.equipment = [seeded_entities["projector"]]

    db_session.add_all([room_b, room_small])
    db_session.commit()

    response = client.get(
        "/rooms/filter",
        params={
            "building": "A",
            "room_type": "Lecture",
            "equipment": ["Projector"],
            "min_seat_count": 20,
        },
    )

    assert response.status_code == 200
    rooms = response.json()

    assert len(rooms) == 1
    assert rooms[0]["name"] == seeded_entities["room_a"].name
    assert rooms[0]["building"] == seeded_entities["room_a"].building
