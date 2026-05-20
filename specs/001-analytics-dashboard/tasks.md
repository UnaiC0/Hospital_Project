---

description: "Task list for plataforma hospitalaria de radiologia, pipeline Big Data y dashboard operativo"
---

# Tasks: Plataforma hospitalaria de radiologia, pipeline Big Data y dashboard operativo

**Input**: Design documents from `/specs/001-analytics-dashboard/`

**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Incluidos — el SDD obliga a verificar respuestas HTTP, persistencia y comportamiento del pipeline.

**Organization**: Tareas agrupadas por historia de usuario para implementacion y verificacion independiente.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias).
- **[Story]**: US1 (clasificacion), US2 (pipeline), US3 (entrenamiento), US4 (dashboard).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Esqueleto de servicios y configuracion comun.

- [X] T001 Crear estructura multi-servicio (`backend/`, `dashboard/`, `pipeline/`, `ml/`, `data/`, `models/`).
- [X] T002 [P] Definir `docker-compose.yml` con servicios `backend`, `dashboard`, `postgres`, `minio`, `spark`, `spark-worker` y perfiles `pipeline`, `training`, `triage-training`.
- [X] T003 [P] Crear `.env.example` con todos los `replace_with_*` requeridos por compose (`${VAR:?...}`).
- [X] T004 [P] Configurar `iniciar_proyecto.bat` con validacion de `.env`, espera de Docker Desktop y flags `--no-build` / `--reset-data`.
- [X] T005 [P] Configurar linting/formatting y pytest por servicio (`backend/requirements-dev.txt`, `dashboard/requirements-dev.txt`).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestructura compartida sin la que ninguna historia avanza.

- [X] T006 Implementar `backend/app/core/config.py` con `Settings` tipado y `get_settings()` cacheado.
- [X] T007 Implementar `backend/app/core/logging.py` con `configure_logging()` y `get_logger`.
- [X] T008 Definir esquema Postgres en `backend/app/db/schema.py` (`radiology_studies`, `triage_assessments`, `pipeline_runs`, `quality_events`) con init con reintentos.
- [X] T009 [P] Implementar cliente de object storage (MinIO) con autocreacion de bucket `hospital-data` cuando `MINIO_AUTO_CREATE_BUCKET=true`.
- [X] T010 [P] Crear `backend/app/api/deps.py` con providers de sesion DB, storage y servicios (base para `dependency_overrides`).
- [X] T011 [P] Crear `backend/tests/helpers/fakes.py` con fakes en memoria de DB y storage; configurar `conftest.py` para que `client` no entre en el lifespan.
- [X] T012 Registrar routers vacios `health`, `triage`, `radiology`, `quality`, `metrics` en `backend/app/main.py`.

**Checkpoint**: Infraestructura lista; las historias pueden avanzar en paralelo.

---

## Phase 3: User Story 1 - Clasificacion de radiografias en linea (Priority: P1) 🎯 MVP

**Goal**: Recibir una radiografia, validarla, clasificarla con la CNN y persistir estudio + informe.

**Independent Test**: `POST /radiology/predict` con una imagen JPG/PNG valida devuelve clase, probabilidades, confianza y `study_id`, y crea fila en `radiology_studies` + JSON en MinIO.

### Tests for User Story 1

- [X] T013 [P] [US1] Contract test de `POST /radiology/predict` (200 con payload valido, 400 con MIME/tamano invalido) en `backend/tests/unit/test_radiology_router.py`.
- [X] T014 [P] [US1] Test de `RadiologyService` con fakes en `backend/tests/unit/test_radiology_service.py` (persistencia + generacion de informe).
- [X] T015 [P] [US1] Test de `InferenceService` cargando modelo dummy y validando contrato (`ml/model_contract.json`).

### Implementation for User Story 1

- [X] T016 [P] [US1] Definir entidad `RadiologyStudy` y DTOs Pydantic en `backend/app/api/routers/radiology.py` y `backend/app/services/radiology_service.py`.
- [X] T017 [P] [US1] Implementar `inference_service` en `backend/app/services/inference_service.py` cargando `models/radiology_cnn_resnet18.pt` (read-only) segun `ml/model_contract.json`.
- [X] T018 [US1] Implementar validaciones (extension, MIME, <=5 MB) y respuesta HTTP 400 antes de invocar la CNN.
- [X] T019 [US1] Persistir estudio en `radiology_studies` y subir imagen + informe JSON al bucket bajo claves deterministas.
- [X] T020 [US1] Anadir nota clinica de limitacion en la respuesta y en el informe JSON.
- [X] T021 [US1] Logging estructurado de cada prediccion (sin datos sensibles) via `get_logger`.

**Checkpoint**: US1 funcional end-to-end e independientemente verificable.

---

## Phase 4: User Story 2 - Pipeline Big Data de estudios radiologicos (Priority: P2)

**Goal**: Ejecutar el job Spark que limpia el CSV, registra la ejecucion y emite eventos de calidad.

**Independent Test**: `docker compose --profile pipeline up pipeline` con un CSV valido produce `data/processed/radiology_clean`, fila en `pipeline_runs` e informe en `pipeline-reports/`.

### Tests for User Story 2

- [X] T022 [P] [US2] Test de validacion de schema (columnas obligatorias) en `pipeline/tests/test_schema.py`.
- [X] T023 [P] [US2] Test de deduplicacion y particion rechazada en `pipeline/tests/test_partitioning.py`.

### Implementation for User Story 2

- [X] T024 [US2] Implementar `pipeline/jobs/radiology_pipeline.py`: lectura CSV, validacion de columnas y etiquetas, deduplicacion por `study_id`.
- [X] T025 [US2] Escribir aceptados a `data/processed/radiology_clean` y rechazados a particion separada.
- [X] T026 [US2] Generar informe JSON en MinIO bajo prefijo `pipeline-reports/` y fila en `pipeline_runs`.
- [X] T027 [US2] Emitir `quality_events` cuando existan registros rechazados.
- [X] T028 [US2] Configurar submit al master Spark standalone (`spark` + `spark-worker`) en el perfil `pipeline`.

**Checkpoint**: US1 y US2 funcionan de forma independiente.

---

## Phase 5: User Story 3 - Entrenamiento de la CNN (Priority: P3)

**Goal**: Entrenar la ResNet18 y producir artefacto + metricas + matriz de confusion.

**Independent Test**: `docker compose --profile training up model-trainer` con dataset organizado genera `models/radiology_cnn_resnet18.pt`, `models/radiology_cnn_metrics.json` y la matriz de confusion.

### Tests for User Story 3

- [X] T029 [P] [US3] Test que comprueba el chequeo de estructura del dataset (mensaje claro cuando falta).

### Implementation for User Story 3

- [X] T030 [US3] Implementar `ml/train_cnn.py`: carga del dataset, transforms, entrenamiento ResNet18, soporte `TRAINING_PRETRAINED`.
- [X] T031 [US3] Volcar artefactos a `./models/` (`radiology_cnn_resnet18.pt`, `radiology_cnn_metrics.json`, matriz de confusion).
- [X] T032 [US3] Mantener `ml/model_contract.json` sincronizado con label map y normalizacion usados por `InferenceService`.
- [X] T033 [US3] Definir servicio `model-trainer` bajo perfil Docker `training` (requiere GPU NVIDIA).

**Checkpoint**: El entrenamiento es reproducible y no impacta el arranque normal del stack.

---

## Phase 6: User Story 4 - Dashboard operativo unificado (Priority: P2)

**Goal**: UI para subir radiografias, ver resultados, historico y estado del pipeline/calidad.

**Independent Test**: Abrir el dashboard con backend vacio (sin errores), procesar una imagen y comprobar que aparece en historico; ver estado del pipeline tras una ejecucion.

### Tests for User Story 4

- [X] T034 [P] [US4] Test del `BackendClient` con respuestas mock (rutas `/metrics`, `/studies/history`, `/quality/events`).
- [X] T035 [P] [US4] Test de blueprint `auth` con scrypt (`ADMIN_PASSWORD_HASH`, `USER_PASSWORD_HASH`).

### Implementation for User Story 4

- [X] T036 [US4] Implementar `dashboard/app/factory.py` con blueprints `auth` y `main`.
- [X] T037 [US4] Implementar `BackendClient` (HTTP al backend) y `StorageClient` (lectura directa de MinIO).
- [X] T038 [US4] Pantalla de subida de radiografia + render de resultado individual con nota clinica.
- [X] T039 [US4] Vistas de historico de estudios, estado del pipeline y eventos de calidad consumiendo `/metrics`, `/studies/history`, `/quality/events`.
- [X] T040 [US4] Estados vacios y degradados para cuando el backend no devuelve datos.

**Checkpoint**: Las cuatro historias funcionan independientemente y de forma integrada.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [X] T041 [P] Actualizar `docs/SDD.md` y `CLAUDE.md` con la arquitectura final.
- [X] T042 [P] Endurecer binding a `127.0.0.1` en compose para todos los servicios expuestos.
- [X] T043 Revision de logging y eliminacion de `print` residuales.
- [X] T044 Quickstart manual: primer arranque con `iniciar_proyecto.bat` desde `.env.example`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sin dependencias.
- **Foundational (Phase 2)**: depende de Setup; bloquea todas las historias.
- **US1 (Phase 3)**: depende de Foundational. MVP.
- **US2 (Phase 4)**: depende de Foundational; integra con el catalogo de estudios pero se ejecuta de forma aislada.
- **US3 (Phase 5)**: depende de Foundational; produce el artefacto que consume US1 pero puede entregarse despues con un modelo placeholder.
- **US4 (Phase 6)**: depende de Foundational; consume endpoints de US1 y US2 pero debe degradar limpiamente si no hay datos.
- **Polish (Phase 7)**: tras completar las historias deseadas.

### Within Each User Story

- Tests marcados [P] se escriben antes que la implementacion y deben fallar inicialmente.
- Modelos/DTOs antes que servicios; servicios antes que endpoints; endpoints antes que UI.

### Parallel Opportunities

- Toda la Phase 1 puede paralelizarse salvo T001.
- En Phase 2, T009/T010/T011 pueden ir en paralelo tras T006-T008.
- Una vez completada Foundational, US1, US2, US3 y US4 pueden avanzar en paralelo con distintos desarrolladores.

---

## Implementation Strategy

### MVP First (US1 only)

1. Phase 1 → Phase 2 → Phase 3.
2. Validar `POST /radiology/predict` end-to-end con un modelo placeholder.
3. Demo.

### Incremental Delivery

1. MVP con US1.
2. + US4 (dashboard sobre US1) — entrega valor visible.
3. + US2 (pipeline Big Data).
4. + US3 (entrenamiento real para refrescar el modelo).

---

## Notes

- Identificadores en ingles, strings de usuario en espanol.
- El modelo `radiology_cnn_resnet18.pt` no se commitea; debe generarse via perfil `training` o aportarse manualmente antes de iniciar el backend.
- Tests del backend usan `dependency_overrides` y NO requieren Postgres/MinIO reales.
- Cualquier nueva configuracion se declara en `core/config.py` y `docker-compose.yml`, nunca via `os.environ` ad-hoc.
