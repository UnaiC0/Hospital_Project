# Hospital Project

Base containerizada de un sistema hospitalario con `Docker Compose`.

Incluye:

- `backend`: API REST en FastAPI
- `dashboard`: interfaz web en Flask
- `db`: PostgreSQL
- `minio`: almacenamiento de objetos compatible con S3
- `spark`: nodo master de Spark
- `spark-worker`: worker de Spark para ejecutar jobs
- `pipeline`: job Spark de ingesta, calidad y transformacion
- `model-trainer`: entrenamiento CNN bajo perfil Docker

El objetivo de esta composicion es levantar una infraestructura base, desacoplada y facil de ejecutar, sobre la que se pueda construir el resto del proyecto hospitalario.

## Arranque

Requisitos:

- Docker Desktop
- `docker compose`

Crear el archivo de entorno local copiando `.env.example` a `.env`:

```bash
cp .env.example .env
```

Levantar el entorno:

```bash
docker compose up -d
```

En Windows tambien puedes usar el script de inicio:

```bat
iniciar_proyecto.bat
```

El script comprueba `.env`, valida Docker Compose, construye las imagenes y arranca los servicios principales.

Si has cambiado contrasenas de PostgreSQL o MinIO despues de haber creado los volumenes locales, reinicializa el entorno con:

```bat
iniciar_proyecto.bat --reset-data
```

Ese comando borra los volumenes locales de PostgreSQL y MinIO antes de arrancar.

Reconstruir imagenes locales:

```bash
docker compose up --build -d
```

Ver estado:

```bash
docker compose ps
```

Ejecutar el pipeline Big Data sobre el CSV de ejemplo:

```bash
docker compose --profile pipeline up --build pipeline
```

Entrenar el modelo CNN cuando exista un dataset en `data/radiology_dataset`:

```bash
docker compose --profile training run --rm model-trainer
```

Parar el entorno:

```bash
docker compose down
```

Parar y borrar volumenes:

```bash
docker compose down -v
```

## Que hace el `docker-compose`

El archivo [docker-compose.yml](./docker-compose.yml):

- construye `backend`
- construye `dashboard`
- despliega PostgreSQL, MinIO y Spark
- despliega un worker de Spark
- define perfiles para pipeline y entrenamiento
- crea la red `hospital_network`
- crea volumenes persistentes para PostgreSQL y MinIO
- usa healthchecks para `db` y `minio`
- conecta todos los servicios para que se resuelvan por nombre dentro de Docker

En la practica, esto permite arrancar toda la plataforma con un solo comando y tener una separacion clara entre API, inferencia, almacenamiento estructurado, almacenamiento de radiografias en MinIO, procesamiento y visualizacion.

## Arquitectura

```text
Browser
  |--> http://localhost:8501  -> dashboard
                           |
                           |--> http://localhost:8000  -> backend

backend
  |--> db
  |--> minio
  |--> spark
```

## Servicios y puertos

- `dashboard` -> `http://localhost:8501`
- `backend` -> `http://localhost:8000`
- `minio` API -> `http://localhost:9000`
- `minio` consola -> `http://localhost:9001`
- `db` -> `localhost:5432`

Servicios internos no publicados al host:

- `spark` -> `spark://spark:7077`
- `spark-worker`
- `pipeline`
- `model-trainer`

### Resumen de responsabilidades

- `backend`: expone la API REST y centraliza el acceso al resto de servicios
- `backend`: incluye temporalmente la inferencia de triaje en la propia API
- `dashboard`: ofrece la interfaz de subida de radiografias y visualizacion
- `db`: almacena los registros estructurados de triaje
- `minio`: almacena radiografias y reportes JSON como objetos
- `spark`: coordina procesos distribuidos
- `spark-worker`: ejecuta trabajo distribuido
- `pipeline`: valida datos tabulares, detecta duplicados y registra calidad
- `model-trainer`: entrena una CNN ResNet18 para radiografias

## Flujo entre servicios

- El navegador entra por el `dashboard`
- `dashboard` envia la radiografia al `backend`
- `backend` ejecuta la inferencia directamente
- `backend` guarda el historial de triaje en PostgreSQL
- `backend` guarda el reporte detallado del triaje en MinIO
- `backend` guarda estudios radiologicos y reportes JSON en PostgreSQL/MinIO
- `pipeline` procesa lotes CSV con Spark y registra ejecuciones

## Variables de entorno

El repositorio incluye [.env.example](./.env.example) como plantilla y usa un archivo local `.env` para las credenciales y la configuracion del entorno.

Variables necesarias:

```env
POSTGRES_USER=hospital_user
POSTGRES_PASSWORD=replace_with_strong_postgres_password
POSTGRES_DB=hospital_db
SECRET_KEY=replace_with_random_flask_secret_key
SESSION_COOKIE_SECURE=false
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH='replace_with_werkzeug_admin_password_hash'
USER_USERNAME=doctor
USER_PASSWORD_HASH='replace_with_werkzeug_doctor_password_hash'
MINIO_ROOT_USER=hospital_minio_admin
MINIO_ROOT_PASSWORD=replace_with_strong_minio_password
MINIO_REGION=us-east-1
MINIO_BUCKET_NAME=hospital-data
MINIO_AUTO_CREATE_BUCKET=true
MINIO_CONSOLE_URL=http://localhost:9001
PIPELINE_INPUT_PATH=/data/incoming/radiology_studies.csv
PIPELINE_OUTPUT_PATH=/data/processed/radiology_clean
TRAINING_EPOCHS=5
TRAINING_BATCH_SIZE=16
TRAINING_LEARNING_RATE=0.0005
TRAINING_PRETRAINED=false
```

Estas variables se cargan automaticamente al ejecutar `docker compose`. El archivo `.env` no debe subirse a GitHub.

Las contrasenas del dashboard no se guardan en claro. Genera hashes compatibles con Werkzeug, por ejemplo:

```bash
python -c "from werkzeug.security import generate_password_hash; import getpass; print(generate_password_hash(getpass.getpass(), method='pbkdf2:sha256:1000000'))"
```

Los puertos publicados por Compose estan enlazados a `127.0.0.1`, asi que quedan accesibles desde la maquina local pero no desde otros equipos de la red.

## Persistencia y red

La infraestructura usa una red comun llamada `hospital_network`, lo que permite que todos los contenedores se comuniquen por nombre de servicio.

Ademas, se crean dos volumenes persistentes:

- `postgres_data`
- `minio_data`

Esto hace que los datos de PostgreSQL y los objetos de MinIO no se pierdan al reiniciar o recrear contenedores.

## Healthchecks y dependencias

El `docker-compose` define comprobaciones de salud para:

- `db`

El `backend` espera a que PostgreSQL y MinIO esten disponibles antes de arrancar.

## Pruebas rapidas

Comprobar salud del backend:

```bash
curl http://localhost:8000/health
```

Lanzar una simulacion de triaje:

```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/triage" `
  -ContentType "application/json" `
  -Body '{"symptoms":["fever","shortness of breath"],"vitals":{"heart_rate":125,"oxygen_saturation":90,"systolic_bp":95}}'
```

Abrir interfaces web:

- `http://localhost:8501`
- `http://localhost:8000/docs`
- `http://localhost:9001`

Endpoints utiles del backend:

- `GET /health`
- `POST /triage`
- `POST /predict`
- `GET /metrics`
- `GET /studies/history`
- `GET /studies/{study_id}`
- `GET /studies/{study_id}/report`
- `GET /quality/events`
- `GET /triage/history`
- `GET /triage/{triage_id}`
- `GET /triage/{triage_id}/report`

## Estructura del proyecto

```text
Hospital_Project/
|- backend/
|- data/
|- dashboard/
|- docs/
|- ml/
|- models/
|- pipeline/
|- .env.example
|- .gitignore
|- docker-compose.yml
`- README.md
```

## Estado actual

La infraestructura ya cubre el flujo principal del enunciado:

- `backend` funciona
- `dashboard` funciona
- La inferencia de triaje esta embebida temporalmente en el backend
- PostgreSQL ya guarda el historial estructurado de triajes
- PostgreSQL guarda estudios radiologicos, eventos de calidad y ejecuciones de pipeline
- MinIO almacena radiografias, reportes de estudios, reportes de triaje y reportes de pipeline
- Spark tiene master, worker y un job de ingesta/calidad bajo perfil `pipeline`
- El dashboard muestra subida de radiografias, resultado individual, metricas, historico y alertas
- El entrenamiento CNN esta preparado bajo perfil `training`

## Limitaciones

- El modelo activo del backend es un baseline tecnico, no un modelo clinico validado
- El entrenamiento CNN requiere incorporar un dataset real en `data/radiology_dataset`
- El dashboard tiene autenticacion basica con roles, pero no hay HTTPS integrado en Compose
- No hay cifrado de objetos en MinIO
- La monitorizacion es basica y se limita a eventos, healthchecks y registros en base de datos

## Troubleshooting

Si algo no arranca bien, los comandos mas utiles son:

```bash
docker compose ps
docker compose logs -f
```

Si algun puerto esta ocupado en tu maquina, revisa especialmente:

- `8000`
- `9000`
- `9001`
- `5432`
