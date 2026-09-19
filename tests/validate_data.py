import great_expectations as ge
import pandas as pd
from src.data import get_db_engine, load_config
from src.logger import get_logger

logger = get_logger("data_validation")


def validate_database_tables():
    """التحقق من صحة وجودة بيانات جدول الطلبات والمنتجات في قاعدة البيانات"""
    try:
        config = load_config()
        engine = get_db_engine(config)

        logger.info("جاري الاتصال بقاعدة البيانات واختبار جودة البيانات...")

        # استعلام يربط جدول الطلبات بجدول المنتجات للحصول على السعر ورسوم الشحن
        query = """
        SELECT o.order_id, o.customer_id, oi.price, oi.freight_value 
        FROM orders o 
        JOIN order_items oi ON o.order_id = oi.order_id 
        LIMIT 1000
        """
        df = pd.read_sql(query, engine)

        if df.empty:
            logger.error("البيانات المسترجعة فارغة!")
            return False

        # تحويل الـ DataFrame إلى Great Expectations DataAsset
        ge_df = ge.from_pandas(df)

        # 1. التحقق من وجود الأعمدة الأساسية (price و freight_value)
        required_cols = config["features"]["numerical_cols"]
        for col in required_cols:
            ge_df.expect_column_to_exist(col)

        # 2. التحقق من ألا تكون قيم المعرفات فارغة
        ge_df.expect_column_values_to_not_be_null("order_id")

        results = ge_df.validate()

        if results["success"]:
            logger.info("نجحت جميع اختبارات جودة البيانات! ✅")
            print("Data Validation Passed successfully!")
        else:
            logger.warning("فشلت بعض اختبارات جودة البيانات! ⚠️")
            print("Data Validation Failed!")
            for res in results["results"]:
                if not res["success"]:
                    print(
                        "FAILED EXPECTATION:",
                        res["expectation_config"]["expectation_type"],
                        res["expectation_config"]["kwargs"],
                    )

        return results["success"]

    except Exception as e:
        logger.error(f"حدث خطأ أثناء فحص البيانات: {str(e)}")
        raise e


if __name__ == "__main__":
    validate_database_tables()