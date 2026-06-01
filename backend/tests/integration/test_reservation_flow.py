def test_create_reservation_is_persisted_and_listed(client, seeded_entities):
    payload = {
        "room_id": seeded_entities["room_a"].id,
        "user_id": seeded_entities["regular_user"].id,
        "date": seeded_entities["future_date"].isoformat(),
        "time_from": "10:00",
        "time_to": "11:30",
        "purpose": "Integration test reservation",
    }

    response = client.post("/reservations", json=payload)
    assert response.status_code == 200

    reservation_id = response.json()["id"]
    reservations = client.get("/reservations")

    assert reservations.status_code == 200
    assert any(item["id"] == reservation_id for item in reservations.json())


def test_cancel_reservation_releases_time_slot(client, seeded_entities, auth_as_regular_user):
    payload = {
        "room_id": seeded_entities["room_a"].id,
        "user_id": seeded_entities["regular_user"].id,
        "date": seeded_entities["future_date"].isoformat(),
        "time_from": "13:30",
        "time_to": "15:00",
        "purpose": "Reservation to cancel",
    }

    created = client.post("/reservations", json=payload)
    assert created.status_code == 200

    reservation_id = created.json()["id"]
    cancelled = client.delete(f"/reservations/{reservation_id}")
    assert cancelled.status_code == 200

    recreated = client.post("/reservations", json=payload)
    assert recreated.status_code == 200
