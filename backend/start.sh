#!/usr/bin/env bash
set -e

# Idempotente: crea las tablas que falten via SQLAlchemy, no toca las existentes.
python -m src.db.init

uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"
