# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the stack

The whole project runs via Docker Compose. The entrypoint script `iniciar_proyecto.bat` (Windows) validates `.env`, waits for Docker Desktop, and runs `docker compose up -d --build`.

- First run: copy `.env.example` to `.env` and replace every `replace_with_*` placeholder before starting (the launcher refuses to proceed otherwise).
- Start everything: `iniciar_proyecto.bat` or `docker compose up -d --build`.
- Restart without rebuilding images: `iniciar_proyecto.bat --no-build`.
- Wipe Postgres + MinIO volumes (needed when changing `POSTGRES_PASSWORD`): `iniciar_proyecto.bat --reset-data --yes`.
- Logs: `docker compose logs -f [service]`.

Service URLs (bound to `127.0.0.1` only):
- Dashboard (Flask): http://localhost:8501
- Backend (FastAPI): http://localhost:8000 — docs at `/docs`
- MinIO console: http://localhost:9001

### Compose profiles (not started by default)

- `pipeline` — one-shot Spark batch job: `docker compose --profile pipeline up --build pipeline`
- `training` — CNN training (requires NVIDIA GPU): `docker compose --profile training up --build model-trainer`
- `triage-training` — sklearn triage model: `docker compose --profile triage-training up --build triage-trainer`

## Tests

Each service has its own `requirements-dev.txt` and pytest suite. Run from inside the service directory (or the corresponding container) — `conftest.py` sets up the `app/` import path and stub env vars.

- Backend: `cd backend && pytest` (single test: `pytest tests/unit/test_radiology_service.py::test_name`)
- Dashboard: `cd dashboard && pytest`
- Backend coverage: `pytest --cov=app`

Backend tests use FastAPI `dependency_overrides` with in-memory fakes (`tests/helpers/fakes.py`) — no Postgres or MinIO needed. The `client` fixture intentionally does not enter the lifespan context, so DB schema init is skipped.

## Architecture

Four cooperating services on the `hospital_network` bridge:

1. **backend** (FastAPI, [backend/app/main.py](backend/app/main.py)) — REST API. Routers under [backend/app/api/routers/](backend/app/api/routers/) (`health`, `triage`, `radiology`, `quality`, `metrics`) delegate to services in [backend/app/services/](backend/app/services/). All dependencies (DB session, object storage, services) are resolved through [backend/app/api/deps.py](backend/app/api/deps.py) — never instantiate them directly inside routers or services; this is what makes test overrides work.
2. **dashboard** (Flask, [dashboard/app/factory.py](dashboard/app/factory.py)) — UI. Calls the backend over HTTP via `BackendClient` and reads MinIO directly via `StorageClient`. Two blueprints: `auth` and `main`. Auth uses `werkzeug` scrypt password hashes stored in env (`ADMIN_PASSWORD_HASH`, `USER_PASSWORD_HASH`).
3. **pipeline** (PySpark, [pipeline/jobs/radiology_pipeline.py](pipeline/jobs/radiology_pipeline.py)) — one-shot batch job. Reads `data/incoming/radiology_studies.csv`, validates/partitions accepted vs. rejected rows, writes accepted JSON to `data/processed/`, writes the run report to MinIO (`pipeline-reports/`) and to Postgres (`pipeline_runs`). Submits to the standalone Spark master (`spark` + `spark-worker` containers).
4. **ml** ([ml/train_cnn.py](ml/train_cnn.py), [ml/train_triage.py](ml/train_triage.py)) — training. Outputs land in `./models/`, which is mounted **read-only** into the backend at `/models`. The contract for the CNN (label mapping, normalization) lives in [ml/model_contract.json](ml/model_contract.json) — keep it in sync with `RadiologyService` / inference code.

### Data flow

- Image upload: dashboard → `POST /radiology/predict` → backend stores object in MinIO, runs CNN (`inference_service`), persists row in `radiology_studies`, returns class + probabilities + report key.
- Triage: dashboard form → `POST /triage/assess` → sklearn model (`triage_model.joblib`) → predicted level + confidence. Low-confidence predictions (< `TRIAGE_LOW_CONFIDENCE`, default 0.55) are flagged and logged as quality events.
- Batch ingest: CSV in `data/incoming/` → Spark job → clean parquet/JSON in `data/processed/` + `pipeline_runs` row + report in `pipeline-reports/` bucket prefix.
- Metrics/quality endpoints aggregate from Postgres; the dashboard polls them.

### Configuration

Every service has a `core/config.py` that reads env vars through a typed `Settings` object via `get_settings()` (lru_cached). Required vars are declared with `${VAR:?...}` in `docker-compose.yml` — compose will refuse to start if missing. Add new config there, not via ad-hoc `os.environ` reads.

### Storage layout

- Postgres tables: `radiology_studies`, `triage_assessments`, `pipeline_runs`, `quality_events` (schema in [backend/app/db/schema.py](backend/app/db/schema.py), initialized with retry on backend startup).
- MinIO bucket (`MINIO_BUCKET_NAME`, default `hospital-data`): radiology images, per-study JSON reports, pipeline run reports. Auto-created on backend start when `MINIO_AUTO_CREATE_BUCKET=true`.

## Conventions

- Python 3.11+, `from __future__ import annotations` everywhere.
- Structured logging via `app.core.logging.get_logger`. Don't `print()`; don't reconfigure logging outside `configure_logging()`.
- Service classes take their collaborators in `__init__` (constructor injection). Tests rely on this — keep it.
- Spanish is used in user-facing strings, scripts, and the SDD ([docs/SDD.md](docs/SDD.md)). Keep code identifiers in English.
- The model file (`radiology_cnn_resnet18.pt`) is **not** in git. Train it via the `training` profile or drop a compatible artifact in `./models/` before starting the backend.
