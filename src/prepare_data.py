#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Préparation des données -- Projet 12
"Exportations agroalimentaires marocaines".

Entrée  : data/processed/comtrade_brut.csv  (produit par src/download_comtrade.py)
Sorties :
  * data/processed/panel.csv            : panel partenaire x produit HS4 x année
  * data/processed/series_annuelles.csv : séries agrégées (6 marchés + monde)
  * data/processed/qualite.csv          : couverture par produit (journal qualité)

Règles de préparation (toutes justifiées dans le rapport) :
  R1. Le code produit est lu comme chaîne sur 4 caractères (0805 et non 805).
  R2. Une cellule absente de Comtrade pour un couple (partenaire, produit, année)
      est traitée comme un flux nul : le Maroc est le déclarant de toutes les
      séries, une absence signifie "aucun flux enregistré". La colonne
      `declare` conserve l'information (1 = observé, 0 = zéro imputé) et permet
      un test de sensibilité excluant les zéros imputés.
  R3. Les produits trop clairsemés (< 50 % de cellules observées) sont écartés
      du modèle mais restent dans le fichier avec `retenu_pour_modele = 0`.
  R4. Aucune variable construite n'utilise d'information postérieure à l'année t
      (les retards sont strictement t, t-1, t-2, t-3).

Exécution : python src/prepare_data.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

PRODUITS = {
    "0801": "Noix de coco, noix du Brésil et noix de cajou",
    "0802": "Autres fruits à coque (amandes, noisettes, noix)",
    "0803": "Bananes et plantains",
    "0804": "Dattes, figues, ananas, avocats, mangues",
    "0805": "Agrumes (frais ou secs)",
    "0806": "Raisins frais ou secs",
    "0807": "Melons, pastèques et papayes",
    "0808": "Pommes, poires et coings",
    "0809": "Abricots, cerises, pêches, prunes",
    "0810": "Autres fruits frais (fraises, kiwis, grenades)",
    "0811": "Fruits congelés",
    "0812": "Fruits conservés provisoirement",
    "0813": "Fruits séchés (autres que 0801-0806)",
    "0814": "Écorces d'agrumes ou de melons",
}

SEUIL_COUVERTURE = 0.50


def charger_brut() -> pd.DataFrame:
    """Charge le CSV brut et normalise les types."""
    df = pd.read_csv(PROCESSED / "comtrade_brut.csv", dtype={"cmdCode": str})
    df["cmdCode"] = df["cmdCode"].str.zfill(4)
    df["period"] = df["period"].astype(int)
    df["primaryValue"] = pd.to_numeric(df["primaryValue"], errors="coerce")
    df["netWgt"] = pd.to_numeric(df["netWgt"], errors="coerce")
    return df


def construire_panel(brut: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Construit le panel complet (grille partenaire x produit x année)."""
    marches = brut[brut["extraction"] == "panel_marches"].copy()
    monde = brut[brut["extraction"] == "monde_hs4"].copy()

    annees = sorted(marches["period"].unique())
    partenaires = (
        marches[["partnerCode", "partnerLibelle"]]
        .drop_duplicates()
        .sort_values("partnerLibelle")
    )

    grille = pd.MultiIndex.from_product(
        [partenaires["partnerCode"], list(PRODUITS), annees],
        names=["partnerCode", "cmdCode", "annee"],
    ).to_frame(index=False)
    grille = grille.merge(partenaires, on="partnerCode", how="left")

    observe = marches[
        ["partnerCode", "cmdCode", "period", "primaryValue", "netWgt"]
    ].rename(columns={"period": "annee", "primaryValue": "valeur_usd",
                      "netWgt": "poids_net_kg"})
    observe["declare"] = 1

    panel = grille.merge(observe, on=["partnerCode", "cmdCode", "annee"], how="left")
    panel["declare"] = panel["declare"].fillna(0).astype(int)
    panel["valeur_usd"] = panel["valeur_usd"].fillna(0.0)
    panel["poids_net_kg"] = panel["poids_net_kg"].fillna(0.0)

    # Totaux mondiaux du produit (tous partenaires confondus)
    monde = monde[["cmdCode", "period", "primaryValue"]].rename(
        columns={"period": "annee", "primaryValue": "monde_usd"}
    )
    panel = panel.merge(monde, on=["cmdCode", "annee"], how="left")

    panel["produit"] = panel["cmdCode"].map(PRODUITS)
    panel["part_marche"] = np.where(
        panel["monde_usd"] > 0, panel["valeur_usd"] / panel["monde_usd"], np.nan
    )
    panel["prix_unitaire_usd_kg"] = np.where(
        panel["poids_net_kg"] > 0,
        panel["valeur_usd"] / panel["poids_net_kg"],
        np.nan,
    )

    # Couverture par produit et règle R3
    couverture = (
        panel.groupby(["cmdCode", "produit"])["declare"]
        .agg(cellules_observees="sum", cellules_totales="size")
        .reset_index()
    )
    couverture["taux_couverture"] = (
        couverture["cellules_observees"] / couverture["cellules_totales"]
    ).round(3)
    valeurs = (
        panel.groupby(["cmdCode", "produit"], as_index=False)["valeur_usd"]
        .sum()
        .rename(columns={"valeur_usd": "valeur_totale_usd"})
    )
    couverture = couverture.merge(valeurs, on=["cmdCode", "produit"], how="left")
    couverture["retenu_pour_modele"] = (
        couverture["taux_couverture"] >= SEUIL_COUVERTURE
    ).astype(int)

    panel = panel.merge(
        couverture[["cmdCode", "retenu_pour_modele"]], on="cmdCode", how="left"
    )
    panel = panel.sort_values(["partnerLibelle", "cmdCode", "annee"]).reset_index(
        drop=True
    )
    return panel, couverture


def construire_series(panel: pd.DataFrame, brut: pd.DataFrame) -> pd.DataFrame:
    """Séries annuelles : exportations vers les 6 marchés et vers le monde."""
    six = (
        panel.groupby("annee")
        .agg(
            valeur_6_marches_usd=("valeur_usd", "sum"),
            poids_6_marches_kg=("poids_net_kg", "sum"),
        )
        .reset_index()
    )
    monde = (
        brut[brut["extraction"] == "monde_hs2"]
        .groupby("period")["primaryValue"]
        .sum()
        .reset_index()
        .rename(columns={"period": "annee", "primaryValue": "valeur_monde_usd"})
    )
    series = six.merge(monde, on="annee", how="outer").sort_values("annee")
    series["part_6_marches"] = (
        series["valeur_6_marches_usd"] / series["valeur_monde_usd"]
    )
    series["prix_moyen_usd_kg"] = (
        series["valeur_6_marches_usd"] / series["poids_6_marches_kg"]
    )
    return series


def main() -> None:
    brut = charger_brut()
    panel, couverture = construire_panel(brut)
    series = construire_series(panel, brut)

    panel.to_csv(PROCESSED / "panel.csv", index=False)
    series.to_csv(PROCESSED / "series_annuelles.csv", index=False)
    couverture.to_csv(PROCESSED / "qualite.csv", index=False)

    print(f"Panel      : {panel.shape[0]} lignes x {panel.shape[1]} colonnes")
    print(f"Séries     : {series.shape[0]} années ({series.annee.min()}-{series.annee.max()})")
    print(f"Produits   : {(couverture.retenu_pour_modele == 1).sum()} retenus / "
          f"{len(couverture)}")
    print("\nCouverture par produit :")
    print(couverture.to_string(index=False))


if __name__ == "__main__":
    main()
