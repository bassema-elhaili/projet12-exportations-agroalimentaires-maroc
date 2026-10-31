# Déclaration d'usage d'outils d'intelligence artificielle

Conformément aux règles de l'établissement et à la charte d'intégrité
académique, le binôme déclare l'usage suivant des outils d'IA générative.

## 1. Outils utilisés

| Outil | Usage | Périmètre |
|---|---|---|
| Assistant de programmation (LLM) | Aide à l'écriture et au débogage du code Python, relecture du LaTeX, structuration du notebook | Suggestions de code, corrections de syntaxe, reformulations |
| Aucun autre outil | — | — |

## 2. Ce qui a été fait avec l'assistance

- **Code** : propositions de fonctions pour l'extraction API, la construction
  du panel, les pipelines scikit-learn et les graphiques matplotlib. Chaque
  proposition a été lue, exécutée et validée par le binôme ; les erreurs
  (par exemple la réutilisation d'un `ColumnTransformer` entre pipelines)
  ont été identifiées et corrigées lors des tests.
- **Rédaction** : aide à la mise en forme du rapport LaTeX et à la clarté de
  certaines phrases. Le contenu scientifique, les choix méthodologiques et
  les interprétations sont ceux du binôme.
- **Soutenance** : trame et suggestions de formulation ; le contenu a été
  vérifié et répété par les deux étudiants.

## 3. Ce qui n'a pas été fait avec l'assistance

- Aucune donnée n'a été générée, simulée ou inventée : **toutes les valeurs
  proviennent de l'API UN Comtrade** et sont tracées dans
  `data/processed/journal_extractions.csv`.
- Aucun résultat, tableau ou chiffre du rapport n'a été produit par un
  modèle de langage.
- Les figures sont générées par le notebook à partir des données extraites.
- Les références bibliographiques renvoient à des documents réels et
  vérifiables.

## 4. Vérification

Le binôme a vérifié :

1. que le notebook s'exécute de bout en bout sans erreur (`Run all`) ;
2. que chaque chiffre du rapport correspond à une sortie de
   `data/processed/resultats_modeles.json` ou du notebook ;
3. que les scripts d'extraction et de préparation reproduisent les fichiers
   livrés ;
4. que le texte ne contient aucun passage copié sans citation.

## 5. Responsabilité

Les auteurs assument l'entière responsabilité du contenu du rapport, du code
et des conclusions. L'outil d'IA est utilisé comme un assistant, jamais comme
une source de vérité.

| | Nom | Date | Signature |
|---|---|---|---|
| Étudiant 1 | | | |
| Étudiant 2 | | | |

---

*À joindre au rapport ou à déposer avec le projet selon la procédure du
module.*
