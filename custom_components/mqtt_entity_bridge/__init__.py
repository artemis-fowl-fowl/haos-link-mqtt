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
    _LOGGER.debug(f"async_setup called with config: {DOMAIN in config}")
    if DOMAIN not in config:
        return True

    hass.data[DOMAIN] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configuration du composant via UI."""
    _LOGGER.info(f"🚀 Setup entry pour MQTT Entity Bridge: {entry.data}")

    # Initialiser les données
    hass.data.setdefault(DOMAIN, {})
    
    # Récupérer les entités sélectionnées
    published_entities = entry.data.get("published_entities", [])
    _LOGGER.info(f"📝 Entités sélectionnées: {published_entities}")
    
    hass.data[DOMAIN]["published_entities"] = published_entities
    hass.data[DOMAIN]["mqtt_client"] = None

    # Créer le client MQTT
    mqtt_client = MQTTEntityBridge(hass, entry)
    hass.data[DOMAIN]["mqtt_client"] = mqtt_client
    
    _LOGGER.info(f"🔌 Tentative de connexion MQTT...")
    await mqtt_client.async_connect()
    
    # Attendre un peu que la connexion soit établie
    import asyncio
    await asyncio.sleep(1)
    
    # Publier les entités après connexion
    _LOGGER.info(f"📤 Publication des {len(published_entities)} entités...")
    for entity_id in published_entities:
        _LOGGER.info(f"   Publiant: {entity_id}")
        await mqtt_client.async_publish_entity(hass, entity_id)

    # Enregistrer les services
    async def handle_publish_service(call):
        entity_id = call.data.get("entity_id")
        _LOGGER.info(f"📤 Service: publication de {entity_id}")
        await mqtt_client.async_publish_entity(hass, entity_id)

    async def handle_publish_all_service(call):
        _LOGGER.info(f"📤 Service: publication de toutes les entités")
        for eid in published_entities:
            await mqtt_client.async_publish_entity(hass, eid)

    hass.services.async_register(
        DOMAIN,
        SERVICE_PUBLISH_ENTITY,
        handle_publish_service,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_PUBLISH_SELECTED,
        handle_publish_all_service,
    )

    _LOGGER.info(f"✅ MQTT Entity Bridge initialisé avec succès!")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Arrêter le composant."""
    _LOGGER.info("🛑 Déchargement de MQTT Entity Bridge")
    if DOMAIN in hass.data and hass.data[DOMAIN].get("mqtt_client"):
        client = hass.data[DOMAIN]["mqtt_client"]
        await client.async_disconnect()
    return True


class MQTTEntityBridge:
    """Gère la connexion MQTT et la publication des entités."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialiser le pont MQTT."""
        self.hass = hass
        self.entry = entry
        self.client = None
        self.config = entry.data

        self.mqtt_host = self.config.get("host")
        self.mqtt_port = self.config.get("port", 1883)
        self.mqtt_user = self.config.get("username")
        self.mqtt_password = self.config.get("password")
        self.topic_prefix = self.config.get("topic_prefix", "homeassistant")
        
        _LOGGER.info(f"🔧 MQTT Config: host={self.mqtt_host}, port={self.mqtt_port}, user={self.mqtt_user}, prefix={self.topic_prefix}")
        
        # Vérifier qu'on a tous les params
        if not self.mqtt_host:
            _LOGGER.error(f"❌ MQTT host non configuré!")
        if not self.mqtt_user:
            _LOGGER.error(f"❌ MQTT user non configuré!")

    async def async_connect(self) -> None:
        """Connecter au serveur MQTT."""
        try:
            _LOGGER.info(f"🔗 Connexion à {self.mqtt_host}:{self.mqtt_port} (user: {self.mqtt_user})...")
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_publish = self._on_publish
            
            if not self.mqtt_user:
                _LOGGER.warning(f"⚠️ User MQTT vide, connexion anonyme")
            
            self.client.username_pw_set(self.mqtt_user, self.mqtt_password)
            _LOGGER.debug(f"📝 Credentials configurées")
            
            self.client.connect(self.mqtt_host, self.mqtt_port, keepalive=60)
            _LOGGER.debug(f"📝 Connect() appelé")
            
            self.client.loop_start()
            _LOGGER.debug(f"📝 Loop démarré")
            
            _LOGGER.info(f"✅ Client MQTT initialisé et le loop lancé")
        except Exception as err:
            _LOGGER.error(f"❌ Erreur connexion MQTT: {err}", exc_info=True)

    async def async_disconnect(self) -> None:
        """Déconnecter de MQTT."""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            _LOGGER.info("🛑 Déconnecté de MQTT")

    def _on_connect(self, client, userdata, flags, rc):
        """Callback de connexion MQTT."""
        if rc == 0:
            _LOGGER.info(f"🎉 CONNECTÉ au broker MQTT! (code=0)")
        else:
            _LOGGER.error(f"❌ Erreur connexion MQTT: code {rc}")
            if rc == 1:
                _LOGGER.error("   → Erreur de protocole")
            elif rc == 2:
                _LOGGER.error("   → Client ID invalide")
            elif rc == 3:
                _LOGGER.error("   → Serveur indisponible")
            elif rc == 4:
                _LOGGER.error("   → Credentials invalides (user/password)")
            elif rc == 5:
                _LOGGER.error("   → Non autorisé")

    def _on_disconnect(self, client, userdata, rc):
        """Callback de déconnexion MQTT."""
        if rc != 0:
            _LOGGER.warning(f"⚠️ Déconnexion inattendue: code {rc}")

    def _on_publish(self, client, userdata, mid):
        """Callback publication."""
        _LOGGER.debug(f"📤 Message publié: mid={mid}")

    async def async_publish_entity(self, hass: HomeAssistant, entity_id: str) -> None:
        """Publier l'état d'une entité."""
        try:
            _LOGGER.info(f"📤 Tentative publication: {entity_id}")
            
            if not self.client:
                _LOGGER.error(f"   ❌ Client MQTT non connecté!")
                return

            state = hass.states.get(entity_id)
            if not state:
                _LOGGER.error(f"   ❌ Entité non trouvée dans HA: {entity_id}")
                return

            _LOGGER.info(f"   ✓ État trouvé: {state.state}")

            domain, obj_id = entity_id.split(".", 1)

            # 1. Publier discovery config (MQTT Auto-Discovery)
            config_topic = f"{self.topic_prefix}/{domain}/{obj_id}/config"
            discovery_config = {
                "unique_id": entity_id,
                "name": state.attributes.get("friendly_name", obj_id),
                "state_topic": f"{self.topic_prefix}/{domain}/{obj_id}/state",
                "state_value_template": "{{ value_json.state }}",
                "json_attributes_topic": f"{self.topic_prefix}/{domain}/{obj_id}/state",
                "json_attributes_template": "{{ value_json.attributes | tojson }}",
                "device_class": state.attributes.get("device_class"),
            }
            
            # Enlever les values None et vides
            discovery_config = {k: v for k, v in discovery_config.items() if v not in (None, "")}
            
            try:
                result = self.client.publish(config_topic, json.dumps(discovery_config), qos=1, retain=True)
                _LOGGER.debug(f"   📋 Discovery: topic={config_topic}, result.mid={result.mid}")
            except Exception as err:
                _LOGGER.error(f"   ❌ Erreur discovery: {err}", exc_info=True)

            # 2. Publier l'état actuel
            payload = {
                "entity_id": entity_id,
                "state": state.state,
                "attributes": state.attributes,
            }

            topic = f"{self.topic_prefix}/{domain}/{obj_id}/state"
            
            _LOGGER.debug(f"   📋 Topic: {topic}")
            _LOGGER.debug(f"   📋 Payload: {json.dumps(payload)}")
            
            result = self.client.publish(topic, json.dumps(payload), qos=1, retain=True)
            _LOGGER.info(f"✅ Publié: {entity_id} (mid={result.mid})")
            
        except Exception as err:
            _LOGGER.error(f"❌ Erreur publication {entity_id}: {err}", exc_info=True)

