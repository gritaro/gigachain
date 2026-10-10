"""Test helpers: load geo.py with lightweight Home Assistant stubs.

The integration modules import Home Assistant at import time. To keep these
unit tests dependency-free they inject minimal ``homeassistant`` stubs into
``sys.modules`` and load ``geo.py`` directly from disk, bypassing the package
``__init__`` (which pulls the LLM client libraries).
"""

from __future__ import annotations

import importlib.util
import math
import sys
import types
from pathlib import Path

import pytest

GEO_PATH = (
    Path(__file__).resolve().parent.parent
    / "custom_components"
    / "gigachain"
    / "geo.py"
)


def _distance(lat1, lon1, lat2, lon2):
    """Return the distance in meters between two coordinates (haversine)."""
    radius = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return 2 * radius * math.asin(math.sqrt(a))


def _install_stubs() -> None:
    ha = types.ModuleType("homeassistant")
    core = types.ModuleType("homeassistant.core")

    class HomeAssistant:  # noqa: D401
        """Stub HomeAssistant."""

    core.HomeAssistant = HomeAssistant

    helpers = types.ModuleType("homeassistant.helpers")
    entity_registry = types.ModuleType("homeassistant.helpers.entity_registry")
    entity_registry.async_get = lambda hass: hass.entity_registry

    util = types.ModuleType("homeassistant.util")
    location = types.ModuleType("homeassistant.util.location")
    location.distance = _distance

    helpers.entity_registry = entity_registry
    util.location = location
    ha.core = core
    ha.helpers = helpers
    ha.util = util

    sys.modules.setdefault("homeassistant", ha)
    sys.modules.setdefault("homeassistant.core", core)
    sys.modules.setdefault("homeassistant.helpers", helpers)
    sys.modules.setdefault("homeassistant.helpers.entity_registry", entity_registry)
    sys.modules.setdefault("homeassistant.util", util)
    sys.modules.setdefault("homeassistant.util.location", location)


class FakeState:
    """Minimal state object."""

    def __init__(self, entity_id: str, state: str, attributes: dict | None = None):
        self.entity_id = entity_id
        self.state = state
        self.attributes = attributes or {}

    @property
    def name(self) -> str:
        return self.attributes.get("friendly_name", self.entity_id.split(".", 1)[1])

    @property
    def domain(self) -> str:
        return self.entity_id.split(".", 1)[0]


class FakeStates:
    """Minimal state machine."""

    def __init__(self, states: list[FakeState]):
        self._states = {state.entity_id: state for state in states}

    def get(self, entity_id: str) -> FakeState | None:
        return self._states.get(entity_id)

    def async_all(self, domain: str | None = None) -> list[FakeState]:
        states = list(self._states.values())
        if domain is not None:
            states = [state for state in states if state.domain == domain]
        return states


class FakeEntityEntry:
    """Minimal entity registry entry."""

    def __init__(self, name=None, original_name=None, aliases=None):
        self.name = name
        self.original_name = original_name
        self.aliases = aliases or []


class FakeRegistry:
    """Minimal entity registry."""

    def __init__(self, entries: dict[str, FakeEntityEntry] | None = None):
        self._entries = entries or {}

    def async_get(self, entity_id: str) -> FakeEntityEntry | None:
        return self._entries.get(entity_id)


class FakeHass:
    """Minimal HomeAssistant."""

    def __init__(
        self,
        states: list[FakeState],
        registry: FakeRegistry | None = None,
    ):
        self.states = FakeStates(states)
        self.entity_registry = registry or FakeRegistry()


def _load_geo():
    spec = importlib.util.spec_from_file_location("gigachain_geo", GEO_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_install_stubs()
geo = _load_geo()


@pytest.fixture
def geo_module():
    """Return the loaded geo module."""
    return geo


@pytest.fixture
def fake_hass():
    """Return a factory building a FakeHass."""

    def _factory(states, registry=None):
        return FakeHass(states, registry)

    return _factory


@pytest.fixture
def home_params():
    """Home zone coordinates used across tests."""
    return {"lat": 54.9022, "lon": 83.0335, "radius": 100}


@pytest.fixture
def haversine():
    """Expose the haversine helper to tests."""
    return _distance
