# 🚀 Installation rapide - 5 minutes

Suivez ce guide pour configurer **MQTT Entity Bridge** en moins de 5 minutes.

---

## ✅ Prérequis

- ✔ Home Assistant installé et fonctionnelz
- ✔ HACS installé ([guide](https://hacs.xyz/docs/setup/prerequisites))
- ✔ **Un broker MQTT actif**:
  - Mosquitto sur HA (module complémentaires)
  - Ou un autre broker MQTT avec IP/port/identifiants

---

## 📋 Étapes

### 1️⃣ Installer via HACS (1 min)

```
HACS → Intégrations
  ↓
⋮ (menu) → Dépôts personnalisés
  ↓
URL: https://github.com/mqtt_entity_bridge
  ↓
Chercher: "MQTT Entity Bridge"
  ↓
Cliquer: [Installer]
  ↓
Redémarrer Home Assistant (3 min)
```

### 2️⃣ Configurer (2 min)

```
Paramètres → Appareils et services → [+ Créer]
  ↓
Chercher: "MQTT Entity Bridge"
  ↓
Entrer:
  - Host: 192.168.1.100 (ou mosquitto.local)
  - Port: 1883
  - User: mqtt_user
  - Password: mqtt_password
  ↓
[Soumettre]
```

**Besoin d'aide pour les identifiants MQTT?**
```
Paramètres → Modules complémentaires → Mosquitto
```

---

## 🎯 Test rapide (1 min)

### Publier une entité

```yaml
service: mqtt_entity_bridge.publish_entity
data:
  entity_id: light.salon
```

### Vérifier avec MQTT Explorer

1. Télécharger: [MQTT Explorer](http://mqtt-explorer.com/)
2. Connecter au même broker MQTT
3. Chercher: `homeassistant/light/salon/state`
4. ✅ Vous devriez voir l'état!

---

## 🔌 Connecter un 2e Home Assistant

### Sur HA 2:
1. Répéter les étapes 1️⃣ et 2️⃣
2. **Même broker MQTT** que HA 1
3. Configuration identique

### Résultat:
```
HA 1 publie → MQTT ← HA 2 reçoit
HA 2 publie → MQTT ← HA 1 reçoit
```

---

## ⚡ Automatisations courantes

### Publier automatiquement au démarrage

Dans **Paramètres** → **Automatisations** → **[Créer]**:

```yaml
alias: "HA: Publier sur MQTT au démarrage"
trigger:
  - platform: homeassistant
    event: start
action:
  - service: mqtt_entity_bridge.publish_selected_entities
```

### Republier quand change

```yaml
alias: "HA: Republier lumière"
trigger:
  - platform: state
    entity_id: light.salon
action:
  - service: mqtt_entity_bridge.publish_entity
    data:
      entity_id: "{{ trigger.entity_id }}"
```

---

## 🆘 Problèmes courants

### ❌ "Impossible de se connecter"

1. Vérifier l'IP: `ping mosquitto.local`
2. Vérifier les identifiants
3. Voir les logs:
   ```yaml
   logger:
     logs:
       custom_components.mqtt_entity_bridge: debug
   ```

### ❌ Pas de topics MQTT

1. Vérifier la connexion est ok
2. Lancer le service `publish_entity`
3. Ouvrir MQTT Explorer
4. Chercher `homeassistant/`

### ❌ Rien ne marche?

**Diagnostic complet**:

1. **HA 1 - Logs**:
   ```
   Paramètres → Système → Journaux (chercher: mqtt_entity_bridge)
   ```

2. **Tester MQTT**:
   - Télécharger MQTT Explorer
   - Connecter avec mêmes identifiants
   - Voir les topics

3. **Vérifier le service**:
   ```yaml
   service: mqtt_entity_bridge.publish_entity
   data:
     entity_id: light.salon
   ```

---

## 📚 Prochaines étapes

- 📖 [Guide complet](GUIDE_UTILISATION.md) - Tout détail
- 🎯 [Cas avancés](CAS_USAGE_AVANCES.md) - Scénarios complexes
- ❓ [FAQ](FAQ.md) - Questions courantes
- 💬 [Architecture](ARCHITECTURE.md) - Pour developpeurs

---

## 💡 Astuces

| Astuce | Bénéfice |
|--------|----------|
| Créer une **automatisation globale** | Republier toutes les entités automatiquement |
| Utiliser **Node-RED** avec MQTT | Automatisations complexes |
| **MQTT Explorer** pour déboguer | Voir les topics en temps réel |
| Configurer **plusieurs préfixes** | Organiser les topics |
| Lier **3+ maisons** | Domotique distribuée |

---

## ✨ Félicitations!

Votre pont MQTT est configuré! 🎉

**Résumé fait**:
- ✅ Installé MQTT Entity Bridge
- ✅ Connecté au broker MQTT
- ✅ Publié une entité
- ✅ Testé avec MQTT Explorer

**Maintenant**:
- Lier d'autres entités
- Créer des automatisations
- Relier d'autres HA
- Intégrer Node-RED

---

**Besoin d'aide?**
- 📖 Docs: [README.md](README.md)
- ❓ FAQ: [FAQ.md](FAQ.md)
- 🐛 Issues: GitHub Issues
- 💬 Forum: Home Assistant Community

Bon amusement! 🚀
