import os
import time
import joblib
import pandas as pd
from src.data import load_config
from src.features import prepare_features
from src.logger import get_logger

logger = get_logger("predict_module")


def load_model(model_path: str):
    """تحميل النموذج المدرب المحفوظ مع معالجة الأخطاء"""
    try:
        logger.info(f"جاري تحميل الموديل من المسار: {model_path}")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"ملف الموديل غير موجود في {model_path}")
        model = joblib.load(model_path)
        logger.info("تم تحميل الموديل بنجاح.")
        return model
    except FileNotFoundError as e:
        logger.error(str(e))
        raise e
    except Exception as e:
        logger.error(f"حدث خطأ غير متوقع أثناء تحميل الموديل: {str(e)}")
        raise e


def predict_order(input_df: pd.DataFrame, config_path: str = "config/config.yaml") -> dict:
    """إجراء التنبؤ وتسجيل زمن الاستجابة والنتائج والأخطاء"""
    start_time = time.time()
    logger.info("تم استقبال طلب تنبؤ جديد.")

    try:
        if input_df is None or input_df.empty:
            logger.warning("تم إرسال DataFrame فارغ للتنبؤ.")
            raise ValueError("البيانات المدخلة فارغة ولا يمكن إجراء التنبؤ عليها.")

        config = load_config(config_path)
        model = load_model(config["paths"]["model_path"])

        # تجهيز الميزات
        feature_cols = config["features"]["numerical_cols"]
        X = prepare_features(input_df, feature_cols)

        # التنبؤ
        prediction = int(model.predict(X)[0])
        probabilities = model.predict_proba(X)[0]
        late_probability = float(probabilities[1])

        latency = round((time.time() - start_time) * 1000, 2)

        result = {
            "prediction": prediction,
            "label": "Late" if prediction == 1 else "On Time",
            "probability_late": round(late_probability, 4),
            "latency_ms": latency,
            "model_version": config.get("version", "1.0.0"),
        }

        logger.info(
            f"تم التنبؤ بنجاح | النتيجة: {result['label']} | الاحتمالية: {result['probability_late']} | المستغرق: {latency} ms"
        )
        return result

    except Exception as e:
        logger.error(f"خطأ أثناء عملية التنبؤ: {str(e)}")
        raise e