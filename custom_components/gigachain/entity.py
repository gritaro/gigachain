"""Conversation agent entity for the GigaChain integration."""

from __future__ import annotations

import json
import logging
import re
from typing import Literal

from home_assistant_intents import get_languages
from homeassistant.components import conversation
from homeassistant.components.conversation import agent_manager
from homeassistant.components.homeassistant.exposed_entities import async_should_expose
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers import (
    area_registry as ar,
)
from homeassistant.helpers import (
    device_registry as dr,
)
from homeassistant.helpers import (
    entity_registry as er,
)
from homeassistant.helpers import (
    intent,
    template,
)

from . import llm_tools
from .const import (
    CONF_ENGINE,
    CONF_LLM_HASS_API,
    CONF_PROCESS_BUILTIN_SENTENCES,
    CONF_PROMPT,
    DEFAULT_LLM_HASS_API,
    DEFAULT_PROCESS_BUILTIN_SENTENCES,
    DEFAULT_PROMPT,
    DEFAULT_PROMPT_YANDEXGPT,
    DOMAIN,
    ID_GIGACHAT,
    ID_YANDEX_GPT,
    LLM_API_NONE,
)

LOGGER = logging.getLogger(__name__)

MAX_TOOL_ITERATIONS = 10

FUNCTION_CALL_MARKER = re.compile(r'\{\s*"function_call"')


class GigaChatAgent(conversation.ConversationEntity):
    """GigaChain conversation agent."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = conversation.ConversationEntityFeature.CONTROL

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the agent."""
        self.entry = entry
        self._attr_unique_id = entry.entry_id

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return a list of supported languages."""
        return get_languages()

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        conversation.async_set_agent(self.hass, self.entry, self)

    async def async_will_remove_from_hass(self) -> None:
        """When entity will be removed from hass."""
        conversation.async_unset_agent(self.hass, self.entry)
        await super().async_will_remove_from_hass()

    async def _async_handle_message(
        self,
        user_input: conversation.ConversationInput,
        chat_log: conversation.ChatLog,
    ) -> conversation.ConversationResult:
        """Process a message."""
        engine = self.entry.data.get(CONF_ENGINE) or ID_GIGACHAT
        llm_api_id = self._async_get_llm_api_id()

        use_builtin_sentences = self.entry.options.get(
            CONF_PROCESS_BUILTIN_SENTENCES, DEFAULT_PROCESS_BUILTIN_SENTENCES
        )
        if use_builtin_sentences:
            default_agent = agent_manager.async_get_agent(self.hass, None)
            default_agent_response = await default_agent.async_process(user_input)
            if default_agent_response.response.intent:
                return default_agent_response

        try:
            await chat_log.async_provide_llm_data(
                user_input.as_llm_context(DOMAIN),
                llm_api_id,
                self._user_prompt(engine),
                user_input.extra_system_prompt,
            )
        except conversation.ConverseError as err:
            return err.as_conversation_result()

        client = self.entry.runtime_data
        if engine == ID_YANDEX_GPT:
            await self._async_chat_with_prompt_functions(client, chat_log)
        else:
            await self._async_chat_with_tools(client, chat_log)

        return conversation.async_get_result_from_chat_log(user_input, chat_log)

    def _async_get_llm_api_id(self) -> str | None:
        """Return the HA LLM API to use, or None for a plain chat."""
        engine = self.entry.data.get(CONF_ENGINE) or ID_GIGACHAT
        if engine == ID_YANDEX_GPT:
            return None
        llm_api_id = self.entry.options.get(CONF_LLM_HASS_API, DEFAULT_LLM_HASS_API)
        if not llm_api_id or llm_api_id == LLM_API_NONE:
            return None
        return llm_api_id

    def _user_prompt(self, engine: str) -> str | None:
        """Return the user prompt template."""
        if engine == ID_YANDEX_GPT:
            return None
        return self.entry.options.get(CONF_PROMPT) or DEFAULT_PROMPT

    async def _async_chat_with_tools(
        self,
        client,
        chat_log: conversation.ChatLog,
    ) -> None:
        """Generate an answer, letting the model call HA tools natively."""
        bound_client = client
        if chat_log.llm_api is not None and chat_log.llm_api.tools:
            bound_client = client.bind_tools(
                llm_tools.hass_tools_to_langchain(chat_log.llm_api)
            )

        for _ in range(MAX_TOOL_ITERATIONS):
            messages = llm_tools.chat_log_to_langchain(chat_log.content)
            try:
                result = await self.hass.async_add_executor_job(
                    bound_client.invoke, messages
                )
            except Exception as err:
                LOGGER.exception("Error invoking LLM")
                chat_log.async_add_assistant_content_without_tools(
                    conversation.AssistantContent(
                        agent_id=self.entity_id,
                        content=f"Извини, произошла ошибка при обращении к модели: {err}",
                    )
                )
                return
            content = llm_tools.ai_message_to_assistant_content(
                self.entity_id, result
            )
            if content.tool_calls:
                async for _tool_result in chat_log.async_add_assistant_content(
                    content
                ):
                    pass
                continue
            chat_log.async_add_assistant_content_without_tools(content)
            return

        chat_log.async_add_assistant_content_without_tools(
            conversation.AssistantContent(
                agent_id=self.entity_id,
                content="Извини, я не смог обработать запрос: слишком много действий.",
            )
        )

    async def _async_chat_with_prompt_functions(
        self,
        client,
        chat_log: conversation.ChatLog,
    ) -> None:
        """Legacy control mode for engines without native function calling.

        The exposed entities are listed in the system prompt and the model is
        asked to reply with a function_call JSON, which is mapped to HA intents.
        """
        prompt = template.Template(
            self.entry.options.get(CONF_PROMPT) or DEFAULT_PROMPT_YANDEXGPT,
            self.hass,
        ).async_render(
            {
                "ha_name": self.hass.config.location_name,
                "exposed_entities": self._async_get_exposed_entities(),
            },
            parse_result=False,
        )
        chat_log.content[0] = conversation.SystemContent(content=prompt)

        result_text = ""
        for _ in range(MAX_TOOL_ITERATIONS):
            messages = llm_tools.chat_log_to_langchain(chat_log.content)
            try:
                result = await self.hass.async_add_executor_job(client.invoke, messages)
            except Exception as err:
                LOGGER.exception("Error invoking LLM")
                chat_log.async_add_assistant_content_without_tools(
                    conversation.AssistantContent(
                        agent_id=self.entity_id,
                        content=f"Извини, произошла ошибка при обращении к модели: {err}",
                    )
                )
                return
            chat_log.async_add_assistant_content_without_tools(
                conversation.AssistantContent(
                    agent_id=self.entity_id, content=result.content or ""
                )
            )
            function_data = self._parse_function_call(result.content or "")
            if function_data is None:
                return

            intent_type, slots = self._prepare_intent(function_data)
            if intent_type is None:
                chat_log.async_add_user_content(
                    conversation.UserContent(
                        content="Не удалось определить устройство, попроси пользователя уточнить запрос."
                    )
                )
                continue

            try:
                intent_response = await intent.async_handle(
                    self.hass, "conversation", intent_type, slots
                )
            except (intent.UnknownIntent, intent.InvalidSlotInfo, intent.IntentError) as err:
                LOGGER.error("Error handling intent %s: %s", intent_type, err)
                result_text = f"Ошибка выполнения: {err}"
            else:
                result_text = intent_response.speech.get("plain", {}).get(
                    "speech"
                ) or str(
                    intent_response.matched_states
                    or intent_response.unmatched_states
                    or "Готово"
                )
            LOGGER.debug("Function call result: %s", result_text)
            chat_log.async_add_user_content(
                conversation.UserContent(content=result_text)
            )

        chat_log.async_add_assistant_content_without_tools(
            conversation.AssistantContent(
                agent_id=self.entity_id, content=result_text
            )
        )

    def _prepare_intent(self, function_data: dict) -> tuple[str | None, dict]:
        """Map a parsed function_call to an HA intent with slots."""
        function_call = function_data.get("function_call")
        if not isinstance(function_call, dict):
            return None, {}
        function_type = function_call.get("type")
        entity_id = function_call.get("entity_id")
        if not entity_id:
            return None, {}

        entity_registry = er.async_get(self.hass)
        entity = entity_registry.async_get(entity_id)
        if entity is None:
            LOGGER.warning("Unknown entity from model: %s", entity_id)
            return None, {}

        area_id = entity.area_id
        if area_id is None and entity.device_id is not None:
            device = dr.async_get(self.hass).async_get(entity.device_id)
            area_id = device.area_id if device else None
        area_registry = ar.async_get(self.hass)
        area = area_registry.async_get_area(area_id) if area_id else None
        area_value = area.name if area else area_id
        location_text = function_call.get("location") or area_value or ""

        intent_type = None
        slots = {}
        if function_type == "switch":
            action = function_call.get("action")
            if action == "turn_on":
                intent_type = "HassTurnOn"
            elif action == "turn_off":
                intent_type = "HassTurnOff"
            if intent_type:
                slots = {
                    "name": {
                        "value": entity.name or entity_id,
                        "text": ", ".join(entity.aliases or []) or entity.name,
                    },
                    "area": {"value": area_value, "text": location_text},
                    "domain": {
                        "value": entity_id.partition(".")[0],
                        "text": entity_id.partition(".")[0],
                    },
                }
        elif function_type == "property":
            intent_type = "HassGetState"
            slots = {
                "name": {
                    "value": entity.name or entity_id,
                    "text": ", ".join(entity.aliases or []) or entity.name,
                },
                "area": {"value": area_value, "text": location_text},
            }
        LOGGER.debug("Prepared intent: %s, %s", intent_type, slots)
        return intent_type, slots

    @staticmethod
    def _parse_function_call(text: str) -> dict | None:
        """Extract a function_call JSON object from a model response."""
        match = FUNCTION_CALL_MARKER.search(text)
        if match is None:
            return None
        start = match.start()
        data = None
        try:
            data = json.loads(text[start:])
        except json.JSONDecodeError as err:
            try:
                data = json.loads(text[start : start + err.pos])
            except json.JSONDecodeError:
                LOGGER.warning("Failed to parse function call from: %s", text)
                return None
        if isinstance(data, dict) and isinstance(data.get("function_call"), dict):
            return data
        return None

    @callback
    def _async_get_exposed_entities(self) -> list[dict]:
        """Return entities exposed to the conversation agent."""
        states = [
            state
            for state in self.hass.states.async_all()
            if async_should_expose(self.hass, conversation.DOMAIN, state.entity_id)
        ]
        entity_registry = er.async_get(self.hass)
        device_registry = dr.async_get(self.hass)
        area_registry = ar.async_get(self.hass)
        exposed_entities = []
        for state in states:
            entity = entity_registry.async_get(state.entity_id)
            area_id = entity.area_id if entity else None
            if area_id is None and entity is not None and entity.device_id:
                device = device_registry.async_get(entity.device_id)
                area_id = device.area_id if device else None
            area = area_registry.async_get_area(area_id) if area_id else None
            exposed_entities.append(
                {
                    "entity_id": state.entity_id,
                    "name": state.name,
                    "state": state.state,
                    "area": area.name if area else (area_id or ""),
                    "aliases": list(entity.aliases) if entity and entity.aliases else [],
                }
            )
        return exposed_entities
