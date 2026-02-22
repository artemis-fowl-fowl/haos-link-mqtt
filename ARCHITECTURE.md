# Architecture & Structure - MQTT Entity Bridge

## 📁 Structure du projet

```
mqtt_entity_bridge/
├── custom_components/mqtt_entity_bridge/
│   ├── __init__.py                 # Composant principal (logique)
│   ├── config_flow.py              # Configuration UI et flux
│   ├── manifest.json               # Métadonnées de l'intégration
│   ├── strings.json                # Textes anglais pour l'UI
│   ├── test_init.py                # Tests unitaires
│   └── translations/
│       └── fr.json                 # Traductions français
│
├── README.md                        # Documentation principal
├── GUIDE_UTILISATION.md            # Guide complet utilisateur
├── CAS_USAGE_AVANCES.md            # Cas d'usage avancés
├── PAYLOAD_EXAMPLES.md             # Exemples de payloads MQTT
├── FAQ.md                          # Questions fréquentes
├── CHANGELOG.md                    # Historique des versions
├── LICENSE                         # Licence MIT
├── requirements.txt                # Dépendances Python
└── example_configuration.yaml      # Exemple de configuration
```

---

## 🏗️ Architecture générale

```
┌─────────────────────────────────────────────────┐
│         Home Assistant (Instance 1)              │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │     MQTT Entity Bridge Component        │   │
│  │                                         │   │
│  │  ┌──────────────────────────────────┐  │   │
│  │  │   Config Flow (Interface UI)     │  │   │
│  │  │  - MQTT Host/Port/User/Password  │  │   │
│  │  │  - Sélection des entités         │  │   │
│  │  └──────────────────────────────────┘  │   │
│  │              △                         │   │
│  │              │                         │   │
│  │  ┌──────────────────────────────────┐  │   │
│  │  │   Services (Logique principale)  │  │   │
│  │  │  - publish_entity                │  │   │
│  │  │  - publish_selected_entities     │  │   │
│  │  │  - update_published              │  │   │
│  │  └──────────────────────────────────┘  │   │
│  │              △                         │   │
│  │              │                         │   │
│  │  ┌──────────────────────────────────┐  │   │
│  │  │   MQTTEntityBridge (Client)      │  │   │
│  │  │  - Gère connexion MQTT           │  │   │
│  │  │  - Publie les states             │  │   │
│  │  │  - Reçoit les commandes          │  │   │
│  │  │  - Gère les reconnexions         │  │   │
│  │  └──────────────────────────────────┘  │   │
│  └─────────────────────────────────────────┘  │
│              │                                │
└──────────────┼────────────────────────────────┘
               │
               │  paho-mqtt
               │  (TCP/IP)
               │
        ┌──────┴──────┐
        │  MQTT Broker │
        │  (Mosquitto) │
        └──────┬──────┘
               │
        ┌──────┴──────────────────────────────┐
        │                                      │
┌───────┴──────────────────┐        ┌─────────┴──────────────┐
│  Home Assistant (HA 2)   │        │  Autres Clients MQTT    │
│                          │        │  (Node-RED, HASS.io)    │
│  Reçoit les states via   │        │                         │
│  les topics MQTT         │        │  Peuvent contrôler via  │
│                          │        │  les topics control/     │
└──────────────────────────┘        └─────────────────────────┘
```

---

## 📊 Flow des données

### 1️⃣ Publication d'une entité

```
HA Entity State Change
         │
         ▼
   [Service Called]
   publish_entity(entity_id)
         │
         ▼
   [MQTTEntityBridge]
   async_publish_entity()
         │
         ▼
   [Format JSON]
   {entity_id, state, attributes, ...}
         │
         ▼
   [MQTT Client]
   publish(topic, payload, qos=1, retain=True)
         │
         ▼
   Topic: homeassistant/domain/object_id/state
   Broker MQTT reçoit
         │
         ▼
   Stocké en mémoire (retain)
         │
         ▼
   Broadcast aux autres clients MQTT
```

### 2️⃣ Contrôle d'une entité (entrante)

```
Client MQTT 
(HA 2 ou autre)
         │
         ▼
Topic: homeassistant/control/domain/object_id/set
Payload: {"state": "on", ...}
         │
         ▼
   MQTT Broker
   (Message retenu)
         │
         ▼
   [HA Component]
   _on_message Callback
         │
         ▼
   [Parse Topic]
   Extraire domain/object_id
         │
         ▼
   [Parse Payload]
   Extraire command/state/attributes
         │
         ▼
   [Domain Handler]
   light: turn_on/turn_off
   switch: turn_on/turn_off
   climate: set_temperature
         │
         ▼
   Entity State Changed
         │
         ▼
   Service appliqué
```

---

## 🔑 Composants clés

### `__init__.py` - Cœur du composant

| Fonction | Rôle |
|----------|------|
| `async_setup()` | Initialisation YAML |
| `async_setup_entry()` | Initialisation UI/ConfigFlow |
| `async_unload_entry()` | Nettoyage |
| `handle_publish_entity()` | Service pour publier 1 entité |
| `handle_publish_selected()` | Service pour publier selection |
| `handle_update_published()` | Mettre à jour la liste |

### `MQTTEntityBridge` - Client MQTT

| Méthode | Responsabilité |
|---------|-----------------|
| `async_connect()` | Établir connexion MQTT |
| `async_disconnect()` | Fermer la connexion |
| `async_publish_entity()` | Publier state d'une entité |
| `async_publish_all_entities()` | Publier toutes sélectionnées |
| `_on_connect()` | Callback connexion |
| `_on_message()` | Callback message entrant |
| `_handle_control_message()` | Traiter commandes |

### `config_flow.py` - Configuration UI

| Classe | Rôle |
|--------|------|
| `MQTTEntityBridgeConfigFlow` | Flux de configuration |
| `async_step_user()` | Première étape (MQTT) |
| `test_mqtt_connection()` | Tester la connexion |

---

## 🔄 Cycle de vie

```
Installation
    │
    ▼
Discovery via HACS
    │
    ▼
Config Entry créée
    │
    ▼
async_setup_entry() lancé
    │
    ├─ Créer MQTTEntityBridge
    │
    ├─ Enregistrer services
    │
    └─ async_connect()
        │
        ├─ Créer client MQTT
        │
        ├─ connect(host, port)
        │
        └─ Callback: _on_connect()
           └─ S'abonner aux topics control/#
    │
    ▼
Entité change → Appel service → Publier sur MQTT
    │
    ▼
MQTT Message reçu → _on_message() → Appliquer commande
    │
    ▼
Redémarrage HA
    │
    ▼
async_unload_entry()
    │
    └─ Fermer connexion MQTT
       └─ Cleanup des resources

```

---

## 📡 Topics MQTT utilisés

### Publication (Sortant/Publish)
```
homeassistant/{domain}/{object_id}/state
```

Exemples:
- `homeassistant/light/salon/state`
- `homeassistant/switch/garage/state`
- `homeassistant/sensor/temperature/state`

### Contrôle (Entrant/Subscribe)
```
homeassistant/control/{domain}/{object_id}/{command}
```

Exemples:
- `homeassistant/control/light/salon/set`
- `homeassistant/control/switch/garage/set`
- `homeassistant/control/light/cuisine/toggle`

### Abonnements
```
homeassistant/control/#
homeassistant/request/#
```

---

## 🔐 Gestion de l'état

L'entité publiée contient:

```json
{
  "entity_id": "light.salon",          // Identifiant HA
  "state": "on",                       // État actuel
  "attributes": {                      // Attributs supplémentaires
    "brightness": 200,
    "friendly_name": "Salon",
    "icon": "mdi:lightbulb",
    ...
  },
  "last_changed": "ISO8601",           // Dernier changement
  "last_updated": "ISO8601"            // Dernière mise à jour
}
```

Le broker MQTT:
- ✅ Stocke le message (retain=true)
- ✅ Le rediffuse aux nouveaux clients
- ✅ Permet la reconstruction de l'état après redémarrage

---

## ⚡ Améliorations possibles (Futures)

```
┌─ Optimisation performance
│  ├─ Cache local des états
│  ├─ Compression des payloads
│  └─ Throttling des publications
│
├─ Sécurité améliorée
│  ├─ SSL/TLS
│  ├─ Authentification token
│  └─ Chiffrement payloads
│
├─ Fonctionnalités
│  ├─ Discovery automatique
│  ├─ Mapping topics personnalisé
│  ├─ Templates dans les topics
│  └─ Statistiques MQTT
│
└─ Intégration
   ├─ WebSocket support
   ├─ HomeAssistant Discovery
   └─ REST API
```

---

## 🧪 Tests

Tests actuels dans `test_init.py`:
- `test_async_setup_with_config`
- `test_async_setup_without_config`
- `test_async_setup_entry`

Pour lancer les tests:
```bash
pytest custom_components/mqtt_entity_bridge/test_init.py -v
```

---

## 📚 Patterns et conventions

### Naming conventions
- Fichiers: `snake_case` (config_flow.py)
- Classes: `PascalCase` (MQTTEntityBridge)
- Fonctions: `snake_case` (async_publish_entity)
- Constantes: `UPPER_SNAKE_CASE` (DOMAIN)

### Code style
- Type hints partout
- Async/await pour les opérations longues
- Try/except pour les erreurs de connexion
- Logging systématique

### Home Assistant patterns
- `hass.data[DOMAIN]` pour le stockage
- `.get()` pour accès sécurisé
- Services enregistrés avec `async_register`
- Callbacks pour les événements

---

**Dernière mise à jour**: 2026-02-22
