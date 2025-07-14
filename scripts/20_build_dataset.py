#!/usr/bin/env python


from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import pandas as pd

# ──────────────────────── 0. Пути ────────────────────────────────────────
BASE = Path(__file__).resolve().parents[1]
RAW, INTR, PROC = BASE / "data/raw", BASE / "data/interim", BASE / "data/processed"
for p in (RAW, INTR, PROC):
    p.mkdir(parents=True, exist_ok=True)

# ──────────────────────── 1. Санкции ─────────────────────────────────────
sanc_fp = INTR / "sanctions_flat.parquet"
if sanc_fp.exists() and sanc_fp.stat().st_size:
    sanction_names = (
        pd.read_parquet(sanc_fp, columns=["name"])
        ["name"].str.lower().dropna().unique()
    )
else:
    sanction_names = []

# ──────────────────────── 2. HS-коды ─────────────────────────────────────
hs_fp = RAW / "hs_full.csv"
if not hs_fp.exists():
    raise FileNotFoundError("hs_full.csv отсутствует в data/raw/")

hs_raw = pd.read_csv(hs_fp)

# нормализуем заголовки
norm = {c.lower().strip(): c for c in hs_raw.columns}
code_col = norm.get("code") or norm.get("hs") or list(hs_raw.columns)[0]

# если в CSV всего одна колонка ― добавляем пустую Description
if len(hs_raw.columns) == 1:
    hs_raw["Description"] = ""
    desc_col = "Description"
else:
    desc_col = (
        norm.get("description")
        or norm.get("desc")
        or list(hs_raw.columns)[1]
    )

hs = (
    hs_raw
      .rename(columns={code_col: "hs_code", desc_col: "description"})
      .astype({"hs_code": "string"})
)

# ──────────────────────── 3. Comtrade ────────────────────────────────────
com_fp = RAW / "comtrade_2024.csv"
if com_fp.exists() and com_fp.stat().st_size:
    com = pd.read_csv(com_fp)
    if "hs_code" not in com.columns:
        for alt in ["cc", "commoditycode", "code"]:
            match = [c for c in com.columns if c.lower() == alt]
            if match:
                com = com.rename(columns={match[0]: "hs_code"})
                break
    com["hs_code"] = com["hs_code"].astype("string")
else:
    com = pd.DataFrame(columns=["hs_code"])

# ──────────────────────── 4. Эвристика label v0 ─────────────────────────
kw_re = re.compile(r"(dual[- ]use|explos|missile|weapon|rifle|drone)", re.I)

try:
    from rapidfuzz import fuzz  # type: ignore
    def fuzzy_hit(x: str) -> bool:
        return any(fuzz.partial_ratio(x.lower(), s) > 90 for s in sanction_names)
except ImportError:
    from difflib import SequenceMatcher
    def fuzzy_hit(x: str) -> bool:
        return any(SequenceMatcher(None, x.lower(), s).ratio() > 0.9 for s in sanction_names)

# ──────────────────────── 5. Склейка & метки ────────────────────────────
df = (
    hs.merge(com, on="hs_code", how="left", suffixes=("", "_com"))
      .assign(
          kw_flag=lambda d: d["description"].str.contains(kw_re, na=False),
          name_flag=lambda d: d["consignee_name"].apply(fuzzy_hit)
                       if sanction_names.size else False,
      )
)

# обязательные колонки …
for col, default in {"reporter_iso": pd.NA, "consignee_name": ""}.items():
    if col not in df.columns:
        df[col] = default

df["label"] = (df["kw_flag"] | df["name_flag"]).astype(int)   # int64
df["etl_date"] = date.today()

# ──────────────────────── 6. Save ───────────────────────────────────────
out = PROC / "train.parquet"
df.to_parquet(out, index=False)
print(f"✓ Saved {len(df):,} rows → {out.relative_to(Path.cwd())}")
