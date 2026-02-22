# Exemples de Payloads MQTT

## 1. État d'une lumière

**Topic**: `homeassistant/light/salon/state`

```json
{
  "entity_id": "light.salon",
  "state": "on",
  "attributes": {
    "brightness": 200,
    "color_temp": 370,
    "friendly_name": "Salon",
    "icon": "mdi:lightbulb",
    "entity_picture": null,
    "supported_color_modes": ["color_temp", "xy"],
    "color_mode": "color_temp",
    "min_mireds": 153,
    "max_mireds": 500
  },
  "last_changed": "2026-02-22T14:30:45.123456+00:00",
  "last_updated": "2026-02-22T14:30:45.123456+00:00"
}
```

---

## 2. État d'un switch (prise)

**Topic**: `homeassistant/switch/garage/state`

```json
{
  "entity_id": "switch.garage",
  "state": "off",
  "attributes": {
    "friendly_name": "Garage",
    "icon": "mdi:power-socket",
    "device_class": "outlet",
    "assumed_state": false
  },
  "last_changed": "2026-02-22T10:15:22.456789+00:00",
  "last_updated": "2026-02-22T10:15:22.456789+00:00"
}
```

---

## 3. État d'un capteur de température

**Topic**: `homeassistant/sensor/temperature_salon/state`

```json
{
  "entity_id": "sensor.temperature_salon",
  "state": "22.5",
  "attributes": {
    "friendly_name": "Température Salon",
    "unit_of_measurement": "°C",
    "icon": "mdi:thermometer",
    "device_class": "temperature",
    "state_class": "measurement"
  },
  "last_changed": "2026-02-22T14:25:10.789012+00:00",
  "last_updated": "2026-02-22T14:30:05.456789+00:00"
}
```

---

## 4. État d'un verrouillage de porte

**Topic**: `homeassistant/lock/porte_principale/state`

```json
{
  "entity_id": "lock.porte_principale",
  "state": "locked",
  "attributes": {
    "friendly_name": "Porte Principale",
    "icon": "mdi:lock",
    "code_format": "^\\d{4}$",
    "changed_by": "Pierre",
    "battery_level": 85
  },
  "last_changed": "2026-02-22T08:00:00.000000+00:00",
  "last_updated": "2026-02-22T16:30:45.123456+00:00"
}
```

---

## 5. État d'une climatisation

**Topic**: `homeassistant/climate/salon/state`

```json
{
  "entity_id": "climate.salon",
  "state": "heat",
  "attributes": {
    "friendly_name": "Climat Salon",
    "current_temperature": 22.3,
    "target_temperature": 21,
    "min_temp": 16,
    "max_temp": 30,
    "hvac_modes": ["off", "heat", "cool", "heat_cool"],
    "hvac_action": "heating",
    "preset_modes": ["none", "eco", "comfort", "sleep"],
    "preset_mode": "comfort",
    "icon": "mdi:thermostat"
  },
  "last_changed": "2026-02-22T10:00:00.000000+00:00",
  "last_updated": "2026-02-22T14:32:15.678901+00:00"
}
```

---

## 6. État d'une porte/fenêtre

**Topic**: `homeassistant/binary_sensor/porte_salon/state`

```json
{
  "entity_id": "binary_sensor.porte_salon",
  "state": "off",
  "attributes": {
    "friendly_name": "Porte Salon",
    "device_class": "door",
    "icon": "mdi:door-open",
    "battery_level": 92,
    "last_triggered": "2026-02-22T15:00:00.000000+00:00"
  },
  "last_changed": "2026-02-22T15:00:05.123456+00:00",
  "last_updated": "2026-02-22T15:00:05.123456+00:00"
}
```

---

## 7. Envoi de commandes

### Allumer une lumière avec couleur

**Topic**: `homeassistant/control/light/cuisine/set`

```json
{
  "state": "on",
  "brightness": 255,
  "color_temp": 400,
  "rgb_color": [255, 200, 150]
}
```

### Éteindre un switch

**Topic**: `homeassistant/control/switch/garage/set`

```
off
```

### Ou avec JSON:

```json
{
  "state": "off"
}
```

### Ajuster chauffage

**Topic**: `homeassistant/control/climate/salon/set`

```json
{
  "temperature": 20,
  "hvac_mode": "heat",
  "preset_mode": "eco"
}
```

### Verrouiller une porte

**Topic**: `homeassistant/control/lock/porte_principale/set`

```json
{
  "action": "lock",
  "code": "1234"
}
```

---

## Notes importantes

- Les payloads sont toujours en **JSON valide** (sauf les simples on/off)
- Les timestamps sont en **ISO 8601**
- Les states comme `on`/`off` peuvent être des strings simples pour certains équipements
- Les `attributes` contiennent des informations supplémentaires comme:
  - `friendly_name`: Nom affiché
  - `icon`: Icône MaterialDesignIcon
  - `unit_of_measurement`: Unité (°C, %, etc.)
  - `device_class`: Type de capteur

---

## Variables de template disponibles

Dans les automatisations, vous pouvez utiliser:

```yaml
entity_id: "{{ trigger.payload_json.entity_id }}"
state: "{{ trigger.payload_json.state }}"
brightness: "{{ trigger.payload_json.attributes.brightness }}"
friendly_name: "{{ trigger.payload_json.attributes.friendly_name }}"
```
