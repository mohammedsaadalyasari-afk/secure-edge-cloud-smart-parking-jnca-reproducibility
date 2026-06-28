from fastapi import FastAPI
from model_loader import load_model

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}

@app.get("/predict")
def predict(x: float):
    model = load_model()
    y = model.predict([[x]])
    return {"prediction": float(y[0])}
