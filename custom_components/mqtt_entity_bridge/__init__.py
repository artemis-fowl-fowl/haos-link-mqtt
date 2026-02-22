"""MQTT Entity Bridge - Lie deux Home Assistant via MQTT."""
import logging
import json
from typing import Any

import paho.mqtt.client as mqtt
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_registry import async_get as get_entity_registry
from homeassistant.helpers.state import State

_LOGGER = logging.getLogger(__name__)

DOMAIN = "mqtt_entity_bridge"
PLATFORMS = [Platform.LIGHT, Platform.SWITCH, Platform.SENSOR]

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required("mqtt_host"): cv.string,
                vol.Required("mqtt_port", default=1883): cv.port,
                vol.Required("mqtt_user"): cv.string,
                vol.Required("mqtt_password"): cv.string,
                vol.Required("topic_prefix", default="homeassistant"): cv.string,
                vol.Optional("published_entities", default=[]): cv.ensure_list,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

SERVICE_PUBLISH_ENTITY = "publish_entity"
SERVICE_PUBLISH_SELECTED = "publish_selected_entities"
SERVICE_UPDATE_PUBLISHED = "update_published_entities"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Configuration YAML pour MQTT Entity Bridge."""
    if DOMAIN not in config:
        return True

    hass.data[DOMAIN] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configuration du composant via UI."""
    _LOGGER.debug(f"Setup entry: {entry.data}")

    # Initialiser les données
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["mqtt_client"] = None
    hass.data[DOMAIN]["published_entities"] = entry.data.get("published_entities", [])

    # Créer le client MQTT
    mqtt_client = MQTTEntityBridge(hass, entry)
    hass.data[DOMAIN]["mqtt_client"] = mqtt_client

    # Enregistrer les services
    hass.services.async_register(
        DOMAIN,
        SERVICE_PUBLISH_ENTITY,
        handle_publish_entity,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_id,
        }),
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_PUBLISH_SELECTED,
        handle_publish_selected,
        schema=vol.Schema({}),
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE_PUBLISHED,
        handle_update_published,
        schema=vol.Schema({
            vol.Required("entity_ids"): cv.ensure_list,
        }),
    )

    # Connecter MQTT
    await mqtt_client.async_connect()

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Arrêter le composant."""
    if DOMAIN in hass.data and hass.data[DOMAIN].get("mqtt_client"):
        client = hass.data[DOMAIN]["mqtt_client"]
        await client.async_disconnect()

    return True


async def handle_publish_entity(hass: HomeAssistant, call: Any) -> None:
    """Publier une entité spécifique."""
    entity_id = call.data.get("entity_id")
    client = hass.data[DOMAIN]["mqtt_client"]
    await client.async_publish_entity(hass, entity_id)


async def handle_publish_selected(hass: HomeAssistant, call: Any) -> None:
    """Publier les entités sélectionnées."""
    client = hass.data[DOMAIN]["mqtt_client"]
    entity_ids = hass.data[DOMAIN].get("published_entities", [])
    for entity_id in entity_ids:
        await client.async_publish_entity(hass, entity_id)


async def handle_update_published(hass: HomeAssistant, call: Any) -> None:
    """Mettre à jour la liste des entités publiées."""
    entity_ids = call.data.get("entity_ids", [])
    hass.data[DOMAIN]["published_entities"] = entity_ids
    _LOGGER.info(f"Entités publiées mises à jour: {entity_ids}")


class MQTTEntityBridge:
    """Gère la connexion MQTT et la publication des entités."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialiser le pont MQTT."""
        self.hass = hass
        self.entry = entry
        self.client = None
        self.config = entry.data

        self.mqtt_host = self.config.get("mqtt_host")
        self.mqtt_port = self.config.get("mqtt_port", 1883)
        self.mqtt_user = self.config.get("mqtt_user")
        self.mqtt_password = self.config.get("mqtt_password")
        self.topic_prefix = self.config.get("topic_prefix", "homeassistant")

    async def async_connect(self) -> None:
        """Connecter au serveur MQTT."""
        try:
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
            self.client.on_connect = self._on_connect
            self.client.on_message = self._on_message
            self.client.on_disconnect = self._on_disconnect

            self.client.username_pw_set(self.mqtt_user, self.mqtt_password)

            self.client.connect(self.mqtt_host, self.mqtt_port, keepalive=60)
            self.client.loop_start()

            _LOGGER.info(
                f"Connexion MQTT établie: {self.mqtt_host}:{self.mqtt_port}"
            )
        except Exception as err:
            _LOGGER.error(f"Erreur de connexion MQTT: {err}")

    async def async_disconnect(self) -> None:
        """Déconnecter de MQTT."""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            _LOGGER.info("Déconnecté de MQTT")

    def _on_connect(self, client, userdata, flags, rc):
        """Callback de connexion MQTT."""
        if rc == 0:
            _LOGGER.info("Connecté au broker MQTT")
            # S'abonner aux topics de contrôle
            client.subscribe(f"{self.topic_prefix}/control/#")
            client.subscribe(f"{self.topic_prefix}/request/#")
        else:
            _LOGGER.error(f"Erreur de connexion MQTT: code {rc}")

    def _on_disconnect(self, client, userdata, rc):
        """Callback de déconnexion MQTT."""
        if rc != 0:
            _LOGGER.warning(f"Déconnexion inattendue: code {rc}")

    def _on_message(self, client, userdata, msg):
        """Traiter les messages MQTT entrants."""
        _LOGGER.debug(f"Message reçu: {msg.topic} = {msg.payload.decode()}")

        # Exemple: homeassistant/control/light.salon/set
        parts = msg.topic.split("/")
        if len(parts) >= 3 and parts[1] == "control":
            # Extraire entity_id et le state/commande
            entity_domain_id = "/".join(parts[2:-1])  # light.salon
            command = parts[-1]  # set ou toggle

            payload = msg.payload.decode()
            self.hass.create_task(
                self._handle_control_message(entity_domain_id, command, payload)
            )

    async def _handle_control_message(self, entity_id: str, command: str, payload: str) -> None:
        """Gérer les messages de contrôle entrants."""
        domain = entity_id.split(".")[0]

        if domain == "light":
            if command == "set":
                payload_dict = json.loads(payload) if payload.startswith("{") else {"state": payload}
                if payload_dict.get("state") == "on":
                    await self.hass.services.async_call(
                        "light", "turn_on", {"entity_id": entity_id}
                    )
                else:
                    await self.hass.services.async_call(
                        "light", "turn_off", {"entity_id": entity_id}
                    )

        elif domain == "switch":
            if payload == "on":
                await self.hass.services.async_call(
                    "switch", "turn_on", {"entity_id": entity_id}
                )
            else:
                await self.hass.services.async_call(
                    "switch", "turn_off", {"entity_id": entity_id}
                )

        _LOGGER.info(f"Commande appliquée: {entity_id} -> {payload}")

    async def async_publish_entity(self, hass: HomeAssistant, entity_id: str) -> None:
        """Publier l'état d'une entité."""
        if not self.client:
            _LOGGER.warning("Client MQTT non connecté")
            return

        state = hass.states.get(entity_id)
        if not state:
            _LOGGER.warning(f"Entité non trouvée: {entity_id}")
            return

        domain, obj_id = entity_id.split(".", 1)

        # Créer le payload avec les infos
        payload = {
            "entity_id": entity_id,
            "state": state.state,
            "attributes": state.attributes,
            "last_changed": state.last_changed.isoformat() if state.last_changed else None,
            "last_updated": state.last_updated.isoformat() if state.last_updated else None,
        }

        # Topic: homeassistant/light/salon/state
        topic = f"{self.topic_prefix}/{domain}/{obj_id}/state"

        try:
            self.client.publish(topic, json.dumps(payload), qos=1, retain=True)
            _LOGGER.debug(f"Publié: {topic} = {payload}")
        except Exception as err:
            _LOGGER.error(f"Erreur publication: {err}")

    async def async_publish_all_entities(self, hass: HomeAssistant) -> None:
        """Publier toutes les entités sélectionnées."""
        entity_ids = self.hass.data[DOMAIN].get("published_entities", [])
        for entity_id in entity_ids:
            await self.async_publish_entity(hass, entity_id)
