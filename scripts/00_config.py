from pathlib import Path

RAW = Path("data/raw")
INTR = Path("data/interim")
PROC = Path("data/processed")

OFAC_URL   = "https://ofac.treasury.gov/downloads/sdn.csv"
EU_URL     = "https://www.treasury.gov/ofac/downloads/consolidated/consolidated.xml"  # пример
UN_URL     = "https://scsanctions.un.org/resources/xml/en/consolidated.xml"
HS_CSV_URL = "https://raw.githubusercontent.com/datasets/harmonized-system/main/data/hs92.csv"

COMTRADE_ENDPOINT = "https://comtradeapi.worldbank.org/v1/"

RAW.mkdir(exist_ok=True, parents=True)
INTR.mkdir(exist_ok=True)
PROC.mkdir(exist_ok=True)
