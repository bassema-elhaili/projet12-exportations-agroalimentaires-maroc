# Journal des contributions

Ce document accompagne le rapport (annexe B) et sert à décrire la répartition
réelle du travail dans le binôme. Il doit être **rempli et signé par les deux
étudiants** avant la remise : les cases ci-dessous sont volontairement vides,
aucune contribution ne doit être inventée.

## 1. Répartition par tâche

Cocher la ou les personnes ayant réalisé chaque tâche. Une tâche peut être
partagée ; dans ce cas, préciser la nature de la contribution dans la colonne
« Détail ».

| # | Tâche | Étudiant 1 | Étudiant 2 | Détail / preuve |
|---|-------|:----------:|:----------:|-----------------|
| 1 | Cadrage, question de recherche, lecture de la fiche projet | ☐ | ☐ | |
| 2 | Extraction UN Comtrade et journal des requêtes | ☐ | ☐ | |
| 3 | Nettoyage, dictionnaire de produits, construction du panel | ☐ | ☐ | |
| 4 | Analyse exploratoire et figures 1 à 5 | ☐ | ☐ | |
| 5 | Modélisation, validation glissante, test final | ☐ | ☐ | |
| 6 | Tests de sensibilité et analyse des erreurs | ☐ | ☐ | |
| 7 | Rédaction LaTeX du rapport et bibliographie | ☐ | ☐ | |
| 8 | Support de soutenance et répétition | ☐ | ☐ | |

## 2. Répartition du temps (à titre indicatif)

| Activité | Étudiant 1 (h) | Étudiant 2 (h) |
|---|---:|---:|
| Recherche et cadrage | | |
| Données et code | | |
| Analyse et modèles | | |
| Rédaction | | |
| Soutenance | | |
| **Total** | | |

## 3. Points de vigilance méthodologique

Ces points ont été discutés en binôme et validés ensemble ; ils peuvent être
cités en soutenance pour montrer la maîtrise du protocole.

1. **Pas de fuite temporelle** : toutes les variables explicatives sont
   disponibles à la fin de l'année *t* ; la cible est *t+1*. Le
   préprocesseur est réajusté dans chaque fenêtre de validation.
2. **Zéros imputés** : le Maroc est l'unique déclarant, donc une cellule
   absente est interprétée comme un flux nul. L'indicateur `declare` permet
   de tester cette hypothèse (scénario S1).
3. **Choix des hyperparamètres** : réalisé uniquement sur la validation
   glissante 2016–2022, jamais sur le test 2023–2024.
4. **Résultat négatif assumé** : la persistance n'est battue de façon
   robuste par aucun modèle ; le gain de la forêt aléatoire sur le test
   (2,9 %) disparaît en validation. Ce n'est pas un échec, c'est le résultat
   à expliquer.

## 4. Signatures

| | Nom | Date | Signature |
|---|---|---|---|
| Étudiant 1 | | | |
| Étudiant 2 | | | |

---

*Modèle à conserver dans le dépôt ; la version signée peut être exportée en
PDF et jointe au rapport.*
