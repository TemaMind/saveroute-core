import re, rapidfuzz, pandas as pd

kw_pat = re.compile(r"(dual[- ]use|explos|missile|weapon|rifle|drone)", re.I)
sanction_names = sanctions["name"].str.lower().dropna().unique()

def label_row(r):
    kw = bool(kw_pat.search(r["description"] or ""))
    nm = False
    if pd.notna(r["consignee_name"]):
        nm = any(
            rapidfuzz.fuzz.partial_ratio(r["consignee_name"].lower(), s) > 90
            for s in sanction_names
        )
    return int(kw or nm)

df["label"] = df.apply(label_row, axis=1).astype("int8")
df.to_parquet(PROC / "train.parquet", index=False)

