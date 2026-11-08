"""Unit tests for the GigaChat tool-schema sanitizer in ``llm_tools.py``.

The integration modules import Home Assistant and the LLM client libraries at
import time. These tests inject lightweight stubs (like ``conftest`` does for
``geo.py``) and load ``llm_tools.py`` directly from disk.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import pytest

LLM_TOOLS_PATH = (
    Path(__file__).resolve().parent.parent
    / "custom_components"
    / "gigachain"
    / "llm_tools.py"
)


def _install_extra_stubs() -> None:
    class _KwargsStub:
        """Minimal stand-in accepting and storing keyword arguments."""

        def __init__(self, *args, **kwargs) -> None:
            self.__dict__.update(kwargs)

    def _stub(name: str) -> type:
        return type(name, (_KwargsStub,), {})

    ha = sys.modules.get("homeassistant") or types.ModuleType("homeassistant")

    components = sys.modules.get("homeassistant.components") or types.ModuleType(
        "homeassistant.components"
    )
    conversation = types.ModuleType("homeassistant.components.conversation")
    for name in (
        "Content",
        "SystemContent",
        "UserContent",
        "AssistantContent",
        "ToolResultContent",
    ):
        setattr(conversation, name, _stub(name))
    components.conversation = conversation
    ha.components = components

    helpers = sys.modules.get("homeassistant.helpers") or types.ModuleType(
        "homeassistant.helpers"
    )
    llm = types.ModuleType("homeassistant.helpers.llm")
    llm.APIInstance = _stub("APIInstance")
    llm.ToolInput = _stub("ToolInput")
    llm.ToolResult = _stub("ToolResult")
    helpers.llm = llm
    selector_mod = types.ModuleType("homeassistant.helpers.selector")
    selector_mod.SelectOptionDict = _stub("SelectOptionDict")
    helpers.selector = selector_mod
    ha.helpers = helpers

    probatio = types.ModuleType("probatio")
    probatio.to_openapi = lambda *args, **kwargs: {}  # type: ignore[attr-defined]

    langchain_core = types.ModuleType("langchain_core")
    messages = types.ModuleType("langchain_core.messages")
    for name in (
        "AIMessage",
        "BaseMessage",
        "HumanMessage",
        "SystemMessage",
        "ToolMessage",
    ):
        setattr(messages, name, _stub(name))
    langchain_core.messages = messages

    sys.modules.update(
        {
            "homeassistant": ha,
            "homeassistant.components": components,
            "homeassistant.components.conversation": conversation,
            "homeassistant.helpers": helpers,
            "homeassistant.helpers.llm": llm,
            "homeassistant.helpers.selector": selector_mod,
            "probatio": probatio,
            "langchain_core": langchain_core,
            "langchain_core.messages": messages,
        }
    )


def _load_llm_tools():
    _install_extra_stubs()
    # Load llm_tools.py as a member of the (stubbed) integration package so
    # that its relative imports (e.g. ``from .const import LLM_API_NONE``)
    # resolve against the real ``const.py`` next to it.
    pkg_name = "custom_components.gigachain"
    if pkg_name not in sys.modules:
        pkg = types.ModuleType(pkg_name)
        pkg.__path__ = [str(LLM_TOOLS_PATH.parent)]
        sys.modules["custom_components"] = types.ModuleType("custom_components")
        sys.modules[pkg_name] = pkg
    spec = importlib.util.spec_from_file_location(
        f"{pkg_name}.llm_tools", LLM_TOOLS_PATH
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def llm_tools():
    """Return the loaded llm_tools module."""
    return _load_llm_tools()


# The exact schema probatio generates for the media_player
# HassSetVolumeRelative intent slot ("Change volume").
VOLUME_STEP_UNION = {
    "type": "object",
    "properties": {
        "volume_step": {
            "anyOf": [
                {"type": "string", "enum": ["up", "down"]},
                {"type": "integer", "minimum": -100, "maximum": 100},
            ]
        },
        "player_name": {"type": "string"},
    },
    "required": ["volume_step"],
}


def test_mixed_union_degrades_to_string(llm_tools):
    """A str|int union must not keep a string enum under an int type."""
    schema = llm_tools._sanitize_schema(VOLUME_STEP_UNION)
    volume = schema["properties"]["volume_step"]
    assert volume == {"type": "string"}
    assert "enum" not in volume
    assert "anyOf" not in volume and "oneOf" not in volume


def test_same_type_union_is_merged(llm_tools):
    schema = llm_tools._sanitize_schema(
        {"anyOf": [{"type": "string"}, {"type": "string", "enum": ["a", "b"]}]}
    )
    assert schema["type"] == "string"
    assert schema["enum"] == ["a", "b"]


def test_one_of_is_handled(llm_tools):
    schema = llm_tools._sanitize_schema(
        {"oneOf": [{"type": "integer"}, {"type": "integer", "minimum": 0}]}
    )
    assert schema["type"] == "integer"
    assert schema["minimum"] == 0


def test_numeric_enum_is_coerced_and_mismatch_dropped(llm_tools):
    schema = llm_tools._sanitize_schema({"type": "integer", "enum": ["5", "x"]})
    assert schema["type"] == "integer"
    assert schema["enum"] == [5]


def test_plain_string_enum_is_preserved(llm_tools):
    schema = llm_tools._sanitize_schema({"type": "string", "enum": ["a", "b"]})
    assert schema == {"type": "string", "enum": ["a", "b"]}


# The exact shape probatio generates for the media_player
# HassSetVolumeMute intent slot ("is_volume_muted"): description only, no type.
MUTE_SCHEMA = {
    "type": "object",
    "properties": {
        "is_volume_muted": {
            "description": "Whether the media player should be muted or unmuted"
        },
        "name": {"type": "string"},
    },
    "additionalProperties": False,
}


def test_typeless_property_gets_string_type(llm_tools):
    """A description-only property must gain a type or GigaChat answers 422."""
    schema = llm_tools._sanitize_schema(
        {"description": "Whether the media player should be muted or unmuted"}
    )
    assert schema == {
        "type": "string",
        "description": "Whether the media player should be muted or unmuted",
    }


def test_mute_slot_gets_type(llm_tools):
    schema = llm_tools._sanitize_schema(MUTE_SCHEMA)
    muted = schema["properties"]["is_volume_muted"]
    assert muted["type"] == "string"
    assert muted["description"] == "Whether the media player should be muted or unmuted"


def test_typeless_string_enum_infers_string(llm_tools):
    schema = llm_tools._sanitize_schema({"enum": ["up", "down"]})
    assert schema == {"type": "string", "enum": ["up", "down"]}


def test_typeless_integer_enum_infers_integer(llm_tools):
    schema = llm_tools._sanitize_schema({"enum": [1, 2, 3]})
    assert schema == {"type": "integer", "enum": [1, 2, 3]}


def test_typeless_mixed_enum_degrades_to_string(llm_tools):
    schema = llm_tools._sanitize_schema({"enum": ["up", 1]})
    assert schema == {"type": "string"}


def test_object_without_properties_gets_empty_properties(llm_tools):
    schema = llm_tools._sanitize_schema({"type": "object", "description": "x"})
    assert schema == {"type": "object", "description": "x", "properties": {}}


def test_tool_result_message_keeps_tool_name(llm_tools):
    """GigaChat needs the function name on role="function" history messages."""
    messages = llm_tools.chat_log_to_langchain(
        [
            llm_tools.conversation.ToolResultContent(
                result=llm_tools.llm.ToolResult(data={"success": True}),
                tool_call_id="call-1",
                tool_name="HassTurnOn",
            )
        ]
    )
    assert len(messages) == 1
    assert messages[0].name == "HassTurnOn"
    assert messages[0].tool_call_id == "call-1"


def test_normalize_llm_apis_passes_list_through(llm_tools):
    assert llm_tools.normalize_llm_apis(["assist", "mcp-demo"]) == [
        "assist",
        "mcp-demo",
    ]


def test_normalize_llm_apis_wraps_legacy_string(llm_tools):
    """Options saved before 0.4.0 hold a single id string."""
    assert llm_tools.normalize_llm_apis("assist") == ["assist"]


def test_normalize_llm_apis_drops_none_value(llm_tools):
    assert llm_tools.normalize_llm_apis(["none"]) == []
    assert llm_tools.normalize_llm_apis(["none", "assist"]) == ["assist"]


def test_normalize_llm_apis_empty_stays_empty(llm_tools):
    assert llm_tools.normalize_llm_apis(None) == []
    assert llm_tools.normalize_llm_apis([]) == []


def test_format_strip_is_dropped(llm_tools):
    """probatio leaks normalization hints; GigaChat only allows date formats."""
    schema = llm_tools._sanitize_schema(
        {"type": "string", "format": "strip", "description": "Filter by domain"}
    )
    assert schema == {"type": "string", "description": "Filter by domain"}


def test_format_lower_is_dropped(llm_tools):
    schema = llm_tools._sanitize_schema(
        {"type": "string", "format": "lower", "enum": ["loaded", "error"]}
    )
    assert schema == {"type": "string", "enum": ["loaded", "error"]}


def test_format_date_is_kept(llm_tools):
    schema = llm_tools._sanitize_schema({"type": "string", "format": "date"})
    assert schema == {"type": "string", "format": "date"}


def test_format_inside_properties_is_dropped(llm_tools):
    """The real-world shape: config__get_config_entries(domain.format='strip')."""
    schema = llm_tools._sanitize_schema(
        {
            "type": "object",
            "properties": {
                "domain": {
                    "description": "Filter by integration domain.",
                    "type": "string",
                    "format": "strip",
                },
                "status": {
                    "type": "string",
                    "format": "lower",
                    "enum": ["loaded", "error", "not_loaded"],
                },
            },
            "additionalProperties": False,
        }
    )
    assert schema["properties"]["domain"] == {
        "description": "Filter by integration domain.",
        "type": "string",
    }
    assert schema["properties"]["status"] == {
        "type": "string",
        "enum": ["loaded", "error", "not_loaded"],
    }
