"""Config flow pour MQTT Entity Bridge."""
import logging
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

CONF_TOPIC_PREFIX = "topic_prefix"
CONF_PUBLISHED_ENTITIES = "published_entities"


class MQTTEntityBridgeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow pour MQTT Entity Bridge."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Première étape: configuration MQTT."""
        errors = {}

        if user_input is not None:
            try:
                # Tester la connexion MQTT
                await self.hass.async_add_executor_job(
                    test_mqtt_connection,
                    user_input.get(CONF_HOST),
                    user_input.get(CONF_PORT),
                    user_input.get(CONF_USERNAME),
                    user_input.get(CONF_PASSWORD),
                )
                return self.async_create_entry(
                    title=f"MQTT Bridge ({user_input.get(CONF_HOST)})",
                    data=user_input,
                )
            except ConnectionError as err:
                _LOGGER.error(f"Erreur connexion MQTT: {err}")
                errors["base"] = "cannot_connect"
            except Exception as err:
                _LOGGER.error(f"Erreur inattendue: {err}")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default="192.168.1.100"): str,
                    vol.Required(CONF_PORT, default=1883): int,
                    vol.Required(CONF_USERNAME, default=""): str,
                    vol.Required(CONF_PASSWORD, default=""): str,
                    vol.Required(CONF_TOPIC_PREFIX, default="homeassistant"): str,
                }
            ),
            errors=errors,
            description_placeholders={
                "example_host": "192.168.1.100 (adresse IP du broker MQTT)",
                "example_port": "1883 (port MQTT standard)",
            },
        )

    async def async_step_select_entities(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Deuxième étape: sélectionner les entités à publier."""
        if user_input is not None:
            user_data = self.hass.data.get("mqtt_bridge_setup", {})
            user_data.update(user_input)
            return self.async_create_entry(
                title="MQTT Entity Bridge",
                data=user_data,
            )

        # Récupérer les entités disponibles
        states = self.hass.states.async_all()
        entities = {s.entity_id: s.entity_id for s in states}

        return self.async_show_form(
            step_id="select_entities",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_PUBLISHED_ENTITIES, default=[]): vol.In(entities),
                }
            ),
        )


def test_mqtt_connection(host: str, port: int, username: str, password: str) -> bool:
    """Tester la connexion MQTT."""
    import paho.mqtt.client as mqtt

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    client.username_pw_set(username, password)

    try:
        client.connect(host, port, keepalive=5)
        client.disconnect()
        return True
    except Exception as err:
        raise ConnectionError(f"Impossible de se connecter: {err}")


class CannotConnectError(HomeAssistantError):
    """Erreur de connexion."""
