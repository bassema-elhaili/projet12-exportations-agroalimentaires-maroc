# Projet 12 — Exportations agroalimentaires marocaines

**Prévoir les ventes de fruits du Maroc par marché (chapitre 08 du Système harmonisé, 2010–2024)**

Projet de Data Science appliquée au commerce international. Le dépôt contient
l'intégralité de la chaîne : extraction des données officielles, préparation,
analyse exploratoire, modélisation, évaluation, rapport scientifique et
support de soutenance.

> **Question de recherche.** Peut-on prévoir la valeur exportée d'un couple
> (marché, produit) à un an, et les modèles d'apprentissage automatique
> battent-ils une simple reconduction de l'année précédente ?

---

## 1. Résultat principal

Le projet apporte un **résultat négatif documenté**, plus intéressant qu'un
gain artificiel :

| Modèle | WAPE validation glissante | WAPE test 2023–2024 | MASE vs persistance |
|---|---:|---:|---:|
| Persistance (référence) | **0,297** | 0,262 | 1,000 |
| Ridge (α = 100) | 0,381 | 0,395 | 1,506 |
| Forêt aléatoire | 0,314 | **0,255** | **0,971** |
| Gradient boosting | 0,314 | 0,295 | 1,125 |

La forêt aléatoire gagne de 2,9 % sur le test, mais **perd en validation
glissante** (0,314 contre 0,297) : le gain n'est pas robuste et dépend de la
fenêtre. Les gains se concentrent sur l'Espagne, les Pays-Bas et le
Royaume-Uni ; la persistance reste meilleure sur la France, l'Allemagne et
l'Italie. La conclusion est donc que, sur 15 années annuelles, **aucun modèle
testé ne bat la persistance de manière fiable** — ce qui est cohérent avec la
littérature sur les prévisions de commerce à fréquence annuelle.

Quelques chiffres clés (tous issus de l'API, aucun chiffre saisi à la main) :

- **1 607,6 M USD** exportés vers les six marchés étudiés en 2024, contre
  325,6 M USD en 2010 (**×4,9**, TCAM de **12,1 %**).
- **75,6 %** des exportations marocaines du chapitre 08 vont vers ces six
  marchés en 2024 (moyenne 2010–2024 : 66,8 %).
- Produits dominants en 2024 : **0810** autres fruits frais (61,0 %),
  **0804** dattes/avocats (13,9 %), **0805** agrumes (9,8 %).
- Marchés en 2024 : Espagne 415,6 M USD (TCAM 19,3 %), Royaume-Uni
  390,9 M USD (17,7 %), Pays-Bas 322,6 M USD (9,9 %), France 313,5 M USD
  (5,8 %), Allemagne 149,0 M USD (17,1 %), Italie 15,9 M USD (7,9 %).
- Prix implicite des agrumes : **0,73 → 1,06 USD/kg** (+45 %), soit une
  croissance surtout **en valeur**, pas en volume.
- Concentration (indice de Herfindahl) : 6 388 en 2010 → **5 042** en 2024 ;
  les trois premiers couples marché–produit pèsent **49,2 %** de la valeur.
- Projection 2025 (scénario de cadrage, intervalle empirique à 80 %) :
  **1 771,3 M USD** [1 607,8 ; 1 977,4], soit **+10,2 %**.

---

## 2. Structure du dépôt

```
projet12-exportations-agroalimentaires-maroc/
├── README.md                       # ce fichier
├── requirements.txt                # dépendances Python épinglées
├── LICENSE                         # MIT (code) + CC BY 4.0 (texte, figures)
├── data/
│   ├── raw/                        # 45 réponses JSON brutes de UN Comtrade
│   └── processed/
│       ├── comtrade_brut.csv       # 1 058 lignes agrégées
│       ├── journal_extractions.csv # traçabilité des 45 requêtes API
│       ├── panel.csv               # 1 260 lignes (6 marchés × 14 produits × 15 ans)
│       ├── qualite.csv             # couverture par produit
│       ├── series_annuelles.csv    # séries agrégées 2010–2024
│       └── resultats_modeles.json  # toutes les métriques du rapport
├── src/
│   ├── download_comtrade.py        # extraction API + journal
│   └── prepare_data.py             # construction du panel (règles R1–R4)
├── notebooks/
│   └── projet12_exportations_agroalimentaires.ipynb  # analyse complète exécutée
├── figures/                        # fig01 … fig08, 200 dpi
├── rapport/
│   ├── rapport.tex                 # source LaTeX du rapport
│   ├── rapport.pdf                 # rapport compilé (15 pages)
│   └── figures/                    # copie des figures utilisées
├── soutenance/
│   ├── soutenance.tex              # support beamer (8–10 min)
│   └── soutenance.pdf              # support compilé
└── docs/
    ├── journal_des_contributions.md
    └── declaration_ia.md
```

---

## 3. Installation

Python **3.11 ou plus récent** est requis (le projet a été exécuté avec
Python 3.14.8). Les versions épinglées sont celles de l'exécution de
référence.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

Pour recompiler le rapport et la soutenance, il faut une distribution LaTeX
avec `babel-french`, `booktabs`, `beamer` et `tectonic` (recommandé, aucune
installation de milliers de paquets) :

```bash
tectonic -X compile rapport/rapport.tex
tectonic -X compile soutenance/soutenance.tex
```

---

## 4. Ordre d'exécution

La chaîne est **strictement séquentielle** ; chaque étape lit la sortie de la
précédente.

```bash
# 1. Extraction UN Comtrade (45 requêtes, ~1 à 2 min selon le réseau)
python src/download_comtrade.py

# 2. Préparation du panel et des séries agrégées
python src/prepare_data.py

# 3. Analyse, figures et modèles (exécuter le notebook de bout en bout)
jupyter nbconvert --to notebook --execute --inplace \
  notebooks/projet12_exportations_agroalimentaires.ipynb
```

Le notebook est déjà **exécuté** dans le dépôt : ses sorties, ses figures et
`data/processed/resultats_modeles.json` sont inclus. Il n'est donc pas
nécessaire de relancer l'extraction pour lire les résultats. Une exécution
complète prend environ 2 à 4 minutes (hors téléchargement).

> **Reproductibilité.** La graine aléatoire est fixée à `42`. Les scripts
> d'acquisition et de préparation sont séparés du notebook pour que celui-ci
> reste lisible ; les deux étapes sont documentées dans le rapport
> (annexe A). L'API *preview* de Comtrade ne nécessite aucune clé, mais ses
> quotas ne sont pas garantis : en cas d'échec, le journal
> `data/processed/journal_extractions.csv` indique la requête à rejouer.

---

## 5. Données

| Élément | Valeur |
|---|---|
| Source | UN Comtrade, API publique *preview* (`/public/v1/preview/C/A/HS`) |
| Déclarant | Maroc (code 504) |
| Flux | Exportations (`X`) |
| Période | 2010–2024 (15 années) |
| Produits | Chapitre 08, décomposition HS4 0801–0814 |
| Marchés | France (251), Espagne (724), Allemagne (276), Pays-Bas (528), Royaume-Uni (826), Italie (380) |
| Référence monde | Partenaire 0, agrégats HS2 et HS4 |
| Requêtes | 45 (15 années × 3 extractions), **0 échec** |
| Lignes brutes | 1 058 |
| Panel | 1 260 lignes ; **834 cellules observées (66,2 %)**, 426 zéros imputés |
| Produits modélisés | 9 sur 14 (couverture ≥ 50 %) |
| Observations modélisables | 648 |

**Choix assumés et documentés dans le rapport :**

1. **Six marchés au lieu de deux.** La fiche imposait la France et l'Espagne ;
   quatre marchés européens ont été ajoutés pour disposer d'un panel
   exploitable (648 observations au lieu d'environ 200). Le couple
   France–Espagne reste analysé séparément.
2. **Zéros imputés.** Le Maroc est l'unique déclarant : une cellule absente
   signifie « aucun flux enregistré ». Elle est traitée comme un zéro, avec
   un indicateur `declare` (1 = observé, 0 = imputé) et un test de
   sensibilité S1 qui exclut ces zéros de l'entraînement.
3. **Produits écartés.** Les produits présents dans moins de 50 % des
   cellules (0801, 0803, 0808, 0812, 0813) sont exclus de la modélisation
   mais conservés dans les fichiers avec `retenu_pour_modele = 0`.
4. **Aucune fuite temporelle.** Toutes les variables explicatives sont
   connues à la fin de l'année *t* (retards t, t−1, t−2, t−3, moyennes
   mobiles passées, part du marché, croissance mondiale). La cible est la
   valeur en *t+1*.

### Limites

- Montants **nominaux** en dollars courants : aucune déflation, la croissance
  mesurée inclut l'inflation.
- **15 points annuels** seulement : les modèles à base d'arbres sont bridés
  par la taille de l'échantillon.
- **Pas de saisonnalité** : invisible à fréquence annuelle, c'est la première
  limite à lever (passage au mensuel).
- **Hub néerlandais** : les Pays-Bas réexportent une partie des flux, la
  destination statistique n'est pas la destination finale.
- **Zéros imputés** : simplification assumée, testée en sensibilité.
- **Corrélation ≠ causalité** : le projet est prédictif, pas explicatif.

---

## 6. Méthode

- **Cible** : `y_{t+1}`, modélisée en `log1p` puis reconstruite par `expm1`.
- **Découpage temporel** : entraînement *t* ≤ 2019 (cibles 2011–2020),
  validation glissante à six fenêtres *expanding* (2016→2017 … 2021→2022)
  pour le choix des hyperparamètres, test final *t* = 2022–2023 (cibles
  2023–2024, 108 observations).
- **Modèles** : persistance (référence), Ridge (α = 100), forêt aléatoire
  (600 arbres, feuille minimale 15, `max_features = 0.5`), gradient boosting
  histogramme (perte absolue, taux 0,02, 200 itérations).
- **Métriques** : MAE, RMSE, WAPE et MASE par rapport à la persistance.
- **Tests de sensibilité** : S1 sans zéros imputés, S2 test élargi
  2020–2024, S3 sans le produit dominant 0810.

Le préprocesseur (indicateurs de marché et de produit, standardisation des
variables numériques) est encapsulé dans un `Pipeline` scikit-learn réajusté
à chaque fenêtre : aucune statistique calculée sur le test ne contamine
l'entraînement.

---

## 7. Figures

| Fichier | Contenu |
|---|---|
| `fig01_dynamique_agregee.png` | Valeur exportée vers les six marchés et part dans le total mondial |
| `fig02_structure_produits.png` | Structure par produit HS4, 2010 vs 2024 |
| `fig03_marches.png` | Dynamique par marché et contribution à la croissance |
| `fig04_agrumes.png` | Exportations d'agrumes (0805) et prix implicite |
| `fig05_concentration.png` | Indice de Herfindahl et principaux couples marché–produit |
| `fig06_comparaison_modeles.png` | Prévisions vs réalisations et WAPE par modèle |
| `fig07_importance.png` | Importance par permutation des variables |
| `fig08_projection_2025.png` | Projection 2025 par marché avec intervalle à 80 % |

---

## 8. Auteurs et licence

- **Binôme** : *à compléter* (Nom 1, Nom 2)
- **Établissement / filière** : *à compléter*
- **Module** : Data Science appliquée au commerce international
- **Année universitaire** : 2026–2027

Les données appartiennent à UN Comtrade et sont utilisées selon ses conditions
d'utilisation (citation de la source obligatoire). Le code, le rapport et les
figures de ce dépôt sont produits par les auteurs du projet et publiés sous
licence **MIT** pour le code et **CC BY 4.0** pour le texte et les figures.

> L'usage d'outils d'IA comme aide à la programmation et à la relecture est
> déclaré dans `docs/declaration_ia.md`, conformément aux règles de
> l'établissement. Les données, résultats et interprétations restent de la
> responsabilité des auteurs ; aucun chiffre n'a été simulé ni inventé.
