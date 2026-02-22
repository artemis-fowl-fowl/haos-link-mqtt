"""Config flow pour MQTT Entity Bridge."""
import logging
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

CONF_TOPIC_PREFIX = "topic_prefix"
CONF_PUBLISHED_ENTITIES = "published_entities"


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow pour MQTT Entity Bridge."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialiser le flow."""
        self.mqtt_config: Dict[str, Any] = {}

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
                # Sauvegarder et aller à l'étape suivante
                self.mqtt_config = user_input
                return await self.async_step_select_entities()
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
        )

    async def async_step_select_entities(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Deuxième étape: sélectionner les entités à publier."""
        if user_input is not None:
            # Combiner les données MQTT avec les entités sélectionnées
            config_data = {**self.mqtt_config, **user_input}
            return self.async_create_entry(
                title=f"MQTT Bridge ({self.mqtt_config.get(CONF_HOST)})",
                data=config_data,
            )

        # Récupérer les entités disponibles
        states = self.hass.states.async_all()
        entity_ids = sorted([state.entity_id for state in states])
        entities_dict = {eid: eid for eid in entity_ids}

        return self.async_show_form(
            step_id="select_entities",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_PUBLISHED_ENTITIES, default=[]): cv.multi_select(entities_dict),
                }
            ),
        )


def test_mqtt_connection(host: str, port: int, username: str, password: str) -> bool:
    """Tester la connexion MQTT."""
    import paho.mqtt.client as mqtt
    import time

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    client.username_pw_set(username, password)

    try:
        _LOGGER.debug(f"🧪 Test MQTT: {host}:{port} avec user={username}")
        client.connect(host, port, keepalive=5)
        client.loop_start()
        time.sleep(2)  # Attendre la connexion
        client.loop_stop()
        client.disconnect()
        _LOGGER.debug(f"✅ Test MQTT réussi")
        return True
    except Exception as err:
        _LOGGER.error(f"❌ Test MQTT échoué: {err}")
        raise ConnectionError(f"Impossible de se connecter: {err}")


class CannotConnectError(HomeAssistantError):
    """Erreur de connexion."""
