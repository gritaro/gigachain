"""Location resolution for people and device trackers.

The resolver answers "where is <person/device>" questions using the
configured Home Assistant zones. When the entity is outside every zone it
reports the distance to the home zone. Entities without GPS coordinates fall
back to their plain state ("home", "not_home" or a zone name).

Reverse geocoding is intentionally not implemented: Home Assistant core does
not provide it and no geocoding integration is installed.
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util.location import distance

LOGGER = logging.getLogger(__name__)

HOME_ENTITY_ID = "zone.home"

LOCATION_DOMAINS = ("person", "device_tracker")


def _get_coordinates(
    hass: HomeAssistant, entity_id: str
) -> tuple[float | None, float | None]:
    """Return the GPS coordinates of an entity, following a person's trackers."""
    state = hass.states.get(entity_id)
    if state is None:
        return None, None
    lat = state.attributes.get("latitude")
    lon = state.attributes.get("longitude")
    if lat is not None and lon is not None:
        return lat, lon
    if state.domain == "person":
        for tracker_id in state.attributes.get("device_trackers") or []:
            tracker_state = hass.states.get(tracker_id)
            if tracker_state is None:
                continue
            tlat = tracker_state.attributes.get("latitude")
            tlon = tracker_state.attributes.get("longitude")
            if tlat is not None and tlon is not None:
                return tlat, tlon
    return None, None


def _find_location_entity(hass: HomeAssistant, target: str | None) -> str | None:
    """Find a person or device_tracker entity by name, alias or entity_id."""
    if not target:
        return None
    needle = target.casefold().strip()
    if hass.states.get(needle) is not None:
        return needle

    registry = er.async_get(hass)
    exact: list[str] = []
    partial: list[str] = []
    for state in hass.states.async_all():
        if state.domain not in LOCATION_DOMAINS:
            continue
        names = {state.entity_id.casefold(), (state.name or "").casefold()}
        entry = registry.async_get(state.entity_id)
        if entry is not None:
            for value in (entry.name, entry.original_name):
                if value:
                    names.add(value.casefold())
            for alias in entry.aliases or []:
                if isinstance(alias, str):
                    names.add(alias.casefold())
        if needle in names:
            exact.append(state.entity_id)
        elif any(needle in name for name in names):
            partial.append(state.entity_id)
    if exact:
        return exact[0]
    if partial:
        return partial[0]
    return None


def _find_zone(
    hass: HomeAssistant, lat: float, lon: float
) -> tuple[str, str, float] | None:
    """Return (zone name, entity_id, distance_m) of the closest zone."""
    best: tuple[str, str, float] | None = None
    for state in hass.states.async_all("zone"):
        zone_lat = state.attributes.get("latitude")
        zone_lon = state.attributes.get("longitude")
        radius = state.attributes.get("radius", 100)
        if zone_lat is None or zone_lon is None:
            continue
        dist = distance(lat, lon, zone_lat, zone_lon)
        if dist <= radius and (best is None or dist < best[2]):
            best = (state.name, state.entity_id, dist)
    return best


def _distance_to_home(hass: HomeAssistant, lat: float, lon: float) -> float | None:
    home = hass.states.get(HOME_ENTITY_ID)
    if home is None:
        return None
    home_lat = home.attributes.get("latitude")
    home_lon = home.attributes.get("longitude")
    if home_lat is None or home_lon is None:
        return None
    return distance(lat, lon, home_lat, home_lon)


def _is_ru(language: str | None) -> bool:
    return (language or "").lower().startswith("ru")


async def async_resolve_location(
    hass: HomeAssistant, target: str | None, language: str | None = None
) -> dict[str, Any]:
    """Resolve the location of a person or device tracker."""
    entity_id = _find_location_entity(hass, target)
    if entity_id is None:
        return {"found": False, "error": "entity_not_found", "target": target}

    state = hass.states.get(entity_id)
    name = state.name if state is not None else entity_id
    result: dict[str, Any] = {
        "found": True,
        "entity_id": entity_id,
        "name": name,
        "state": state.state if state is not None else "unknown",
    }

    lat, lon = _get_coordinates(hass, entity_id)
    if lat is None or lon is None:
        result["location"] = result["state"]
        return result

    result["latitude"] = round(lat, 4)
    result["longitude"] = round(lon, 4)

    zone = _find_zone(hass, lat, lon)
    if zone is not None:
        zone_name, zone_entity_id, zone_distance = zone
        if zone_entity_id == HOME_ENTITY_ID:
            result["zone"] = "home"
            result["location"] = "дома" if _is_ru(language) else "at home"
        else:
            result["zone"] = zone_name
            result["location"] = zone_name
        result["distance_m"] = round(zone_distance)
        return result

    home_distance = _distance_to_home(hass, lat, lon)
    if home_distance is not None:
        result["distance_from_home_km"] = round(home_distance / 1000, 1)
    result["location"] = "вне дома" if _is_ru(language) else "not at home"
    return result


def format_location_text(result: dict[str, Any], language: str | None) -> str:
    """Render a resolver result as a plain sentence for the legacy path."""
    ru = _is_ru(language)
    if not result.get("found"):
        return (
            "Не удалось найти человека или устройство."
            if ru
            else "Could not find the person or device."
        )
    name = result.get("name", "")
    if result.get("zone") == "home":
        return f"{name}: дома" if ru else f"{name}: at home"
    location = result.get("location") or result.get("state") or "неизвестно"
    distance = result.get("distance_from_home_km")
    if ru:
        text = f"{name} находится: {location}"
        if distance is not None:
            text += f", примерно {distance} км от дома"
        return text
    text = f"{name} is at: {location}"
    if distance is not None:
        text += f", about {distance} km from home"
    return text
