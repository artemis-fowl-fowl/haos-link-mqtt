# Cas d'utilisation avancés - MQTT Entity Bridge

## 1. 🏘️ Relier 3 maisons Home Assistant

### Architecture:
```
Maison 1 (HA)  ──┐
                  ├─── Broker MQTT ───── Node-RED (optionnel)
Maison 2 (HA)  ──┤
                  │
Maison 3 (HA)  ──┘
```

### Configuration Maison 1 (Principale):
```yaml
mqtt_entity_bridge:
  mqtt_host: "mqtt.mondomaine.local"
  mqtt_user: "ha_user"
  mqtt_password: !secret mqtt_password
  topic_prefix: "maisons"
  published_entities:
    - light.salon
    - light.cuisine
    - switch.climatisation
```

### Configuration Maison 2 (Secondaire):
Même configuration avec une préfixe différente si souhaité:
```yaml
mqtt_entity_bridge:
  mqtt_host: "mqtt.mondomaine.local"
  mqtt_user: "ha_user"
  mqtt_password: !secret mqtt_password
  topic_prefix: "maisons"
  published_entities:
    - light.chambre
    - sensor.temperature
```

### Résultat:
```
maisons/light/salon/state
maisons/light/cuisine/state
maisons/switch/climatisation/state
maisons/light/chambre/state
maisons/sensor/temperature/state
```

---

## 2. 🤖 Intégrer Node-RED pour l'automatisation

### Flux Node-RED de base:

```json
[
  {
    "id": "mqtt_in",
    "type": "mqtt in",
    "topic": "homeassistant/light/+/state",
    "qos": "1"
  },
  {
    "id": "json_parser",
    "type": "json",
    "action": "obj"
  },
  {
    "id": "switch_logic",
    "type": "switch",
    "property": "payload.state"
  },
  {
    "id": "mqtt_out",
    "type": "mqtt out",
    "topic": "homeassistant/control/light/cuisine/set"
  }
]
```

### Exemple: Synchroniser deux lumières

Quand `light.salon` s'allume, allumer aussi `light.cuisine`:

**Nœud 1 (MQTT In)**:
- Topic: `homeassistant/light/salon/state`

**Nœud 2 (Function)**:
```javascript
msg.payload = {
  state: msg.payload.state,
  brightness: msg.payload.attributes.brightness
};
return msg;
```

**Nœud 3 (MQTT Out)**:
- Topic: `homeassistant/control/light/cuisine/set`
- Payload: `msg.payload`

---

## 3. 🔐 Sécuriser la connexion MQTT

### Utiliser des certificats SSL

```yaml
mqtt_entity_bridge:
  mqtt_host: "mqtt.secure.local"
  mqtt_port: 8883  # Port SSL
  mqtt_user: "secure_user"
  mqtt_password: !secret mqtt_password
  # Certificat client (si requis)
  ca_certs: "/config/certs/ca.crt"
  client_cert: "/config/certs/client.crt"
  client_key: "/config/certs/client.key"
```

### ACLs Mosquitto recommandées:

```
user admin
topic admin
topic read homeassistant/#
topic write homeassistant/control/#

user ha_device
topic read homeassistant/#
topic write homeassistant/control/#
```

---

## 4. 📊 Monitorer via InfluxDB

### Flux Node-RED:

```
MQTT In (homeassistant/+/+/state)
    ↓
Extract Entity & Value
    ↓
InfluxDB Out (save to database)
    ↓
Grafana (visualize)
```

### Exemple Node-RED Function:

```javascript
const payload = JSON.parse(msg.payload);
const entity = payload.entity_id;
const value = payload.state;

msg.payload = {
  measurement: "entity_state",
  tags: {
    entity_id: entity,
    domain: entity.split('.')[0]
  },
  fields: {
    value: isNaN(value) ? (value === "on" ? 1 : 0) : parseFloat(value)
  },
  timestamp: new Date(payload.last_changed).getTime() * 1000000
};

return msg;
```

---

## 5. 🌐 Exposer les entités via une API HTTP

### Créer un serveur Node.js:

```javascript
const mqtt = require('mqtt');
const express = require('express');

const app = express();
const client = mqtt.connect('mqtt://broker:1883');
const entityStates = {};

client.on('message', (topic, message) => {
  const payload = JSON.parse(message);
  entityStates[payload.entity_id] = payload;
});

client.subscribe('homeassistant/+/+/state');

app.get('/api/entities/:entity_id', (req, res) => {
  const entity = entityStates[req.params.entity_id];
  if (entity) {
    res.json(entity);
  } else {
    res.status(404).json({ error: 'Entity not found' });
  }
});

app.listen(3000);
```

---

## 6. 💾 Archiver l'historique dans une base de données

### Configuration PostgreSQL:

```yaml
automation:
  - alias: "Archiver température"
    trigger:
      - platform: time_pattern
        minutes: "/5"
    action:
      service: mqtt_entity_bridge.publish_entity
      data:
        entity_id: sensor.temperature_salon
      then:
        - service: shell_command.archive_to_db
          data:
            entity_id: sensor.temperature_salon
```

### Script Python pour archiver:

```python
import psycopg2
import json
from datetime import datetime

def archive_entity_state(entity_id: str, state_data: dict):
    conn = psycopg2.connect(
        host="localhost",
        database="homeassistant",
        user="ha_admin",
        password="password"
    )
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO entity_history (entity_id, state, attributes, timestamp)
        VALUES (%s, %s, %s, %s)
    """, (
        entity_id,
        state_data['state'],
        json.dumps(state_data['attributes']),
        state_data['last_updated']
    ))
    
    conn.commit()
    cur.close()
    conn.close()
```

---

## 7. 🔔 Notifications de changements critiques

### Automatisation:

```yaml
automation:
  - alias: "Alerter si température élevée"
    trigger:
      - platform: mqtt
        topic: "homeassistant/sensor/temperature/state"
    condition:
      - condition: template
        value_template: "{{ trigger.payload_json.state | float > 30 }}"
    action:
      - service: notify.telegram
        data:
          message: "⚠️ Température élevée: {{ trigger.payload_json.state }}°C"
```

---

## 8. 🎯 Scénarios multi-zone

### Configuration pour 3 étages:

```yaml
mqtt_entity_bridge:
  mqtt_host: "broker.local"
  topic_prefix: "smart_home"
  published_entities:
    # Rez-de-chaussée
    - light.rez_salon
    - light.rez_cuisine
    - switch.rez_clim
    
    # Premier étage
    - light.1er_chambre
    - light.1er_bureau
    
    # Deuxième étage
    - light.2e_chambre
    - sensor.2e_temperature
```

### Automatisation par zone:

```yaml
automation:
  - alias: "Lumières automatiques RDC au crépuscule"
    trigger:
      - platform: sun
        event: sunset
        offset: "-00:30:00"
    action:
      - repeat:
          count: 2
          sequence:
            - service: mqtt.publish
              data:
                topic: "smart_home/control/light/rez_{{ repeat.index }}/set"
                payload: '{"state":"on","brightness":200}'
```

---

## 9. 🏢 Mode bureau (Pas de présence)

Arrêter la synchronisation MQTT quand personne n'est à la maison:

```yaml
automation:
  - alias: "Arrêter sync MQTT absent"
    trigger:
      - platform: state
        entity_id: group.all_persons
        to: "not_home"
    action:
      - service: homeassistant.turn_off
        entity_id: switch.mqtt_sync

  - alias: "Relancer sync MQTT au retour"
    trigger:
      - platform: state
        entity_id: group.all_persons
        to: "home"
    action:
      - service: homeassistant.turn_on
        entity_id: switch.mqtt_sync
```

---

## 10. 🔄 Synchronisation bidirectionnelle sélective

Utiliser deux instances d'MQTT Entity Bridge avec préfixes différents:

```yaml
# Instance 1: Publier les lumières
group1:
  mqtt_host: "broker"
  topic_prefix: "ha1_to_ha2"
  published_entities:
    - light.salon

# Instance 2: Publier les capteurs
group2:
  mqtt_host: "broker"
  topic_prefix: "ha2_to_ha1"
  published_entities:
    - sensor.temperature
```

Cela crée une synchronisation :
- HA1 → HA2: Contrôler les lumières
- HA2 → HA1: Recevoir les températures

---

Ces cas d'usage montrent la flexibilité de **MQTT Entity Bridge** pour créer des systèmes domotiques complexes et bien intégrés!
