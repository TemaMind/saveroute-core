import glob
import pathlib
import xml.etree.ElementTree as ET

import pandas as pd

RAW_DIR = pathlib.Path("data/raw")
OUT_DIR = pathlib.Path("data/interim")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------- OFAC (CSV) ------------------------------------------------------
ofac_files = sorted(glob.glob(str(RAW_DIR / "ofac_sdn_*.csv")))
if not ofac_files:
    raise FileNotFoundError("Файл ofac_sdn_*.csv не найден в data/raw/")

ofac_df = (
    pd.read_csv(ofac_files[-1], encoding="latin1")
    .rename(
        columns={
            "name": "name",
            "program": "program",
            "nationality": "nationality",
            "publication_date": "last_update",
        }
    )[
        ["name", "program", "nationality", "last_update"]
    ]
)
ofac_df["source"] = "OFAC_SDN"

# ---------- EU (XML) --------------------------------------------------------
eu_path = RAW_DIR / "eu_fsf.xml"
if not eu_path.exists():
    raise FileNotFoundError("eu_fsf.xml не найден в data/raw/")

eu_entries = []
tree = ET.parse(eu_path)
for entry in tree.findall(".//{*}sanctions-entry"):
    eu_entries.append(
        {
            "name": entry.findtext(".//{*}nameAlias/{*}wholeName"),
            "program": "EU_FSF",
            "nationality": entry.findtext(".//{*}citizenship"),
            "last_update": entry.findtext(".//{*}regulation/{*}publication-date"),
            "source": "EU_FSF",
        }
    )
eu_df = pd.DataFrame(eu_entries)

# ---------- UN (XML) --------------------------------------------------------
un_path = RAW_DIR / "un_sc.xml"
if not un_path.exists():
    raise FileNotFoundError("un_sc.xml не найден в data/raw/")

un_entries = []
tree = ET.parse(un_path)
for ind in tree.findall(".//INDIVIDUAL"):
    un_entries.append(
        {
            "name": ind.findtext("FIRST_NAME") + " " + ind.findtext("SECOND_NAME", ""),
            "program": "UN_SC",
            "nationality": ind.findtext("NATIONALITY"),
            "last_update": ind.findtext("LISTED_ON"),
            "source": "UN_SC",
        }
    )
un_df = pd.DataFrame(un_entries)

# ---------- Объединяем и чистим --------------------------------------------
df_all = pd.concat([ofac_df, eu_df, un_df], ignore_index=True)
df_all["name"] = df_all["name"].str.strip()
df_all = df_all.dropna(subset=["name"]).reset_index(drop=True)

# last_update → datetime64
df_all["last_update"] = pd.to_datetime(
    df_all["last_update"], errors="coerce", dayfirst=True
)

out_path = OUT_DIR / "sanctions_flat.parquet"
df_all.to_parquet(out_path, index=False)

print(f"✓ Сохранено {len(df_all):,} строк в {out_path}")