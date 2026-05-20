# Implementation Plan: Plataforma hospitalaria de radiologia, pipeline Big Data y dashboard operativo

**Branch**: `001-analytics-dashboard` | **Date**: 2026-05-18 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-analytics-dashboard/spec.md`

## Summary

Sistema integrado de cuatro servicios cooperantes sobre Docker Compose: un backend FastAPI que clasifica radiografias con una CNN ResNet18 y persiste estudios en PostgreSQL/MinIO; un pipeline PySpark on-demand que ingiere CSVs de estudios, valida y limpia datos, y registra ejecuciones; un trainer ML que produce el artefacto del modelo y sus metricas; y un dashboard Flask que orquesta la interaccion humana sobre estos servicios. El enfoque tecnico prioriza una API REST con inyeccion de dependencias para tests deterministas, perfiles Docker para cargas pesadas (pipeline/training) y MinIO como object storage compartido.

## Technical Context

**Language/Version**: Python 3.11+ (`from __future__ import annotations` en todos los modulos).

**Primary Dependencies**: FastAPI (backend), Flask + Jinja (dashboard), PySpark (pipeline), PyTorch + torchvision (entrenamiento e inferencia CNN), scikit-learn (triage), SQLAlchemy/psycopg (Postgres), boto3/minio (object storage).

**Storage**: PostgreSQL (`radiology_studies`, `triage_assessments`, `pipeline_runs`, `quality_events`) + MinIO (`hospital-data` bucket: imagenes, informes JSON, reportes de pipeline).

**Testing**: pytest por servicio con `dependency_overrides` y fakes en memoria; no requiere Postgres/MinIO reales.

**Target Platform**: Linux containers orquestados con Docker Compose en host unico. Servicios expuestos en `127.0.0.1`.

**Project Type**: Sistema multi-servicio (web-service + batch + ML).

**Performance Goals**: Latencia interactiva de prediccion < 2 s p95 sobre CPU; pipeline capaz de procesar CSVs de hasta ~1M filas en una sola ejecucion local.

**Constraints**: Imagen <= 5 MB, MIME estricto JPG/PNG, `models/` montado read-only en backend, modelo CNN no versionado en git.

**Scale/Scope**: 4 servicios, 4 historias de usuario, ~5 tablas Postgres, 1 bucket MinIO con tres prefijos logicos (imagenes, informes, pipeline-reports).

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Inyeccion de dependencias en routers/servicios via `app.api.deps`: PASS.
- Logging estructurado via `app.core.logging.get_logger`, sin `print`: PASS.
- Configuracion declarada en `core/config.py` + `${VAR:?}` en compose: PASS.
- Spanish en UI/SDD, identificadores de codigo en ingles: PASS.
- Sin violaciones que justificar.

## Project Structure

### Documentation (this feature)

```text
specs/001-analytics-dashboard/
├── spec.md              # Especificacion funcional
├── plan.md              # Este archivo
├── tasks.md             # Lista de tareas ejecutables
└── checklists/          # Listas de verificacion auxiliares
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   │   ├── deps.py
│   │   └── routers/         # health, triage, radiology, quality, metrics
│   ├── services/            # radiology_service, inference_service, pipeline_service, quality_service
│   ├── db/
│   │   └── schema.py
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   └── main.py
└── tests/
    ├── unit/
    ├── integration/
    └── helpers/fakes.py

dashboard/
├── app/
│   ├── factory.py
│   ├── blueprints/          # auth, main
│   └── clients/             # BackendClient, StorageClient
└── tests/

pipeline/
└── jobs/
    └── radiology_pipeline.py

ml/
├── train_cnn.py
├── train_triage.py
└── model_contract.json

models/                     # artefactos (no versionados); montado read-only en backend
data/
├── incoming/                # CSVs de entrada al pipeline
├── processed/               # salida limpia del pipeline
└── radiology_dataset/{train,val}/<clase>/
```

**Structure Decision**: Cuatro servicios independientes con su propio `requirements.txt` y `requirements-dev.txt`, orquestados con `docker-compose.yml`. Los perfiles `pipeline`, `training` y `triage-training` aislan cargas pesadas. El contrato del modelo (`ml/model_contract.json`) se sincroniza con `RadiologyService` en backend.

## Complexity Tracking

> Sin violaciones que justificar. La separacion en cuatro servicios responde a fronteras tecnologicas reales (FastAPI vs Flask vs Spark vs PyTorch) y no a sobre-ingenieria.
