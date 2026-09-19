import os
import yaml
from sqlalchemy import create_engine


def load_config(config_path="config/config.yaml"):
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"ملف الإعدادات غير موجود في المسار: {config_path}"
        )

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if config is None:
        raise ValueError(
            "ملف الإعدادات فارغ! يرجى إضافة إعدادات db و features."
        )

    return config


def get_db_engine(config):
    db_conf = config["db"]
    # إنشاء رابط الاتصال بـ PostgreSQL
    connection_string = f"postgresql://{db_conf['user']}:{db_conf['password']}@{db_conf['host']}:{db_conf['port']}/{db_conf['database']}"
    engine = create_engine(connection_string)
    return engine