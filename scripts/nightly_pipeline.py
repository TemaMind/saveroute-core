#!/usr/bin/env python

import datetime
import subprocess
import sys
import hashlib
import pandas as pd
from _utils import download
import scripts.sanctions_parser as sp
from scripts.config import INTR, OFAC_URL, EU_URL, UN_URL
from scripts.build_dataset import build_dataset

THRESHOLD = 0.01        # retrain, если прирост ≥ 1 %
TODAY = datetime.date.today().strftime("%Y%m%d")
PATCH_DIR = INTR / "patches"
PATCH_DIR.mkdir(exist_ok=True, parents=True)
MASTER_PATH = INTR / "sanctions_flat.parquet"

# ---------------------------------------------------------------------- fetch
ofac_file = download(OFAC_URL, f"ofac_sdn_{TODAY}.csv")
eu_file   = download(EU_URL,   f"eu_fsf_{TODAY}.xml")
un_file   = download(UN_URL,   f"un_sc_{TODAY}.xml")

# ---------------------------------------------------------------- normalize →
def sig(text: str) -> int:
    return hashlib.sha1(text.encode("utf-8")).hexdigest().__hash__()

frames = []

# OFAC
ofac = pd.read_csv(ofac_file, encoding="latin1")[["name", "program", "nationality"]]
ofac["source"] = "OFAC_SDN"
frames.append(ofac)

# EU
frames.append(pd.DataFrame(sp.parse_eu(eu_file)))
# UN
frames.append(pd.DataFrame(sp.parse_un(un_file)))

today_df = (
    pd.concat(frames, ignore_index=True)
    .dropna(subset=["name"])
    .assign(sig=lambda d: d["name"].str.lower().str.strip().map(sig))
)

# ---------------------------------------------------------------------- diff
if MASTER_PATH.exists():
    master = pd.read_parquet(MASTER_PATH, columns=["sig"])
else:
    master = pd.DataFrame(columns=["sig"])

new_rows = today_df[~today_df["sig"].isin(master["sig"])].copy()
if new_rows.empty:
    print("✓ No new sanctioned entities today.")
    sys.exit(0)

patch_path = PATCH_DIR / f"{TODAY}.parquet"
new_rows.to_parquet(patch_path, index=False)
print(f"✓ Patch saved: +{len(new_rows)} rows → {patch_path}")

# merge + overwrite master
updated_master = pd.concat([master, new_rows], ignore_index=True)
updated_master.to_parquet(MASTER_PATH, index=False)
print(f"✓ Master updated → {len(updated_master)} total rows")

# ---------------------------------------------------------------- retrain?
growth = len(new_rows) / len(updated_master)
print(f"Δ = {growth:.2%}")
if growth < THRESHOLD:
    print("∆ below threshold; skip retrain.")
    sys.exit(0)

# ---------------------------------------------------------------- dataset &
build_dataset(master_df=updated_master)
print("✓ train.parquet rebuilt")

# ---------------------------------------------------------------- retrain ml
print("→ retraining baseline model...")
ret = subprocess.run(
    ["poetry", "run", "python", "scripts/train_model.py"],
    capture_output=True, text=True
)
print(ret.stdout)
if ret.returncode:
    print(ret.stderr, file=sys.stderr)
    sys.exit(ret.returncode)

print("✓ baseline model retrained")
