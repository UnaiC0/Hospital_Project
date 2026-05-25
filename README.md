# Sistema Inteligente de Soporte Hospitalario
### LaSalle Health Center · Aprendizaje Automático / Big Data

> Plataforma containerizada de IA y Big Data para clasificación radiológica y triaje clínico.  
> Todo el sistema arranca con **un único comando**.

Desarrollado por **Oriol Fontcuberta**, **Unai Canet** y **Albert Garrido**  
Asignatura: *Sistemes d'Aprenentatge Automatic / Big Data* · Entrega: 2026-05-20

---

## Qué hace este proyecto

Este sistema simula una plataforma real de soporte clínico para un hospital de tamaño medio. No es solo un modelo de IA aislado — es una pila completa de servicios que trabajan juntos:

- **Clasifica radiografías de tórax** en tres categorías (Sana, Neumonía, COVID-19) usando una CNN ResNet18 con 93.94% de accuracy en test.
- **Evalúa la gravedad de pacientes en urgencias** (triaje) con un Random Forest calibrado, asignando nivel low / medium / high / critical.
- **Procesa grandes volúmenes de datos** en batch mediante un pipeline Apache Spark que valida, limpia y registra lotes de estudios desde CSV.
- **Genera informes automáticos** en MinIO (compatible S3) para cada predicción, triaje y ejecución del pipeline.
- **Dispara alertas de calidad** automáticamente ante casos críticos, predicciones de baja confianza o datos rechazados.
- **Lo muestra todo** en un dashboard web con autenticación, historial y panel de eventos.

---

## Arquitectura rápida

```
Browser
  └─> Dashboard Flask :8501
        ├─> Backend FastAPI :8000
        │     ├─> PostgreSQL :5432   (estudios, triajes, eventos)
        │     ├─> MinIO :9000        (imágenes, informes JSON)
        │     └─> Modelos IA         (ResNet18 + Random Forest)
        └─> MinIO :9000              (subida directa de imágenes)

Pipeline Spark (on-demand)
  └─> Lee CSV ──> valida ──> PostgreSQL + MinIO
```

Nueve servicios Docker coordinados por Compose sobre una red interna (`hospital_network`). Cada uno tiene una responsabilidad única y se comunica por protocolos estándar (HTTP, S3, psycopg).

---

## Requisitos previos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y en ejecución
- Windows 10/11 (el launcher usa `.bat`; en Linux/Mac basta con `docker compose up -d --build`)
- Para el entrenamiento de la CNN: GPU NVIDIA con drivers actualizados (opcional)

No necesitas Python, Spark ni ninguna otra dependencia instalada localmente. Todo corre dentro de los contenedores.

---

## Puesta en marcha

### 1. Clonar el repositorio

```bash
git clone https://github.com/UnaiC0/Hospital_Project.git
cd Hospital_Project
```

### 2. Configurar el entorno

Copia el fichero de ejemplo y rellena los valores marcados como `replace_with_*`:

```bash
cp .env.example .env
# Edita .env con tu editor favorito
```

Los únicos valores que **debes** cambiar antes de arrancar:

| Variable | Qué poner |
|---|---|
| `POSTGRES_PASSWORD` | Cualquier contraseña segura |
| `MINIO_ROOT_PASSWORD` | Cualquier contraseña segura (mín. 8 caracteres) |
| `SECRET_KEY` | Una cadena aleatoria larga (para firmar sesiones Flask) |

El resto de variables ya tienen valores por defecto funcionales. Los hashes de contraseña incluidos en `.env.example` corresponden a `Hospital2026!` (admin) y `Doctor2026!` (user).

### 3. Arrancar

```bash
# Windows
iniciar_proyecto.bat

# Linux / Mac
docker compose up -d --build
```

El script de Windows valida que Docker esté activo, comprueba que `.env` está bien configurado (sin placeholders sin rellenar) y arranca todos los servicios. La primera vez tarda unos minutos mientras descarga las imágenes base.

### 4. Acceder

| Servicio | URL | Credenciales por defecto |
|---|---|---|
| Dashboard | http://localhost:8501 | admin / `Hospital2026!` |
| Backend API | http://localhost:8000 | — |
| Documentación API | http://localhost:8000/docs | — |
| Consola MinIO | http://localhost:9001 | `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` del `.env` |

---

## Opciones del launcher (Windows)

```bash
iniciar_proyecto.bat                   # Arranca construyendo imágenes
iniciar_proyecto.bat --no-build        # Arranca sin reconstruir (más rápido si ya tienes imágenes)
iniciar_proyecto.bat --reset-data      # Borra volúmenes de PostgreSQL y MinIO antes de arrancar
iniciar_proyecto.bat --reset-data --yes  # Lo mismo pero sin pedir confirmación
```

> **Cuándo usar `--reset-data`**: si cambias `POSTGRES_PASSWORD` en `.env` después del primer arranque, Postgres rechazará la conexión porque el volumen guardó la contraseña anterior. Con `--reset-data` se borran los datos y se reinicializa todo.

---

## Servicios y perfiles Docker

Por defecto arrancan los servicios principales. Los trabajos pesados (pipeline, entrenamiento) usan **perfiles** para no interferir con el flujo normal:

```bash
# Pipeline Spark — procesa data/incoming/radiology_studies.csv
docker compose --profile pipeline up --build pipeline

# Entrenamiento CNN (requiere GPU NVIDIA)
docker compose --profile training up --build model-trainer

# Entrenamiento Random Forest de triaje
docker compose --profile triage-training up --build triage-trainer
```

Servicios que arrancan **siempre**: `backend`, `dashboard`, `db`, `minio`, `spark`, `spark-worker`.

---

## Modelos de IA

### CNN ResNet18 — Clasificación de radiografías

Red neuronal con 11.7M parámetros entrenada sobre el [COVID-19 Radiography Database](https://www.kaggle.com/datasets/tawsifurrahman/covid19-radiography-database) de Kaggle.

- **Accuracy en test: 93.94%** (1.288 imágenes)
- Recall COVID-19: **0.983** — de 116 casos, solo 2 falsos negativos, ninguno confundido con Neumonía
- Preprocesado: resize 224×224, normalización ImageNet, data augmentation (flip + rotación 8°)
- El artefacto entrenado (`radiology_cnn_resnet18.pt`) no está en git. Entrénalo con el perfil `training` o descárgalo aparte y colócalo en `./models/`.

### Random Forest calibrado — Triaje clínico

400 árboles con calibración isotónica sobre 17 variables (6 vitales + 10 síntomas binarios).

- **Accuracy global: 80.6%** — Clase *critical*: precision 0.97 / recall 0.92
- Generado con un dataset sintético de 8.000 muestras siguiendo reglas MEWS/NEWS2
- Artefacto incluido en `./models/triage_model.joblib`
- Si el modelo no está disponible al arrancar, el backend activa automáticamente una heurística de reglas como *safety net*

---

## Ejecutar los tests

Cada servicio tiene su propia suite de pytest. No necesitas Docker levantado para los tests unitarios.

```bash
# Backend (desde la carpeta backend/)
cd backend
pip install -r requirements-dev.txt
pytest

# Con cobertura
pytest --cov=app

# Un test concreto
pytest tests/unit/test_radiology_service.py::test_predict_valid_image

# Dashboard
cd dashboard
pip install -r requirements-dev.txt
pytest
```

Los tests del backend usan `dependency_overrides` de FastAPI con fakes en memoria — ni PostgreSQL ni MinIO son necesarios. La cobertura de lógica de negocio supera el 90%.

---

## Pipeline Big Data

El pipeline Spark ingiere el fichero `data/incoming/radiology_studies.csv`, valida cada registro, detecta duplicados y produce:

1. Datos limpios en `data/processed/radiology_clean/` (JSON)
2. Registro de ejecución en PostgreSQL (`pipeline_runs`)
3. Informe detallado en MinIO (`pipeline-reports/<run_id>.json`)
4. Eventos de calidad en `quality_events` si hay rechazos o fallos

**Columnas obligatorias del CSV:** `study_id`, `patient_age`, `patient_sex`, `image_object_key`, `label`, `acquisition_date`, `source`

**Etiquetas válidas:** `Sana`, `Neumonia`, `COVID-19`

```bash
# Lanzar el pipeline
docker compose --profile pipeline up --build pipeline

# Ver logs en tiempo real
docker compose logs -f pipeline
```

---

## Automatizaciones incluidas

El sistema genera eventos de calidad y actúa de forma autónoma sin intervención manual:

| Cuándo | Severidad | Dónde se ve |
|---|---|---|
| La CNN detecta COVID-19 | HIGH | Dashboard → Eventos |
| Confianza de predicción < 0.55 | MEDIUM | Dashboard → Eventos |
| El pipeline rechaza registros | MEDIUM | Dashboard → Eventos |
| El pipeline falla completamente | HIGH | Dashboard → Eventos |
| Triaje clasifica paciente como critical | HIGH | Dashboard → Eventos |

Además, el bucket de MinIO se crea automáticamente al primer arranque, y el backend espera a que PostgreSQL y MinIO estén sanos antes de inicializarse.

---

## Estructura del repositorio

```
Hospital_Project/
├── backend/              FastAPI modular en capas (api/services/repositories/db/storage)
│   ├── app/
│   │   ├── api/          Routers HTTP y inyección de dependencias
│   │   ├── services/     Lógica de negocio
│   │   ├── repositories/ Acceso a PostgreSQL
│   │   ├── db/           Pool de conexiones y transacciones ACID
│   │   ├── storage/      Adaptador S3/MinIO (boto3)
│   │   └── schemas/      DTOs Pydantic
│   └── tests/            24 archivos de test (unit + api)
│
├── dashboard/            Flask con app factory y blueprints
│   ├── app/
│   │   ├── blueprints/   /login, /upload, /triage, /history, /events
│   │   ├── services/     Clientes HTTP y S3
│   │   └── templates/    Jinja2
│   └── tests/
│
├── pipeline/             Job Spark modular
│   ├── app/
│   │   ├── core/         SparkSession factory, config, logging
│   │   ├── validators/   Schema del CSV
│   │   ├── transforms/   Filtrado y deduplicación
│   │   └── writers/      PostgreSQL + MinIO
│   └── jobs/
│       └── radiology_pipeline.py
│
├── ml/
│   ├── train_cnn.py      Entrenamiento ResNet18
│   ├── train_triage.py   Entrenamiento Random Forest
│   └── model_contract.json  Contrato de inferencia (clases, normalización)
│
├── models/               Artefactos de modelos (montado read-only en backend)
├── data/
│   ├── incoming/         CSV de entrada para el pipeline
│   └── processed/        Salida limpia del pipeline
│
├── docs/                 Memoria técnica (PDF) y SDD
├── docker-compose.yml
├── iniciar_proyecto.bat  Launcher para Windows
└── .env.example
```

---

## Stack tecnológico

| Área | Tecnología | Versión |
|---|---|---|
| Backend API | FastAPI + Pydantic | 0.11x |
| Dashboard | Flask + Jinja2 | — |
| Base de datos | PostgreSQL | 16.13-alpine |
| Object storage | MinIO | RELEASE.2024-01-11 |
| Big Data | Apache Spark (PySpark) | 3.5.8 |
| IA — visión | PyTorch + torchvision (ResNet18) | — |
| IA — triaje | scikit-learn (Random Forest) | — |
| Orquestación | Docker Compose | — |
| CI/CD | GitHub Actions (pytest + compose config) | — |
| Driver PostgreSQL | psycopg2 (pool 2–10) | — |
| Driver MinIO/S3 | boto3 | — |

---

## Comandos útiles del día a día

```bash
# Ver estado de todos los contenedores
docker compose ps

# Logs en tiempo real (todos los servicios)
docker compose logs -f

# Logs de un servicio concreto
docker compose logs -f backend

# Parar todo sin borrar datos
docker compose down

# Parar y borrar volúmenes (PostgreSQL + MinIO)
docker compose down -v

# Acceder al shell del backend
docker compose exec backend bash

# Validar el fichero docker-compose.yml sin arrancar
docker compose config
```

---

## Consideraciones éticas y legales

Este proyecto es un **prototipo académico**. Algunas cosas importantes a tener en cuenta:

- **No está validado clínicamente.** La CNN tiene 93.94% de accuracy en test público, pero esto no es suficiente para uso clínico real. Requiere validación por radiólogos, datos hospitalarios reales y certificación MDR (Reglamento UE 2017/745).
- **El triaje usa datos sintéticos.** Un despliegue real exigiría reentrenamiento con datos anonimizados del hospital y validación frente a protocolos MEWS/NEWS2 vigentes.
- **El sistema es una herramienta de apoyo, no un sustituto del criterio clínico.** Cada predicción incluye una nota explícita: *resultado de apoyo, no diagnóstico*.
- **Sin cifrado en reposo.** En producción sería obligatorio: SSE-S3/KMS en MinIO, LUKS en PostgreSQL, TLS en todos los flujos.
- **Los datos clínicos son datos especiales (Art. 9 RGPD).** Usar exclusivamente con datos anonimizados, sintéticos o simulados.

---

## Limitaciones conocidas

Documentamos abiertamente lo que este prototipo no hace (aún):

- Sin HTTPS entre servicios internos
- Sin scheduler de pipeline (Airflow/Prefect): el pipeline es on-demand
- Sin SSO corporativo (OAuth2/OIDC)
- Sin alta disponibilidad: una instancia de cada servicio, sin failover
- Dataset radiográfico no incluido en el repo (hay que descargarlo de Kaggle para reentrenar)

---

## Licencia

Proyecto académico desarrollado para la asignatura *Sistemes d'Aprenentatge Automatic / Big Data* en La Salle - Universitat Ramon Llull. No tiene licencia de uso comercial.
