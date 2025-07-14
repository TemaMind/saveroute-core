import joblib
import pathlib


def test_model_load():
    m = joblib.load(pathlib.Path("models/saveroute_lr.joblib"))
    assert hasattr(m, "predict_proba")
