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


def _sanitize_schema(node: Any) -> Any:
    """Normalize a JSON schema for GigaChat function calling.

    GigaChat does not support array types, ``anyOf`` or schemas without an
    explicit object/dict type, so arrays are flattened to their item schema
    (HA intent slots accept single values thanks to EnsureList), anyOf is
    merged and empty or bare-string schemas become ``{"type": "string"}``.
    """
    if isinstance(node, str):
        return {"type": node}
    if not isinstance(node, dict):
        return node
    if not node:
        return {"type": "string"}
    if node.get("type") == "array":
        return _sanitize_schema(node.get("items") or {})
    if "anyOf" in node:
        merged: dict[str, Any] = {}
        for option in node.pop("anyOf"):
            if isinstance(option, dict):
                merged.update(_sanitize_schema(option))
        node = {**node, **merged}
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
