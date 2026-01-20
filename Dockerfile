# ==========================================
# Stage 1: Build Frontend (React/Vite)
# ==========================================
FROM node:20-slim AS builder

WORKDIR /app/frontend

COPY frontend/Dify-ChatBot-V2/ ./

RUN npm ci && npm run build


# ==========================================
# Stage 2: Build Backend (Django + Utils)
# ==========================================
FROM python:3.12-slim

LABEL "language"="python"
LABEL "framework"="django"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY --from=builder /app/frontend/dist ./frontend/Dify-ChatBot-V2/dist

RUN SECRET_KEY=dummy_for_build python manage.py collectstatic --noinput

EXPOSE 8080

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8080"]