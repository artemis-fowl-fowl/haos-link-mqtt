# Guide d'utilisation complet - MQTT Entity Bridge

Ce guide explique comment configurer et utiliser **MQTT Entity Bridge** pour relier deux instances Home Assistant.

## Table des matières
1. [Installation](#installation)
2. [Configuration initiale](#configuration-initiale)
3. [Publier les entités](#publier-les-entités)
4. [Contrôler à distance via MQTT](#contrôler-à-distance-via-mqtt)
5. [Cas d'usage courants](#cas-dusage-courants)
6. [Dépannage](#dépannage)

---

## Installation

### 1. Installer HACS (si ce n'est pas déjà fait)
- Suivre: https://hacs.xyz/docs/setup/prerequisites
- Une fois installé, vous verrez **HACS** dans le menu de gauche

### 2. Ajouter le dépôt personnalisé
1. Aller à **HACS** → **Intégrations**
2. Cliquer sur **⋮** (menu) → **Dépôts personnalisés**
3. Ajouter: `https://github.com/mqtt_entity_bridge`
4. Chercher **MQTT Entity Bridge**
5. Cliquer sur **Installer**
6. **Redémarrer Home Assistant**

### 3. Configurer l'intégration
- Aller à **Paramètres** → **Appareils et services**
- Chercher **MQTT Entity Bridge** et configurer

---

## Configuration initiale

### 🔗 Obtenir les détails du broker MQTT

Si vous utilisez **Mosquitto** sur HA:
```yaml
mqtt:
  broker: homeassistant.local
  port: 1883
  username: mqtt_user
  password: mqtt_password
```

Ces données sont utilisées pour **MQTT Entity Bridge**.

### ⚙️ Configuration via interface HA

1. **Adresse IP**: Entrer l'IP du broker
   - Exemple: `192.168.1.100` ou `mosquitto.local`

2. **Port**: 1883 (port standard MQTT)

3. **Nom d'utilisateur**: Votre compte MQTT

4. **Mot de passe**: Votre mot de passe MQTT

5. **Préfixe du sujet** (optionnel): `homeassistant`
   - Sera utilisé pour tous les topics MQTT publiés

---

## Publier les entités

### Méthode 1: Via un service (le plus facile)

Dans n'importe quelle automatisation ou script:

```yaml
action:
  service: mqtt_entity_bridge.publish_selected_entities
```

### Méthode 2: Publier une seule entité

```yaml
service: mqtt_entity_bridge.publish_entity
data:
  entity_id: light.salon
```

### Méthode 3: Configuration YAML

Il est possible d'automatiser la publication au démarrage:

```yaml
automation:
  - alias: "Publier entités au démarrage"
    trigger:
      - platform: homeassistant
        event: start
    action:
      service: mqtt_entity_bridge.publish_selected_entities
```

### Méthode 4: Republier en temps réel

Publier automatiquement dès que l'état change:

```yaml
automation:
  - alias: "Republier lumières"
    trigger:
      - platform: state
        entity_id:
          - light.salon
          - light.cuisine
    action:
      service: mqtt_entity_bridge.publish_entity
      data:
        entity_id: "{{ trigger.entity_id }}"
```

---

## Contrôler à distance via MQTT

Une fois les entités publiées, vous pouvez les contrôler depuis un autre système.

### Vérifier les topics MQTT

Utilisez un client MQTT comme **MQTT Explorer** pour voir les topics:

```
homeassistant/light/salon/state
homeassistant/light/cuisine/state
homeassistant/switch/garage/state
```

### Contrôler une lumière

**Topic**: `homeassistant/control/light/salon/set`  
**Payload**:
```json
{
  "state": "on",
  "brightness": 200,
  "color_temp": 370
}
```

### Contrôler un switch

**Topic**: `homeassistant/control/switch/garage/set`  
**Payload**: `on` ou `off`

### Exemple avec Node-RED

Dans Node-RED, créez un nœud MQTT Out:

```
Topic: homeassistant/control/light/cuisine/set
Payload: {"state":"on","brightness":255}
```

---

## Cas d'usage courants

### 🏠 Relier deux maisons via MQTT

**HA Principale (Maison 1)**:
```yaml
automation:
  - alias: "Publier salon maison 1"
    trigger:
      - platform: homeassistant
        event: start
    action:
      service: mqtt_entity_bridge.publish_selected_entities
```

**HA Secondaire (Maison 2)**:
- Configure le même broker MQTT
- Reçoit les states de Maison 1
- Peut les contrôler via MQTT

### 🔗 Intégration avec Node-RED

1. Connecter Node-RED au même broker MQTT
2. Utiliser les nœuds MQTT pour:
   - Recevoir les états
   - Envoyer des commandes

Exemple Node-RED:
```
[MQTT In] homeassistant/light/salon/state
    ↓
[Function] - Parser le JSON
    ↓
[Node-RED Logic]
    ↓
[MQTT Out] homeassistant/control/light/cuisine/set
```

### 📱 Créer des panneaux de contrôle

Avec **Home Assistant** ou un autre client MQTT:

```yaml
script:
  toggle_all_lights:
    sequence:
      - service: mqtt.publish
        data:
          topic: homeassistant/control/light/salon/set
          payload: '{"state":"toggle"}'
      - service: mqtt.publish
        data:
          topic: homeassistant/control/light/cuisine/set
          payload: '{"state":"toggle"}'
```

### 🎚️ Synchroniser des capteurs

Publier régulièrement les états des capteurs:

```yaml
automation:
  - alias: "Synchroniser température"
    trigger:
      - platform: time_pattern
        minutes: "/5"  # Toutes les 5 minutes
    action:
      service: mqtt_entity_bridge.publish_entity
      data:
        entity_id: sensor.temperature_salon
```

---

## Dépannage

### ❌ "Impossible de se connecter au broker MQTT"

**Causes possibles**:
1. L'IP du broker est incorrecte
2. Le port 1883 est fermé/bloquer
3. Les identifiants sont incorrect
4. Le broker MQTT ne fonctionne pas

**Solutions**:
- Vérifier l'IP avec: `ping mosquitto.local`
- Vérifier le port: `telnet 192.168.1.100 1883`
- Réinitialiser les identifiants MQTT
- Vérifier les logs: `logger: custom_components.mqtt_entity_bridge: debug`

### ❌ Les entités ne sont pas publiées

**Vérifier**:
1. La connexion MQTT est établie (voir les logs)
2. Les `entity_id` existent vraiment
3. Vérifier avec MQTT Explorer si les topics existent

**Test rapide**:
```yaml
service: mqtt_entity_bridge.publish_entity
data:
  entity_id: light.salon
```

Voir dans MQTT Explorer si `homeassistant/light/salon/state` apparaît.

### ❌ Payload mal formaté

Vérifier le format JSON du payload:
```json
{
  "entity_id": "light.salon",
  "state": "on",
  "attributes": {},
  "last_changed": "2026-02-22T10:30:00",
  "last_updated": "2026-02-22T10:30:00"
}
```

### 🔧 Activer la verbosité des logs

Dans `configuration.yaml`:
```yaml
logger:
  logs:
    custom_components.mqtt_entity_bridge: debug
```

Puis redémarrer HA et vérifier les logs dans **Paramètres** → **Système** → **Journaux**.

---

## ℹ️ Informations supplémentaires

- **Format MQTT**: HomeAssistant Discovery compatible
- **QoS**: Niveau 1 (entente de livraison)
- **Retain**: Activé (les messages persistent)
- **Connexion**: Automatique avec reconnexion

---

## 📞 Support

- Issues: Ouvrir un ticket sur GitHub
- Questions: Discussion forum HA
- Logs: Partager les logs `mqtt_entity_bridge`
