#!/usr/bin/env bash
set -e

echo "[entrypoint] Czekam na baze danych i upewniam sie, ze istnieje..."
python wait_for_db.py

echo "[entrypoint] Startuje FastAPI (uvicorn) na 0.0.0.0:8000..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
