import pandera as pa, pandas as pd
from 00_config import PROC
schema = pa.DataFrameSchema(
    {
        "hs_code": pa.Column(str, regex=True, nullable=False),
        "description": pa.Column(str),
        "reporter_iso": pa.Column(str, nullable=True, regex=False, coerce=True),
        "label": pa.Column(int, pa.Check.isin([0,1])),
    }
)
def test_train_schema():
    df = pd.read_parquet(PROC / "train.parquet", columns=schema.columns)
    schema.validate(df, lazy=True)