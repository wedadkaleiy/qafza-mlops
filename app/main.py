import os
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator
from src.data import load_config

app = FastAPI(
    title="Olist MLOps Prediction API",
    description="API for order status/delivery prediction with MLOps monitoring",
    version="1.0.0",
)

# تفعيل المراقبة وتوفير نقطة النهاية /metrics
Instrumentator().instrument(app).expose(app)

# تحميل الإعدادات والنموذج عند تشغيل التطبيق
config = load_config()
model_path = config.get("model", {}).get("path", "models/final_model.pkl")

model = None
if os.path.exists(model_path):
    model = joblib.load(model_path)


# هيكل البيانات المدخلة من المستخدم
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


@app.post("/predict")
def predict(data: OrderPredictionInput):
    if model is None:
        raise HTTPException(
            status_code=500, detail="Model file not found or failed to load."
        )

    try:
        # 1. تحويل المدخلات إلى DataFrame
        input_dict = data.dict()
        input_df = pd.DataFrame([input_dict])

        # 2. الحصول على قائمة الأعمدة المطلوبة للنموذج بالترتيب الصحيح
        if hasattr(model, "feature_names_in_"):
            expected_features = list(model.feature_names_in_)

            # إضافة أي أعمدة متوقعة مفقودة وإعطائها القيمة 0
            for col in expected_features:
                if col not in input_df.columns:
                    input_df[col] = 0

            # إعادة ترتيب الأعمدة لتطابق ترتيب التدريب تماماً
            input_df = input_df[expected_features]

        # 3. إجراء التنبؤ
        prediction = model.predict(input_df)

        return {
            "input": input_dict,
            "prediction": (
                prediction.tolist()
                if hasattr(prediction, "tolist")
                else prediction
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))