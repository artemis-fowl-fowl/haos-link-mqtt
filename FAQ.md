# FAQ - Questions Fréquemment Posées

## Installation & Configuration

### **Q: Où trouver l'adresse IP du broker MQTT?**
**R**: 
- Si Mosquitto est sur la même HA: `homeassistant.local` ou l'IP locale de HA
- Vérifier dans **Paramètres** → **Modules complémentaires** → **Mosquitto**
- Ou utiliser: `mosquitto.local` (si mDNS est actif)

### **Q: Quel port MQTT utiliser?**
**R**: 
- Par défaut: `1883` (non chiffré)
- SSL/TLS: `8883` (chiffré)

### **Q: Comment obtenir les identifiants MQTT?**
**R**:
Si vous utilisez le module Mosquitto de Home Assistant:
1. Aller à **Paramètres** → **Modules complémentaires** → **Mosquitto**
2. Voir les identifiants configurés
3. Utiliser les mêmes dans MQTT Entity Bridge

### **Q: Puis-je utiliser un broker MQTT externe?**
**R**: 
Oui, absolument!
- Cloud MQTT (gratuit pour petits usages)
- Adresse: `[instance].mq.cloud.ibm.com`
- Port: `1883`

### **Q: MQTT Entity Bridge nécessite-t-il une configuration YAML?**
**R**: 
Non, il est complètement configurable via l'interface HA.
La configuration YAML est optionnelle pour avancés.

---

## Utilisation & Fonctionnalités

### **Q: Quelle est la différence entre "publish" et "control"?**
**R**:
- **Publish** (publier): Envoyer l'état d'une entité sur MQTT
  - Topic: `homeassistant/light/salon/state`
  - Direction: HA → MQTT (sortante)

- **Control** (contrôle): Recevoir une commande et l'appliquer
  - Topic: `homeassistant/control/light/salon/set`
  - Direction: MQTT → HA (entrante)

### **Q: Comment publier seulement certaines entités?**
**R**:
```yaml
service: mqtt_entity_bridge.publish_entity
data:
  entity_id: light.salon
```

Ou avec une automatisation pour plusieurs:
```yaml
automation:
  trigger: state
  entity_id:
    - light.salon
    - light.cuisine
  action:
    service: mqtt_entity_bridge.publish_entity
    data:
      entity_id: "{{ trigger.entity_id }}"
```

### **Q: Puis-je renommer les topics MQTT?**
**R**:
Oui, avec le `topic_prefix` dans la configuration:

```yaml
mqtt_entity_bridge:
  topic_prefix: "ma_maison"  # Topics seront: ma_maison/light/salon/state
```

### **Q: Comment mettre à jour un état sans contrôler l'appareil?**
**R**:
Les entités publiées sont en **lecture seule** par défaut.
Pour les contrôler, envoyer un message sur le topic `control/`:

```
Topic: homeassistant/control/switch/garage/set
Payload: on
```

### **Q: Peut-on publier les mêmes entités sur deux topics différents?**
**R**:
Techniquement oui en utilisant deux instances, mais c'est complexe.
Pour la plupart des cas, un seul broker MQTT suffit.

### **Q: À quelle fréquence les entités sont-elles publiées?**
**R**:
- À la demande: Immédiatement via `publish_entity`
- Automatiquement: Quand l'état change (si configuré)
- Au démarrage: Une seule fois avec `publish_selected_entities`

### **Q: Comment publier les entités automatiquement quand elles changent?**
**R**:
```yaml
automation:
  - alias: "Republier automatiquement"
    trigger:
      platform: state
      entity_id: 
        - light.salon
        - switch.garage
    action:
      service: mqtt_entity_bridge.publish_entity
      data:
        entity_id: "{{ trigger.entity_id }}"
```

---

## Dépannage & Performance

### **Q: Je vois "Erreur de connexion MQTT" - Pourquoi?**
**R**:
1. Vérifier que le broker MQTT fonctionne
2. Vérifier les identifiants (username/password)
3. Vérifier l'IP et le port
4. Vérifier les pare-feu (port 1883 ouvert?)

### **Q: Les topics MQTT ne contiennent pas toutes les infos, comment les ajouter?**
**R**:
Les attributs sont inclus dans le payload JSON:
```json
{
  "state": "on",
  "attributes": {
    "brightness": 200,
    "friendly_name": "Salon",
    ...
  }
}
```

Pour extraire en Node-RED:
```javascript
msg.brightness = msg.payload.attributes.brightness;
return msg;
```

### **Q: Comment surveiller les publications?**
**R**:
Utiliser **MQTT Explorer**:
1. Connecter au broker MQTT
2. Chercher le topic: `homeassistant/#`
3. Vérifier que les messages arrivent

### **Q: Combien d'entités puis-je publier?**
**R**:
Théoriquement illimité, mais considérer:
- Bande passante MQTT (utilisée)
- Stockage du broker (si `retain: true`)
- Performance HA (si republication fréquente)

Recommandation: < 100 entités par instance

### **Q: Quel est l'impact sur la performance?**
**R**:
- Minime: Les publications sont asynchrones
- Connexion MQTT: ~1% CPU max
- Bande passante: ~5-10 kbps (selon fréquence)

### **Q: Les messages MQTT sont-ils conservés?**
**R**:
Oui, si `retain: true`. Cela signifie:
- ✅ Les nouveaux clients reçoivent l'état au connexion
- ⚠️ Le broker stocke les messages (espace disque)
- ✅ C'est activé par défaut dans Bridge

### **Q: Comment désactiver le retain?**
**R**:
Actuellement, le retain est activé par défaut.
Pour le désactiver, modifier `__init__.py`:
```python
self.client.publish(topic, json.dumps(payload), qos=1, retain=False)
```

---

## Cas spécifiques

### **Q: Comment lier deux Home Assistant?**
**R**:
1. Installer MQTT Entity Bridge sur les deux
2. Configurer le même broker MQTT sur les deux
3. Sur HA1: Publier les entités à partager
4. Sur HA2: Les recevoir automatiquement

### **Q: Comment contrôler HA2 depuis HA1?**
**R**:
```yaml
# HA1: Automatisation pour envoyer la commande
automation:
  - trigger: state
    entity_id: light.salon_ha1
    action:
      service: mqtt.publish
      data:
        topic: "homeassistant/control/light/salon/set"
        payload: |
          {
            "state": "{{ states('light.salon_ha1') }}"
          }
```

### **Q: Comment synchroniser bidirectionnellement?**
**R**:
```yaml
# HA1 publie ses lumières
# HA2 publie ses capteurs

# HA1 écoute les topics HA2 et crée des entities
# HA2 écoute les topics HA1 et crée des entities
```

### **Q: Peut-on créer des entités virtuelles depuis MQTT?**
**R**:
Non directement, mais on peut utiliser:
- **MQTT Sensor** natif de HA
- **NodeRed** + **Template entities**
- **Automation** pour créer des virtual_device

### **Q: Comment faire une UI partagée?**
**R**:
Utiliser un tableau de bord avec des cartes MQTT:
```yaml
type: custom:apexcharts-card
title: Maisons
entities:
  - entity: sensor.ha1_temperature
  - entity: sensor.ha2_temperature
```

---

## Sécurité & Avancé

### **Q: Comment sécuriser la connexion MQTT?**
**R**:
1. Utiliser SSL/TLS (port 8883)
2. Utiliser des identifiants forts
3. Configurer ACLs côté Mosquitto
4. Utiliser VPN pour la distance

### **Q: Comment chiffrer les messages?**
**R**:
MQTT n'a pas de chiffrement natif.
Solutions:
- SSL/TLS au niveau du broker
- VPN pour la transmission
- Chiffrer les payloads avant de publier (avancé)

### **Q: Peut-on utiliser des wildcard MQTT?**
**R**:
Oui, mais limitiement dans Bridge.
Pour des cas complexes, utiliser Node-RED.

### **Q: Comment monitorer MQTT Entity Bridge?**
**R**:
Vérifier dans les logs:
```yaml
logger:
  logs:
    custom_components.mqtt_entity_bridge: debug
```

Ou utiliser MQTT Explorer pour voir les topics.

### **Q: Puis-je exposer MQTT sur Internet?**
**R**:
❌ **Non recommandé**! 
✅ Mieux: Utiliser VPN ou Nginx reverse proxy

### **Q: Comment faire une sauvegarde/restauration?**
**R**:
Les configurations sont stockées dans:
`.homeassistant/.storage/mqtt_entity_bridge`

Pour sauvegarder:
```bash
cp -r .homeassistant/.storage/mqtt_entity_bridge ./backup/
```

---

## Support & Contribution

### **Q: Comment rapporter un bug?**
**R**:
1. Ouvrir une issue sur GitHub
2. Inclure les logs de debug
3. Décrire la configuration (sans passwords)
4. Expliquer la reproduction

### **Q: Comment contribuer?**
**R**:
1. Fork le repository
2. Créer une branche (`git checkout -b feature/ma-feature`)
3. Commiter (`git commit -am 'Add feature'`)
4. Push (`git push origin feature/ma-feature`)
5. Ouvrir une Pull Request

### **Q: Y a-t-il d'autres extensions similaires?**
**R**:
- **Node-RED**: Plus flexible
- **AppDaemon**: Pour l'automatisation avancée
- **Home Assistant Cloud**: Solution propriétaire
- **Zwave/Zigbee Gateway**: Pour des protocoles spécifiques

### **Q: Où trouver de l'aide?**
**R**:
- [Community HA Forums](https://community.home-assistant.io/)
- [GitHub Issues](https://github.com/mqtt_entity_bridge/)
- [Discord HA Community](https://discord.gg/home-assistant)

---

**Dernière mise à jour**: 2026-02-22
