# MQTT Entity Bridge - Pont MQTT pour Home Assistant

Extension HACS qui relie deux instances **Home Assistant** via un broker **MQTT**. Permet de:
- 📤 **Publier** les entités Home Assistant sur MQTT
- 🎮 **Contrôler** les entités d'un autre Home Assistant via MQTT
- 🔄 **Synchroniser** l'état des appareils entre deux instances HA

## 🚀 Installation

### Prérequis
- Home Assistant 2023.1.0 ou plus récent
- Un broker MQTT accessible (ex: Mosquitto, Cloud MQTT)
- HACS installé

### Installation via HACS
1. Ouvrir **HACS** → **Intégrations**
2. Cliquer sur **⋮** → **Repository personnalisé**
3. Ajouter l'URL: `https://github.com/[USERNAME]/mqtt_entity_bridge`
4. Cliquer sur **Installer**
5. Redémarrer Home Assistant

### Installation manuelle
1. Cloner le repo: `git clone https://github.com/[USERNAME]/mqtt_entity_bridge.git`
2. Copier le dossier `custom_components/mqtt_entity_bridge` dans `config/custom_components/`
3. Redémarrer Home Assistant

## ⚙️ Configuration

### Via l'interface Home Assistant
1. Aller à **Paramètres** → **Appareils et services**
2. Cliker sur **Créer une automation**
3. Chercher **MQTT Entity Bridge**
4. Rentrer les détails du broker MQTT:
   - **Adresse IP**: `192.168.1.100`
   - **Port**: `1883`
   - **Nom d'utilisateur**: `mqtt_user`
   - **Mot de passe**: `mqtt_password`
   - **Préfixe du sujet**: `homeassistant` (optionnel)

### Configuration YAML
```yaml
mqtt_entity_bridge:
  mqtt_host: "192.168.1.100"
  mqtt_port: 1883
  mqtt_user: "mqtt_user"
  mqtt_password: "mqtt_password"
  topic_prefix: "homeassistant"
  published_entities:
    - light.salon
    - light.cuisine
    - switch.garage
    - sensor.temperature_outdoor
```

## 🎯 Utilisation

### Services disponibles

#### 1. `mqtt_entity_bridge.publish_entity`
Publier une entité spécifique sur MQTT.

```yaml
service: mqtt_entity_bridge.publish_entity
data:
  entity_id: light.salon
```

#### 2. `mqtt_entity_bridge.publish_selected_entities`
Publier toutes les entités configurées.

```yaml
service: mqtt_entity_bridge.publish_selected_entities
```

#### 3. `mqtt_entity_bridge.update_published`
Mettre à jour la liste des entités publiées.

```yaml
service: mqtt_entity_bridge.update_published
data:
  entity_ids:
    - light.salon
    - switch.garage
```

### Structure MQTT

Les entités sont publiées sur les topics suivants:

```
homeassistant/light/salon/state
homeassistant/light/cuisine/state
homeassistant/switch/garage/state
```

**Payload de l'état**:
```json
{
  "entity_id": "light.salon",
  "state": "on",
  "attributes": {
    "brightness": 255,
    "color_temp": 370,
    "friendly_name": "Salon"
  },
  "last_changed": "2026-02-22T10:30:00",
  "last_updated": "2026-02-22T10:30:00"
}
```

### Contrôler les appareils via MQTT

Desde l'autre HA, envoyer un message à:

```
homeassistant/control/[domain]/[object_id]/set
```

**Exemples**:

1. **Allumer une lumière**:
   ```
   Topic: homeassistant/control/light/salon/set
   Payload: {"state": "on", "brightness": 200}
   ```

2. **Éteindre un switch**:
   ```
   Topic: homeassistant/control/switch/garage/set
   Payload: off
   ```

3. **Basculer un appliance**:
   ```
   Topic: homeassistant/control/light/cuisine/toggle
   Payload: (vide)
   ```

## 📊 Exemple d'automatisation

Lier deux Home Assistant:

```yaml
automation:
  - alias: "Publier entités salon sur MQTT"
    trigger:
      - platform: homeassistant
        event: start
    action:
      service: mqtt_entity_bridge.publish_selected_entities

  - alias: "Republier quand l'état change"
    trigger:
      - platform: state
        entity_id: 
          - light.salon
          - light.cuisine
          - switch.garage
    action:
      service: mqtt_entity_bridge.publish_entity
      data:
        entity_id: "{{ trigger.entity_id }}"
```

## 🐛 Dépannage

### La connexion MQTT échoue
- Vérifier l'adresse IP et le port du broker
- Vérifier les identifiants (username/password)
- S'assurer que le broker MQTT est accessible depuis la machine HA

### Les entités ne sont pas publiées
- Vérifier que la connexion MQTT est établie dans les logs
- Vérifier que les `entity_id` sont corrects
- Utiliser un client MQTT (ex: MQTT Explorer) pour vérifier les topics

### Voir les logs
```yaml
logger:
  logs:
    custom_components.mqtt_entity_bridge: debug
```

## 📝 Format de development

Pour modifier/étendre le composant:

```
mqtt_entity_bridge/
├── __init__.py           # Composant principal
├── config_flow.py        # Configuration UI
├── manifest.json         # Métadonnées
├── strings.json          # Traductions
└── README.md            # Documentation
```

## 🤝 Contribution

Les pull requests sont bienvenues! N'hésitez pas à ouvrir une issue si vous rencontrez un problème.

## 📄 Licence

MIT License - Voir [LICENSE](LICENSE)

## 💬 Support

Pour plus d'aide, ouvrir une issue dans le [GitHub Repository](https://github.com/artemis-fowl-fowl/haos-link-mqtt/issues)
