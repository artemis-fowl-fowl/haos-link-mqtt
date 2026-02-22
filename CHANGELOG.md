# CHANGELOG

## [1.0.0] - 2026-02-22

### ✨ Nouvelles fonctionnalités
- ✅ Configuration initiale via interface Home Assistant
- ✅ Service pour publier une entité individuelle
- ✅ Service pour publier toutes les entités sélectionnées
- ✅ Support du contrôle bidirectionnel via MQTT
- ✅ Gestion automatique de la connexion/reconnexion MQTT
- ✅ Support des lumières, switches, capteurs, climatisation
- ✅ Payloads JSON complètes avec attributs
- ✅ Configuration YAML optionnelle
- ✅ Logs de débogage intégrés
- ✅ Interface de configuration avec test de connexion

### 🔧 Améliorations techniques
- Utilisation de `paho-mqtt` pour la stabilité
- Architecture asynchrone (async/await)
- Support de la reconnexion automatique
- Gestion des erreurs robuste
- Code bien structuré et commenté

### 📚 Documentation
- README complet en français
- Guide d'utilisation détaillé
- Cas d'usage avancés
- Exemples de payloads MQTT
- FAQ complet
- Commentaires dans le code

### 🐛 Corrections de bugs
- N/A (première version)

---

## Versions futures

### [1.1.0] - Planifié
- [ ] Support du chiffrement SSL/TLS
- [ ] Éditeur visuel pour sélectionner les entités
- [ ] Historique des communications MQTT
- [ ] Notifications de déconnexion/reconnexion
- [ ] Mode découverte automatique des brokers MQTT

### [1.2.0] - Planifié
- [ ] Filtres avancés pour les entités
- [ ] Mapping personnalisé des topics
- [ ] Support des templates dans les topics
- [ ] Cache des derniers états
- [ ] Statistiques de bande passante

### [2.0.0] - Vision long terme
- [ ] Support complet HomeAssistant Discovery
- [ ] Dashboard personnalisé dans HA
- [ ] Migration vers websockets (plus rapide)
- [ ] Support des entités personnalisées
- [ ] Interface web indépendante

---

## Notes de migration

### De 0.x vers 1.0.0
- Première version majeure
- Pas de breaking changes (N/A)
- Nouvelle installation recommandée

---

## Dépendances

### Mises à jour requises
- `paho-mqtt` >= 1.6.1
- `voluptuous` >= 0.12.2
- Home Assistant >= 2023.1.0

### Dépendances optionnelles
- Node-RED (pour l'automatisation avancée)
- MQTT Explorer (pour le débogage)

---

## Supporters & Contributeurs

Merci à tous ceux qui ont aidé:
- Community Home Assistant
- Testeurs et bêta-testeurs
- Contributeurs GitHub

---

## Support des versions

| Version | Statut | Fin du support |
|---------|--------|-----------------|
| 1.0.0   | 🟢 Stable | 2027-02-22 |
| 0.x     | ❌ EOL | EOL |

---

## Roadmap public

```
2026-02
├─ v1.0.0: Version initiale stable
│
2026-04
├─ v1.1.0: SSL/TLS + UI améliorée
│
2026-06
├─ v1.2.0: Filtres avancés
│
2026-12
└─ v2.0.0: Refactorisation majeure
```

---

## Feedback & Suggestions

Pour suggérer une nouvelle fonctionnalité:
1. Ouvrir une issue GitHub avec le tag `enhancement`
2. Décrire le use case
3. Expliquer les bénéfices

Merci pour vos retours!

---

**Dernière mise à jour**: 2026-02-22
