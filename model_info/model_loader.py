import os
import joblib

PERSISTENT_MODEL_PATH = "/home/site/wwwroot/models/model.joblib"

_model_cache = None

def load_model(model_path: str = None):
    global _model_cache
    if _model_cache is not None:
        return _model_cache

    env_path = os.getenv("MODEL_PATH")
    print(f"[DEBUG] MODEL_PATH env = {env_path}")
    print(f"[DEBUG] persistent exists = {os.path.exists(PERSISTENT_MODEL_PATH)}")

    path = model_path or env_path or PERSISTENT_MODEL_PATH

    print(f"[DEBUG] using model path = {path}")
    if not path or not os.path.exists(path):
        raise FileNotFoundError(f"Model file not found at: {path}")

    _model_cache = joblib.load(path)
    return _model_cache
