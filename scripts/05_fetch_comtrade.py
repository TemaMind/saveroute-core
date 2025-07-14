from comtradeapicall import ComtradeAPI
import pathlib

api = ComtradeAPI()
df = api.previewFinalData({
    "freq": "A", "ps": "2024", "px": "HS",
    "cc": "TOTAL", "rg": "all", "max": 500000
})
pathlib.Path("data/raw/comtrade_2024.csv").write_text(df.to_csv(index=False))