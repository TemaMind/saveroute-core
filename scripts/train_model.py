#!/usr/bin/env python

from pathlib import Path

import joblib
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

DATA = Path("data/processed/train.parquet")
MODELDIR = Path("models")
MODELDIR.mkdir(exist_ok=True)

df = pd.read_parquet(DATA, columns=["description", "label"])
X = df["description"].fillna("")
y = df["label"]

if df.empty:
    # fall-back: модель всегда возвращает «0» (низкий риск)
    model = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(vocabulary=["placeholder"])),
            ("clf", DummyClassifier(strategy="constant", constant=0, random_state=0)),
        ],
    ).fit(["placeholder"], [0])
    print("⚠️  empty train set → saved DummyClassifier (always 0)")
else:
    model = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(max_features=25_000, ngram_range=(1, 2))),
            ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ],
    ).fit(X, y)
    print(f"✓ model trained on {len(df):,} rows")

joblib.dump(model, MODELDIR / "saveroute_lr.joblib")
print("→", MODELDIR / "saveroute_lr.joblib")
