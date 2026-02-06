from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib

app = FastAPI()

# Load model pas start-up
model = joblib.load('model_fraud.pkl')

# Schema input: Model cuma nerima list float (V1-V28 + Amount)
class TransactionData(BaseModel):
    features: list[float] 

@app.get("/")
def home():
    return {"status": "active", "msg": "SalesGuard AI Backend is Running!"}

@app.post("/predict")
def predict_fraud(data: TransactionData):
    # Bungkus fitur ke dalam list biar jadi format 2D (row, col) buat model
    input_data = [data.features]
    
    # 1. Tebak label (0/1)
    prediction = model.predict(input_data)[0]
    label = "Fraud" if prediction == 1 else "Safe"
    
    # 2. Ambil skor probabilitas buat kelas '1' (Fraud)
    # [0][1] itu artinya ambil row pertama, kolom kedua (indeks 1)
    prob_score = model.predict_proba(input_data)[0][1]
    probability = round(prob_score * 100, 2) 

    # Return JSON ke dashboard
    return {
        "prediction": label,
        "probability": probability
    }