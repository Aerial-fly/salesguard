from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib

app = FastAPI()

model = joblib.load('model_fraud.pkl')

class TransactionData(BaseModel):
    features: list[float] 

@app.get("/")
def home():
    return {"status": "active", "msg": "SalesGuard AI Backend is Running!"}

@app.post("/predict")
def predict_fraud(data: TransactionData):
    input_data = [data.features]
    
    prediction = model.predict(input_data)[0]
    label = "Fraud" if prediction == 1 else "Safe"
    
    prob_score = model.predict_proba(input_data)[0][1]
    probability = round(prob_score * 100, 2) 

    return {
        "prediction": label,
        "probability": probability
    }
