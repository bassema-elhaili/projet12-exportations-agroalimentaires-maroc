#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Téléchargement des données UN Comtrade -- Projet 12
"Exportations agroalimentaires marocaines".

Source officielle
-----------------
UN Comtrade, API publique "preview" (sans clé) :
    https://comtradeapi.un.org/public/v1/preview/C/A/HS
Documentation : https://uncomtrade.org/docs/un-comtrade-api/

Contraintes constatées le 31/10/2026 (à revérifier le jour du TP) :
  * 1 seule période par requête en mode preview ;
  * 500 lignes maximum par réponse ;
  * pas de clé d'API -> quotas horaires/journalsiers non garantis.

Le script :
  1. interroge l'API une fois par année (2010-2024) ;
  2. sauvegarde la réponse JSON brute dans data/raw/ ;
  3. journalise chaque requête (URL, code HTTP, nb de lignes, horodatage)
     dans data/processed/journal_extractions.csv ;
  4. agrège les réponses dans data/processed/comtrade_brut.csv.

Exécution :  python src/download_comtrade.py
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

# --------------------------------------------------------------------------
# Paramètres de l'extraction (à documenter dans le rapport)
# --------------------------------------------------------------------------
BASE_URL = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"

REPORTER = 504                 # Maroc
FLOW = "X"                     # exportations
PERIODES = list(range(2010, 2025))   # 2010-2024

# Partenaires : les deux marchés imposés par la fiche (France, Espagne)
# + quatre marchés européens ajoutés pour disposer d'un panel exploitable.
PARTENAIRES = {
    0: "Monde",
    251: "France",
    724: "Espagne",
    276: "Allemagne",
    528: "Pays-Bas",
    826: "Royaume-Uni",
    380: "Italie",
}

# Chapitre 08 du Système harmonisé : « fruits comestibles, écorces d'agrumes »
# Décomposition HS4 (codes 0801 à 0814).
PRODUITS_HS4 = [
    "0801", "0802", "0803", "0804", "0805", "0806", "0807",
    "0808", "0809", "0810", "0811", "0812", "0813", "0814",
]

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "projet12-data-science/1.0 (etudiant)"})


def construire_url(periode: int, partenaires: list[int], codes: list[str]) -> str:
    """Construit l'URL de requête (paramètres triés, reproductible)."""
    params = {
        "reporterCode": REPORTER,
        "period": periode,
        "partnerCode": ",".join(str(p) for p in partenaires),
        "cmdCode": ",".join(codes),
        "flowCode": FLOW,
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{BASE_URL}?{query}"


def interroger(url: str, essais: int = 3, pause: float = 3.0) -> dict:
    """Requête HTTP avec ré-essais (l'API preview peut répondre 429/5xx)."""
    derniere_erreur: Exception | None = None
    for tentative in range(1, essais + 1):
        try:
            reponse = SESSION.get(url, timeout=90)
            if reponse.status_code == 200:
                charge = reponse.json()
                if charge.get("error"):
                    raise RuntimeError(f"Erreur API : {charge['error']}")
                return charge
            derniere_erreur = RuntimeError(f"HTTP {reponse.status_code}")
        except Exception as exc:  # noqa: BLE001 - on journalise et on réessaie
            derniere_erreur = exc
        if tentative < essais:
            time.sleep(pause * tentative)
    raise RuntimeError(f"Échec après {essais} tentatives : {derniere_erreur}")


def aplatir(charge: dict) -> list[dict]:
    """Ne conserve que les champs utiles au projet."""
    champs = [
        "period", "refYear", "reporterCode", "flowCode", "partnerCode",
        "cmdCode", "aggrLevel", "primaryValue", "netWgt", "qty",
        "qtyUnitAbbr", "classificationCode", "isAggregate",
    ]
    lignes = []
    for enregistrement in charge.get("data", []):
        ligne = {champ: enregistrement.get(champ) for champ in champs}
        ligne["partnerLibelle"] = PARTENAIRES.get(ligne["partnerCode"], "?")
        lignes.append(ligne)
    return lignes


def main() -> None:
    journal: list[dict] = []
    toutes_les_lignes: list[dict] = []

    taches = [
        # (nom, partenaires, codes)
        ("panel_marches", [p for p in PARTENAIRES if p != 0], PRODUITS_HS4),
        ("monde_hs2", [0], ["08"]),
        ("monde_hs4", [0], PRODUITS_HS4),
    ]

    for nom, partenaires, codes in taches:
        for periode in PERIODES:
            url = construire_url(periode, partenaires, codes)
            horodatage = datetime.now(timezone.utc).isoformat(timespec="seconds")
            try:
                charge = interroger(url)
                lignes = aplatir(charge)
                statut = "ok"
            except Exception as exc:  # noqa: BLE001
                lignes = []
                statut = f"erreur: {exc}"

            fichier = RAW_DIR / f"comtrade_{nom}_{periode}.json"
            if lignes:
                fichier.write_text(
                    json.dumps(charge, ensure_ascii=False, indent=1), encoding="utf-8"
                )
            for ligne in lignes:
                ligne["extraction"] = nom
            toutes_les_lignes.extend(lignes)

            journal.append({
                "extraction": nom,
                "periode": periode,
                "url": url,
                "statut": statut,
                "nb_lignes": len(lignes),
                "fichier_brut": fichier.name if lignes else "",
                "horodatage_utc": horodatage,
            })
            print(f"[{nom:12s}] {periode} -> {len(lignes):3d} lignes ({statut})")
            time.sleep(1.2)  # ménage la bande passante de l'API publique

    df = pd.DataFrame(toutes_les_lignes)
    df.to_csv(PROCESSED_DIR / "comtrade_brut.csv", index=False)
    pd.DataFrame(journal).to_csv(
        PROCESSED_DIR / "journal_extractions.csv", index=False
    )
    print(f"\nTotal : {len(df)} lignes -> data/processed/comtrade_brut.csv")


if __name__ == "__main__":
    main()
