"""Unit tests for the location resolver (custom_components.gigachain.geo)."""

from __future__ import annotations

import asyncio

from conftest import FakeEntityEntry, FakeHass, FakeRegistry, FakeState


def _home_zone(home_params):
    return FakeState(
        "zone.home",
        "0",
        {
            "friendly_name": "Дом",
            "latitude": home_params["lat"],
            "longitude": home_params["lon"],
            "radius": home_params["radius"],
        },
    )


def test_format_location_text_home(geo_module):
    result = {"found": True, "name": "Телефон", "zone": "home", "location": "дома"}
    assert geo_module.format_location_text(result, "ru") == "Телефон: дома"
    assert geo_module.format_location_text(result, "en") == "Телефон: at home"


def test_format_location_text_not_found(geo_module):
    result = {"found": False, "error": "entity_not_found"}
    assert "Не удалось" in geo_module.format_location_text(result, "ru")
    assert "Could not" in geo_module.format_location_text(result, "en")


def test_format_location_text_with_distance(geo_module):
    result = {
        "found": True,
        "name": "Телефон",
        "location": "вне дома",
        "distance_from_home_km": 7.2,
    }
    text = geo_module.format_location_text(result, "ru")
    assert "вне дома" in text
    assert "7.2" in text


def test_find_zone_inside_home(geo_module, fake_hass, home_params):
    hass = fake_hass([_home_zone(home_params)])
    zone = geo_module._find_zone(hass, 54.9024, 83.0337)
    assert zone is not None
    assert zone[1] == "zone.home"
    assert zone[2] < home_params["radius"]


def test_find_zone_outside(geo_module, fake_hass, home_params):
    hass = fake_hass([_home_zone(home_params)])
    assert geo_module._find_zone(hass, 54.85, 83.10) is None


def test_resolve_in_zone(geo_module, fake_hass, home_params):
    hass = fake_hass([
        _home_zone(home_params),
        FakeState(
            "device_tracker.phone",
            "home",
            {"friendly_name": "Телефон", "latitude": 54.9024, "longitude": 83.0337},
        ),
    ])
    result = asyncio.run(geo_module.async_resolve_location(hass, "Телефон", "ru"))
    assert result["found"] is True
    assert result["zone"] == "home"
    assert result["location"] == "дома"


def test_resolve_far_reports_distance(
    geo_module, fake_hass, home_params, haversine
):
    hass = fake_hass([
        _home_zone(home_params),
        FakeState(
            "device_tracker.phone",
            "not_home",
            {"friendly_name": "Телефон", "latitude": 54.85, "longitude": 83.10},
        ),
    ])
    result = asyncio.run(geo_module.async_resolve_location(hass, "Телефон", "ru"))
    assert result["found"] is True
    assert "zone" not in result
    expected_km = round(
        haversine(54.85, 83.10, home_params["lat"], home_params["lon"]) / 1000, 1
    )
    assert result["distance_from_home_km"] == expected_km
    assert result["location"] == "вне дома"


def test_resolve_no_coords_uses_state(geo_module, fake_hass, home_params):
    hass = fake_hass([
        _home_zone(home_params),
        FakeState("device_tracker.phone", "home", {"friendly_name": "Телефон"}),
    ])
    result = asyncio.run(geo_module.async_resolve_location(hass, "Телефон", "ru"))
    assert result["found"] is True
    assert result["location"] == "home"
    assert "latitude" not in result


def test_resolve_person_follows_tracker(geo_module, fake_hass, home_params):
    hass = fake_hass([
        _home_zone(home_params),
        FakeState(
            "person.roman",
            "not_home",
            {"friendly_name": "Роман", "device_trackers": ["device_tracker.phone"]},
        ),
        FakeState(
            "device_tracker.phone",
            "not_home",
            {"friendly_name": "Телефон", "latitude": 54.85, "longitude": 83.10},
        ),
    ])
    result = asyncio.run(geo_module.async_resolve_location(hass, "Роман", "ru"))
    assert result["found"] is True
    assert result["entity_id"] == "person.roman"
    assert result["location"] == "вне дома"


def test_resolve_unknown_target(geo_module, fake_hass, home_params):
    hass = fake_hass([_home_zone(home_params)])
    result = asyncio.run(geo_module.async_resolve_location(hass, "Космос", "ru"))
    assert result["found"] is False
    assert result["error"] == "entity_not_found"


def test_find_location_entity_by_name_and_alias(geo_module):
    registry = FakeRegistry({
        "device_tracker.phone": FakeEntityEntry(name="Телефон"),
        "person.roman": FakeEntityEntry(name="gritaro", aliases=["Роман"]),
    })
    hass = FakeHass([
        FakeState("device_tracker.phone", "home"),
        FakeState("person.roman", "home", {"friendly_name": "gritaro"}),
    ], registry)
    assert geo_module._find_location_entity(hass, "телефон") == "device_tracker.phone"
    assert geo_module._find_location_entity(hass, "Роман") == "person.roman"
    assert geo_module._find_location_entity(hass, "device_tracker.phone") == (
        "device_tracker.phone"
    )
    assert geo_module._find_location_entity(hass, "нет-такого") is None
