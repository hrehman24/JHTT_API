# PWP SPRING 2026
# Music Web API - Beatify

## Group Information

- Student 1. Jalal Ghaffar, jghaffar24@student.oulu.fi
- Student 2. Hidayat Ur Rehman, Hidayat.Rehman@student.oulu.fi
- Student 3. Heikki Tolonen, heikki.tolonen@student.oulu.fi
- Student 4. Teemu Kettukangas, teemu.kettukangas@student.oulu.fi

## Quick Start

Run all commands from project root.

### 0) Clone repository with submodules

`PWP_JHHT_CLIENT` is a submodule, so clone recursively:

```bash
git clone https://github.com/Heiguli/PWP_JHHT.git --recursive 
cd PWP_JHHT
```

If you already cloned without submodules, run:

```bash
git submodule update --init --recursive
```

### 1) Install dependencies

```bash
pip install -r Database_folder/requirements.txt
pip install flask-restful pytest pytest-cov
```

### 2) Setup database and start API

```bash
python setup.py
```

This script installs missing dependencies, recreates tables, populates sample data, and starts the API.

### 3) Start API manually (optional)

```bash
python -m Beatify.api
```

API base URL:

```text
http://localhost:5000/Beatify/api/v1
```

## Tests

Run only API test file:

```bash
python -m pytest tests/api_test.py -v
```

Run all tests:

```bash
python -m pytest -v
```

Run coverage:

```bash
python -m pytest tests/api_test.py -v --cov=Beatify --cov-report=term-missing
```

## Documentation Index

- Main app package docs: [Beatify/README.md](Beatify/README.md)
- Database notes and setup details: [Database_folder/README.md](Database_folder/README.md)
- Test guide: [tests/README.md](tests/README.md)
- Schema folder notes: [Beatify/static/schema/README.md](Beatify/static/schema/README.md)
- Deployment guide: [DEPLOYMENT.md](DEPLOYMENT.md)
- API client docs: [API_Client_Auxiliary_service/PWP_JHHT_CLIENT/README.md](https://github.com/Heiguli/PWP_JHHT_CLIENT/blob/main/README.md)
- API Auxiliary service: [API_Client_Auxiliary_service/auxiliary_service/README.md](API_Client_Auxiliary_service/auxiliary_service/README.md)


## Docker Deployment (Quick)

Build and run local production-style stack:

```bash
docker compose up --build
```

Docker setup now seeds sample data on first startup by default.

Then open:

```text
http://localhost:5000/Beatify/api/v1/artists
http://localhost:5000/Beatify/api/v1/docs
http://localhost:5000/Beatify/api/v1/openapi.yaml
```

GitHub Actions workflow for CI/CD is in:

```text
.github/workflows/ci-cd.yml
```

Validate OpenAPI locally:

```bash
python -m openapi_spec_validator docs/openapi.yaml
```

Note: `/Beatify/api/v1` itself is not a standalone route in this API; use one of the resource or docs routes above.

## Notes

- The old `app/` package docs are no longer used. Current code lives in the `Beatify/` package.
- If you change folder structure, update imports and scripts (`setup.py`, tests, and DB scripts) accordingly.

