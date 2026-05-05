# Database Setup Guide

This project uses SQLite through SQLAlchemy.

## Recommended Workflow

From project root, run:

```bash
python setup.py
```

This will:
- install missing dependencies
- recreate database tables
- populate sample data
- start the API

## Manual Database Population

If you only want to (re)populate the database without running `setup.py`, run:

```bash
python Database_folder/populate_DB.py
```

## Docker Behavior

When using `docker compose up --build`, the app container can seed sample data automatically on startup via `POPULATE_DB=true`.
The startup script only seeds when the database is empty, so regular restarts do not duplicate records.

## Virtual Environment (Optional but Recommended)

Create venv:

```bash
python -m venv .venv
```

Activate on Windows:

```bat
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r Database_folder/requirements.txt
pip install flask-restful pytest pytest-cov
```

## Current Source of Truth

- Models are in `Beatify/models.py`
- Seeder script is `Database_folder/populate_DB.py`

This README is synced with the current Beatify package structure.
