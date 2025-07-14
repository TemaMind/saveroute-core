from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pathlib

MODEL = joblib.load(pathlib.Path("models/saveroute_lr.joblib"))
app = FastAPI(title="SafeRoute API", version="0.1.0")


class Item(BaseModel):
    description: str


class Prediction(BaseModel):
    risk_score: float
    risk_label: int


@app.post("/v1/check", response_model=Prediction)
def check(item: Item):
    proba_row = MODEL.predict_proba([item.description])[0]
    # если модель знает только один класс (Dummy 0/1)
    if proba_row.shape[0] == 1:
        proba = 0.0 if MODEL.classes_[0] == 0 else 1.0
    else:
        # класс "1" всегда второй по возрастанию
        proba = proba_row[MODEL.classes_ == 1][0]

    return {"risk_score": float(proba), "risk_label": int(proba >= 0.5)}
