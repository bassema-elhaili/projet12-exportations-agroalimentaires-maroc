# Rapport de réalisation — Projet 12

**Exportations agroalimentaires marocaines : prévoir les ventes de fruits par marché**

- **Périmètre** : chaîne complète, de l'extraction UN Comtrade à la soutenance.
- **Base de travail** : pack de Bassma (`Guide_Binomes_14_Jours (1).pdf`,
  `README.pdf`, `requirements.pdf`, `rapport_projet_template.tex`,
  `Template_Projet_DataScience_Colab.ipynb`) et fiche projet n° 12.
- **Principe** : aucune donnée inventée ; tous les chiffres proviennent de
  l'API UN Comtrade et sont tracés.

---

## 1. Objectif

Répondre à la question : *peut-on prévoir à un an la valeur exportée d'un
couple (marché, produit), et les modèles d'apprentissage automatique battent-ils
une simple reconduction de l'année précédente ?*

Contraintes de la fiche : Maroc (504), exportations, France (251) et Espagne
(724), chapitre HS 08, 2010–2024, API *preview* de Comtrade, régression,
baseline + au moins deux modèles, validation temporelle, au moins cinq figures
commentées, rapport LaTeX de 10 à 15 pages, soutenance de 8 à 10 minutes.

---

## 2. Ce qui a été produit

| Livrable | Fichier | Contenu |
|---|---|---|
| Rapport | `rapport/rapport.pdf` | 15 pages, 8 figures, 10 tableaux, bibliographie, annexes |
| Source LaTeX | `rapport/rapport.tex` | document complet recompilable |
| Notebook | `notebooks/projet12_exportations_agroalimentaires.ipynb` | 49 cellules, 23/23 cellules de code exécutées, 8 figures intégrées |
| Extraction | `src/download_comtrade.py` | 45 requêtes, JSON bruts + journal |
| Préparation | `src/prepare_data.py` | panel, séries, table qualité (règles R1–R4) |
| Données | `data/raw/`, `data/processed/` | 1 058 lignes brutes, panel de 1 260 lignes |
| Figures | `figures/fig01` … `fig08` | PNG 200 dpi, palette accessible |
| README | `README.md` | structure, installation, exécution, résultats, limites |
| Dépendances | `requirements.txt` | versions épinglées |
| Soutenance | `soutenance/soutenance.pdf` | 15 diapositives beamer, 8–10 min |
| Annexes | `docs/journal_des_contributions.md`, `docs/declaration_ia.md` | à signer |
| Licence | `LICENSE` | MIT (code) + CC BY 4.0 (texte, figures) |
| Archive | `projet12-exportations-agroalimentaires-maroc.zip` | 4,13 Mo, 80 fichiers |

---

## 3. Déroulé du travail

### 3.1 Cadrage

- Lecture du guide, du template LaTeX et de la fiche projet 12.
- Reformulation de la question de recherche et des hypothèses H1–H3.
- Choix d'étendre le panel de 2 à 6 marchés européens (France, Espagne,
  Allemagne, Pays-Bas, Royaume-Uni, Italie) et de 2 à 14 positions HS4
  (0801–0814) pour obtenir un échantillon modélisable.
- Décision de traiter le problème comme une régression temporelle, avec
  validation glissante et test final isolé.

### 3.2 Acquisition des données

- Interrogation de l'API publique *preview* de UN Comtrade
  (`/public/v1/preview/C/A/HS`), sans clé.
- 45 requêtes : 15 années × 3 extractions (panel marchés, agrégats monde HS2,
  agrégats monde HS4).
- 1 058 lignes brutes, **0 échec**, journal complet
  (`data/processed/journal_extractions.csv`) avec URL, statut, nombre de
  lignes et horodatage.
- Sauvegarde de chaque réponse JSON dans `data/raw/` pour la traçabilité.

### 3.3 Préparation

- Panel final : 6 marchés × 14 produits × 15 ans = **1 260 lignes**.
- **834 cellules observées (66,2 %)**, 426 zéros imputés avec l'indicateur
  `declare` (1 = observé, 0 = imputé).
- **9 produits retenus sur 14** (couverture ≥ 50 %) : 0802, 0804, 0805, 0806,
  0807, 0809, 0810, 0811, 0814.
- **648 observations modélisables** après construction des retards.
- Séries agrégées et table de qualité produites dans `data/processed/`.

### 3.4 Analyse exploratoire

Cinq figures commentées, puis trois figures de modélisation :

1. dynamique agrégée 2010–2024 et part des six marchés ;
2. structure par produit (composition et valeur 2024) ;
3. dynamique par marché (heatmap et taille/croissance) ;
4. agrumes : valeur et prix implicite ;
5. concentration : indice de Herfindahl et top 8 des couples ;
6. prévisions contre réalisations et WAPE ;
7. importance par permutation ;
8. projection 2025 avec intervalle à 80 %.

### 3.5 Modélisation

- Cible : valeur en *t+1*, modélisée en `log1p`, reconstruite par `expm1`.
- Variables strictement connues fin *t* : retards *t*, *t−1*, *t−2*, *t−3*,
  moyennes passées, part de marché, croissance mondiale.
- Découpage :
  - entraînement *t* ≤ 2019 (cibles 2011–2020) ;
  - validation glissante à 6 fenêtres *expanding* (2016→2017 … 2021→2022) ;
  - test final *t* = 2022–2023 (cibles 2023–2024, 108 observations).
- Modèles : persistance (référence), Ridge (α = 100), forêt aléatoire
  (600 arbres, feuille 15, `max_features = 0,5`), gradient boosting
  (perte absolue, taux 0,02, 200 itérations).
- Préprocesseur dans un `Pipeline` réajusté à chaque fenêtre, avec
  `clone()` pour éviter toute fuite.
- Tests de sensibilité : S1 sans zéros imputés, S2 test élargi 2020–2024,
  S3 sans le produit dominant 0810.
- Projection 2025 avec intervalle empirique à 80 % construit sur un backtest
  roulant 2014–2024.

### 3.6 Rédaction et soutenance

- Rapport structuré : résumé, introduction, données, analyse, méthodologie,
  résultats, discussion, conclusion, annexes.
- Tableaux de synthèse : extraction, variables, qualité, hyperparamètres,
  performances, erreurs par marché et par produit, sensibilité, projection,
  reproductibilité, contributions.
- Bibliographie (Comtrade, Banque mondiale, OMC, scikit-learn, Hyndman,
  Makridakis).
- Support beamer de 15 diapositives, construit sur les mêmes chiffres, avec
  un enchaînement question → données → constats → méthode → résultats →
  robustesse → conclusion.

---

## 4. Choix méthodologiques assumés

1. **Six marchés au lieu de deux.** La fiche impose la France et l'Espagne ;
   les quatre autres marchés européens portent l'échantillon d'environ 200 à
   648 observations. Le couple France–Espagne reste analysé séparément.
2. **Zéros imputés.** Le Maroc est l'unique déclarant : une cellule absente
   signifie « aucun flux enregistré ». L'hypothèse est documentée et testée
   en sensibilité (S1).
3. **Produits écartés.** Les produits présents dans moins de 50 % des cellules
   sont exclus de la modélisation mais conservés dans les fichiers.
4. **Aucune fuite temporelle.** Toutes les variables sont connues fin *t* ;
   le test final n'est utilisé qu'une fois.
5. **Résultat négatif présenté tel quel.** La persistance reste le benchmark
   de référence ; aucun modèle ne la bat de façon robuste.

---

## 5. Résultats principaux

### Dynamique et structure

- **1 607,6 M USD** exportés vers les six marchés en 2024, contre 325,6 M USD
  en 2010 : **×4,9**, TCAM de **12,1 %**.
- **75,6 %** des exportations du chapitre 08 vont vers ces six marchés en 2024
  (moyenne 2010–2024 : 66,8 %).
- Produits 2024 : 0810 autres fruits frais **61,0 %**, 0804 dattes/avocats
  **13,9 %**, 0805 agrumes **9,8 %**.
- Marchés 2024 : Espagne 415,6 M USD (TCAM 19,3 %), Royaume-Uni 390,9
  (17,7 %), Pays-Bas 322,6 (9,9 %), France 313,5 (5,8 %), Allemagne 149,0
  (17,1 %), Italie 15,9 (7,9 %).
- Agrumes : prix implicite **0,73 → 1,06 USD/kg** (+45 %), croissance
  surtout en valeur, pas en volume.
- Concentration : Herfindahl **6 388 → 5 042** ; les trois premiers couples
  pèsent **49,2 %** de la valeur.

### Modèles

| Modèle | WAPE validation | WAPE test | MASE vs persistance |
|---|---:|---:|---:|
| Persistance | **0,297** | 0,262 | 1,000 |
| Ridge | 0,381 | 0,395 | 1,506 |
| Forêt aléatoire | 0,314 | **0,255** | **0,971** |
| Gradient boosting | 0,314 | 0,295 | 1,125 |

- La forêt aléatoire gagne **2,9 %** sur le test, mais perd en validation
  glissante : le gain n'est **pas robuste**.
- Les gains se concentrent sur l'Espagne, les Pays-Bas et le Royaume-Uni ;
  la persistance reste meilleure sur la France, l'Allemagne et l'Italie.
- Sensibilité : S1 (0,253), S2 (0,297 vs 0,308), S3 (0,298 vs 0,288) —
  l'ordre des modèles change selon le scénario.
- Projection 2025 : **1 771,3 M USD** [1 607,8 ; 1 977,4], soit **+10,2 %**.

---

## 6. Contrôles qualité effectués

- Notebook exécuté de bout en bout : **23/23 cellules de code**, aucune erreur,
  8 figures intégrées.
- Rapport compilé avec `tectonic` : **15 pages**, aucun dépassement de marge
  (`Overfull`) après corrections, aucune référence manquante.
- Soutenance compilée : **15 diapositives**, aucun `Overfull`, figures
  lisibles, titre lisible.
- Vérification que chaque chiffre du rapport provient de
  `data/processed/resultats_modeles.json` ou des sorties du notebook.
- Vérification des chemins relatifs : le rapport et la soutenance se
  compilent depuis la racine du projet.
- Archive ZIP testée (`testzip`) : **80 fichiers**, 4,13 Mo.

---

## 7. Difficultés rencontrées et corrections

| Difficulté | Correction apportée |
|---|---|
| `ColumnTransformer` partagé entre pipelines (fuite de prétraitement) | Utilisation systématique de `clone(preprocesseur)` |
| Chevauchement d'étiquettes dans les figures 2 et 5 | Réglage des marges, des tailles de police et des annotations |
| Titre de soutenance illisible (texte sombre sur fond vert) | Passage du titre et du sous-titre en blanc |
| Figures trop petites dans les diapositives | Passage à une figure pleine largeur par diapositive, suppression des figures secondaires |
| Dépassements `Overfull` dans le rapport et la soutenance | Réduction des largeurs, `\footnotesize`, réglage des colonnes |
| Absence de `zip` sur la machine | Archive créée avec le module Python `zipfile` |
| Cellules absentes dans Comtrade | Zéros imputés + indicateur `declare` + test de sensibilité |

---

## 8. Limites du travail

- Montants **nominaux** en dollars courants : la croissance inclut l'inflation.
- **15 points annuels** seulement : les modèles à base d'arbres sont bridés.
- **Pas de saisonnalité** : invisible à fréquence annuelle.
- **Hub néerlandais** : les Pays-Bas réexportent une partie des flux.
- **Zéros imputés** : simplification assumée et testée.
- **Corrélation ≠ causalité** : le projet est prédictif, pas explicatif.

---

## 9. Ce qu'il reste à personnaliser

- Noms des deux étudiants, établissement, filière et date de remise dans
  `rapport/rapport.tex` et `soutenance/soutenance.tex`.
- Cochage et signature de `docs/journal_des_contributions.md`.
- Signature de `docs/declaration_ia.md`.
- Eventuelle relecture orthographique finale par le binôme.

---

## 10. Arborescence livrée

```
projet12-exportations-agroalimentaires-maroc/
├── README.md
├── requirements.txt
├── LICENSE
├── .gitignore
├── data/
│   ├── raw/                        # 45 JSON bruts
│   └── processed/                  # panel, séries, qualité, résultats, journal
├── src/
│   ├── download_comtrade.py
│   └── prepare_data.py
├── notebooks/
│   └── projet12_exportations_agroalimentaires.ipynb
├── figures/                        # fig01 … fig08
├── rapport/
│   ├── rapport.tex
│   ├── rapport.pdf
│   └── figures/
├── soutenance/
│   ├── soutenance.tex
│   └── soutenance.pdf
└── docs/
    ├── journal_des_contributions.md
    └── declaration_ia.md
```
