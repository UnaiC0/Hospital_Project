# Memoria tecnica

## Descripcion del problema

LaSalle Health Center necesita una plataforma que ayude a organizar datos clinicos, procesar radiografias de torax y comunicar resultados de forma interpretable. El prototipo implementa un flujo hospitalario completo: ingesta de imagenes, almacenamiento, clasificacion, persistencia, informes, calidad de datos y visualizacion.

## Datos

El proyecto trabaja con datos no estructurados, radiografias de torax, y datos tabulares simulados en `data/incoming/radiology_studies.csv`.

Proceso de tratamiento:
- Ingesta desde dashboard y CSV.
- Validacion de formato, tamano, extension y contenido de imagen.
- Validacion tabular de columnas obligatorias, etiquetas y duplicados.
- Transformacion con Spark hacia `data/processed/radiology_clean`.
- Servicio de resultados mediante API REST y dashboard.

## Arquitectura del sistema

Servicios principales:
- `backend`: API FastAPI, persistencia y logica de negocio.
- `dashboard`: interfaz Flask para carga, resultados y metricas.
- `db`: PostgreSQL para estudios, triajes, eventos y ejecuciones.
- `minio`: almacenamiento de imagenes e informes JSON.
- `spark` y `spark-worker`: infraestructura de procesamiento distribuido.
- `pipeline`: job Spark ejecutable bajo perfil.
- `model-trainer`: entrenamiento CNN bajo perfil.

El flujo principal es: navegador -> dashboard -> MinIO -> backend -> PostgreSQL/MinIO -> dashboard.

## Modelos de Inteligencia Artificial

El backend incluye un clasificador basal de imagen que utiliza estadisticos de intensidad y contraste para mantener el sistema operativo sin dataset externo. No debe presentarse como modelo clinico final.

Para el triaje de urgencias el repositorio incluye `ml/train_triage.py`, que entrena un Random Forest calibrado isotonicamente sobre cuatro clases de riesgo (`low`, `medium`, `high`, `critical`). Se ha elegido Random Forest porque los datos son tabulares y de pequena escala, requiere alta interpretabilidad clinica y permite extraer probabilidades calibradas e importancia de variables sin GPU. El dataset es sintetico, inspirado en MEWS/NEWS2, con ruido controlado en las etiquetas para forzar generalizacion. El artefacto se guarda en `models/triage_model.joblib` y lo consume el backend a traves de `backend/app/triage_model.py`, con fallback automatico al baseline por reglas si el modelo no esta disponible. Para entrenar: `docker compose --profile triage-training up triage-trainer`.

Para cubrir el modulo de Deep Learning, el repositorio incluye `ml/train_cnn.py`, que entrena una ResNet18 sobre tres clases: `Sana`, `Neumonia` y `COVID-19`. El entrenamiento genera:
- Pesos del modelo.
- Accuracy de validacion.
- Classification report.
- Matriz de confusion.

La evaluacion debe centrarse en falsos negativos de COVID-19 y confusiones COVID-19/Neumonia por su impacto clinico.

## Automatizaciones

Automatizaciones implementadas:
- Creacion automatica del bucket MinIO.
- Generacion automatica de informes JSON por estudio.
- Registro automatico de eventos ante COVID-19, baja confianza o mala calidad de imagen.
- Pipeline Spark que detecta registros incompletos, duplicados o etiquetas invalidas.

## Integraciones

Integraciones actuales:
- Dashboard con backend mediante HTTP.
- Backend con PostgreSQL mediante `psycopg`.
- Backend y dashboard con MinIO mediante API S3.
- Pipeline con Spark, PostgreSQL y MinIO.

## Justificaciones tecnicas

PostgreSQL se usa para entidades estructuradas y consultas operativas. MinIO se usa para objetos no estructurados e informes JSON. Spark permite escalar el procesamiento de lotes aunque el volumen del prototipo sea pequeno. Docker Compose facilita reproducibilidad y separacion de responsabilidades.

## Limitaciones

El clasificador activo del backend es un baseline interpretable, no un modelo entrenado clinicamente. El entrenamiento real depende de incorporar un dataset balanceado y documentado. No existe autenticacion ni control de acceso, por lo que no debe desplegarse en un entorno real con datos sensibles.

## Mejoras futuras

- Conectar el backend al artefacto entrenado por `model-trainer`.
- Anadir autenticacion y roles.
- Incorporar tests automatizados.
- Anadir observabilidad con Prometheus/Grafana o logs centralizados.
- Validar el modelo con especialistas clinicos.
