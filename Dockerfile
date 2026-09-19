FROM python:3.11-slim

WORKDIR /app

# نسخ ملف المقتضيات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي كود المشروع
COPY . .

# تعريض المنفذ 8000
EXPOSE 8000

# أمر تشغيل الـ FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]