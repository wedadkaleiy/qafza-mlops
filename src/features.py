import numpy as np
import pandas as pd


def extract_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """استخراج الميزات الزمنية الآمنة من تاريخ الشراء"""
    df = df.copy()
    if "order_purchase_timestamp" in df.columns:
        df["order_purchase_timestamp"] = pd.to_datetime(
            df["order_purchase_timestamp"]
        )
        df["purchase_month"] = df["order_purchase_timestamp"].dt.month
        df["purchase_weekday"] = df["order_purchase_timestamp"].dt.weekday
        df["purchase_hour"] = df["order_purchase_timestamp"].dt.hour
    return df


def prepare_features(input_df: pd.DataFrame, feature_cols: list) -> pd.DataFrame:
    """تطبيق الترتيب والمعالجة وضمان تطابق الميزات مع النموذج"""
    df = extract_time_features(input_df)

    # ملء القيم المفقودة الأساسية إن وجدت
    fill_zeros = [
        "num_items",
        "total_price",
        "total_freight",
        "total_payment_value",
        "num_payment_methods",
    ]
    for col in fill_zeros:
        if col in df.columns:
            df[col] = df[col].fillna(0)

    # التأكد من وجود كافة أعمدة الميزات المتوقعة وتعبئة الناقص منها بـ 0
    for col in feature_cols:
        if col not in df.columns:
            df[col] = 0

    return df[feature_cols]