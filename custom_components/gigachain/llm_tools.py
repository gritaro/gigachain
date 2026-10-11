"""Helpers to convert between Home Assistant ChatLog content and langchain messages."""

from __future__ import annotations

import json
import logging
from typing import Any

import probatio
from homeassistant.components import conversation
from homeassistant.helpers import llm
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

LOGGER = logging.getLogger(__name__)

LOCATION_TOOL_NAME = "GetLocation"


def location_tool_to_langchain() -> dict[str, Any]:
    """Return the custom tool spec used to answer location questions."""
    return {
        "type": "function",
        "function": {
            "name": LOCATION_TOOL_NAME,
            "description": (
                "Get the current location of a person or a device tracker, "
                "such as a phone. Use it to answer questions like 'where is "
                "...' or 'is ... at home'. Returns the zone name and the "
                "distance from home."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": (
                            "Name of the person or tracked device, or its "
                            "entity_id."
                        ),
                    }
                },
                "required": ["name"],
            },
        },
    }


NUMERIC_CONSTRAINTS = (
    "minimum",
    "maximum",
    "exclusiveMinimum",
    "exclusiveMaximum",
    "multipleOf",
)


def _infer_primitive_type(values: list[Any]) -> str | None:
    """Infer a single JSON-schema type from enum values, or ``None``."""
    kinds: set[str] = set()
    for value in values:
        if isinstance(value, bool):
            kinds.add("boolean")
        elif isinstance(value, int):
            kinds.add("integer")
        elif isinstance(value, float):
            kinds.add("number")
        elif isinstance(value, str):
            kinds.add("string")
        else:
            return None
    if len(kinds) == 1:
        return kinds.pop()
    return None


def _fix_numeric_enum(node: dict[str, Any]) -> None:
    """Align an ``enum`` with the declared numeric type.

    GigaChat rejects an enum whose values do not match the property type (for
    example a ``type: integer`` with string values). Values that can be coerced
    are converted, the rest are dropped; an empty enum is removed.
    """
    node_type = node.get("type")
    values = node.get("enum")
    if not isinstance(values, list):
        return
    if node_type == "integer":
        caster: type = int
    elif node_type == "number":
        caster = float
    else:
        return
    coerced: list[Any] = []
    for value in values:
        try:
            coerced.append(caster(value))
        except (TypeError, ValueError):
            continue
    if coerced:
        node["enum"] = coerced
    else:
        node.pop("enum", None)


def _sanitize_schema(node: Any) -> Any:
    """Normalize a JSON schema for GigaChat function calling.

    GigaChat does not support array types, ``anyOf``/``oneOf`` unions or
    schemas without an explicit object/dict type, so arrays are flattened to
    their item schema (HA intent slots accept single values thanks to
    EnsureList), unions are collapsed and empty or bare-string schemas become
    ``{"type": "string"}``.

    A union whose members share one type is merged into a single schema. A
    union of different types (for example ``str | int``) cannot be expressed,
    so it degrades to a plain ``string`` and the constraints of the other
    branches are dropped: HA validators coerce strings back to their target
    type, so both ``"up"``/``"down"`` and ``"5"`` keep working.

    Every property must end up with an explicit primitive ``type``. GigaChat
    treats a property that only carries a ``description`` (as probatio emits
    for ``cv.boolean`` slots such as ``is_volume_muted``) as an object and
    rejects the whole request with a 422, so such nodes are given a type
    inferred from their ``enum`` or default to ``string``.
    """
    if isinstance(node, str):
        return {"type": node}
    if not isinstance(node, dict):
        return node
    if not node:
        return {"type": "string"}
    if node.get("type") == "array":
        return _sanitize_schema(node.get("items") or {})
    union = node.get("anyOf") or node.get("oneOf")
    if union is not None:
        rest = {k: v for k, v in node.items() if k not in ("anyOf", "oneOf")}
        options = [
            _sanitize_schema(option) for option in union if isinstance(option, dict)
        ]
        types = {option.get("type") for option in options}
        if len(types) == 1 and None not in types:
            merged = rest
            for option in options:
                merged.update(option)
            node = merged
        else:
            node = {**rest, "type": "string"}
            for key in ("enum", *NUMERIC_CONSTRAINTS):
                node.pop(key, None)
        if node.get("type") == "array":
            return _sanitize_schema(node.get("items") or {})
    result: dict[str, Any] = {}
    for key, value in node.items():
        if key == "properties" and isinstance(value, dict):
            result["properties"] = {
                name: _sanitize_schema(sub) for name, sub in value.items()
            }
        elif isinstance(value, dict):
            result[key] = _sanitize_schema(value)
        else:
            result[key] = value
    if "type" not in result:
        enum = result.get("enum")
        inferred = _infer_primitive_type(enum) if isinstance(enum, list) and enum else None
        if inferred is not None:
            result["type"] = inferred
        else:
            result["type"] = "string"
            result.pop("enum", None)
    if result.get("type") == "object" and not isinstance(result.get("properties"), dict):
        result["properties"] = {}
    _fix_numeric_enum(result)
    return result


def hass_tools_to_langchain(llm_api: llm.APIInstance) -> list[dict[str, Any]]:
    """Convert HA LLM API tools to OpenAI-style function specs for bind_tools()."""
    tools: list[dict[str, Any]] = []
    for tool in llm_api.tools:
        schema = probatio.to_openapi(
            tool.parameters,
            custom_serializer=llm_api.custom_serializer,
            openapi_version="3.1.0",
        )
        for key in ("oneOf", "anyOf", "allOf", "not"):
            schema.pop(key, None)
        schema = _sanitize_schema(schema)
        if isinstance(schema, dict):
            schema.setdefault("type", "object")
        LOGGER.debug("Tool %s schema: %s", tool.name, json.dumps(schema, ensure_ascii=False))
        tools.append(
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": schema,
                },
            }
        )
    return tools


def chat_log_to_langchain(content: list[conversation.Content]) -> list[BaseMessage]:
    """Convert HA ChatLog content to langchain messages."""
    messages: list[BaseMessage] = []
    for item in content:
        if isinstance(item, conversation.SystemContent):
            messages.append(SystemMessage(content=item.content))
        elif isinstance(item, conversation.UserContent):
            messages.append(HumanMessage(content=item.content))
        elif isinstance(item, conversation.AssistantContent):
            if item.tool_calls:
                messages.append(
                    AIMessage(
                        content=item.content or "",
                        tool_calls=[
                            {
                                "name": tool_call.tool_name,
                                "args": tool_call.tool_args,
                                "id": tool_call.id,
                            }
                            for tool_call in item.tool_calls
                        ],
                    )
                )
            else:
                messages.append(AIMessage(content=item.content or ""))
        elif isinstance(item, conversation.ToolResultContent):
            messages.append(
                ToolMessage(
                    content=json.dumps(item.result.data, ensure_ascii=False),
                    tool_call_id=item.tool_call_id,
                    name=item.tool_name,
                )
            )
    return messages


def ai_message_to_assistant_content(
    agent_id: str, message: AIMessage
) -> conversation.AssistantContent:
    """Convert a langchain AI message to HA assistant content."""
    tool_calls = None
    if message.tool_calls:
        tool_calls = [
            llm.ToolInput(
                tool_name=tool_call["name"],
                tool_args=tool_call.get("args") or {},
                id=tool_call.get("id") or message.id,
            )
            for tool_call in message.tool_calls
        ]
    return conversation.AssistantContent(
        agent_id=agent_id,
        content=message.content or None,
        tool_calls=tool_calls,
    )
