# Hospital Project

Base containerizada de un sistema hospitalario con `Docker Compose`.

Incluye:

- `backend`: API REST en FastAPI
- `dashboard`: interfaz web en Flask
- `db`: PostgreSQL
- `minio`: almacenamiento de objetos compatible con S3
- `spark`: nodo master de Spark

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

Reconstruir imagenes locales:

```bash
docker compose up --build -d
```

Ver estado:

```bash
docker compose ps
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
- crea la red `hospital_network`
- crea volumenes persistentes para PostgreSQL y MinIO
- usa healthchecks para `db`
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

### Resumen de responsabilidades

- `backend`: expone la API REST y centraliza el acceso al resto de servicios
- `backend`: incluye temporalmente la inferencia de triaje en la propia API
- `dashboard`: ofrece la interfaz de subida de radiografias y visualizacion
- `db`: almacena los registros estructurados de triaje
- `minio`: almacena radiografias y reportes JSON como objetos
- `spark`: base para futuros procesos distribuidos

## Flujo entre servicios

- El navegador entra por el `dashboard`
- `dashboard` envia la radiografia al `backend`
- `backend` ejecuta la inferencia directamente
- `backend` guarda el historial de triaje en PostgreSQL
- `backend` guarda el reporte detallado del triaje en MinIO
- `backend` mantiene la conexion a Spark preparada para evolucionar el pipeline

## Variables de entorno

El repositorio incluye [.env.example](./.env.example) como plantilla y usa un archivo local `.env` para las credenciales y la configuracion del entorno.

Variables necesarias:

```env
POSTGRES_USER=hospital_user
POSTGRES_PASSWORD=change_me_postgres_password
POSTGRES_DB=hospital_db
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=change_me_minio_password
MINIO_REGION=us-east-1
MINIO_BUCKET_NAME=hospital-data
MINIO_AUTO_CREATE_BUCKET=true
MINIO_CONSOLE_URL=http://localhost:9001
```

Estas variables se cargan automaticamente al ejecutar `docker compose`. El archivo `.env` no debe subirse a GitHub.

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
- `GET /triage/history`
- `GET /triage/{triage_id}`
- `GET /triage/{triage_id}/report`

## Estructura del proyecto

```text
Hospital_Project/
|- backend/
|- dashboard/
|- .env.example
|- .gitignore
|- docker-compose.yml
`- README.md
```

## Estado actual

La infraestructura esta operativa, pero el proyecto aun es una base tecnica:

- `backend` funciona
- `dashboard` funciona
- La inferencia de triaje esta embebida temporalmente en el backend
- PostgreSQL ya guarda el historial estructurado de triajes
- MinIO almacena radiografias y reportes desde el backend y el dashboard
- Spark esta desplegado, pero aun no ejecuta jobs del proyecto

## Limitaciones

- El backend todavia no usa tablas clinicas complejas, solo registros de triaje
- No hay pipeline real de ingesta, limpieza o transformacion
- Spark aun no esta conectado a procesamiento real
- El modelo de IA actual no es un modelo clinico entrenado

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
