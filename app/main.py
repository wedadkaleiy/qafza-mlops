import logging
import os
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from src.data import load_config

# إعداد الـ Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mlops_app")

app = FastAPI(
    title="Olist MLOps Prediction API",
    description="API for order status prediction with MLOps monitoring and logging",
    version="1.0.0",
)

# تفعيل المراقبة عبر Prometheus
Instrumentator().instrument(app).expose(app)

# تحميل الإعدادات والنموذج
config = load_config()
model_path = config.get("model", {}).get("path", "models/final_model.pkl")

model = None
if os.path.exists(model_path):
  model = joblib.load(model_path)


class OrderPredictionInput(BaseModel):
  num_items: int = 1
  num_payment_methods: int = 1
  purchase_hour: int = 14
  purchase_month: int = 5
  purchase_weekday: int = 2
  freight_value: float = 15.2
  price: float = 120.5


@app.get("/")
def read_root():
  return {
      "status": "online",
      "message": "Welcome to Olist MLOps Prediction API",
  }


@app.get("/health")
def health_check():
  return {
      "status": "healthy" if model is not None else "degraded",
      "model_loaded": model is not None,
      "model_version": "1.0.0",
      "environment": "production",
  }


@app.post("/predict")
def predict(data: OrderPredictionInput):
  if model is None:
    logger.error("Predict attempt failed: Model not loaded.")
    raise HTTPException(
        status_code=500, detail="Model file not found or failed to load."
    )

  try:
    input_dict = data.dict()
    input_df = pd.DataFrame([input_dict])

    if hasattr(model, "feature_names_in_"):
      expected_features = list(model.feature_names_in_)
      for col in expected_features:
        if col not in input_df.columns:
          input_df[col] = 0
      input_df = input_df[expected_features]

    prediction = model.predict(input_df)
    probabilities = None
    if hasattr(model, "predict_proba"):
      probabilities = model.predict_proba(input_df).tolist()

    result = {
        "model_version": "1.0.0",
        "input": input_dict,
        "prediction": (
            prediction.tolist() if hasattr(prediction, "tolist") else prediction
        ),
        "probabilities": probabilities,
    }

    logger.info(f"Prediction requested. Result: {result['prediction']}")
    return result

  except Exception as e:
    logger.error(f"Error during prediction: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))