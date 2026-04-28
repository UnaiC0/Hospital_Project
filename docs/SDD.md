# Spec-Driven Development

## Componente 1: clasificacion de radiografias

Descripcion funcional:
El sistema recibe una radiografia de torax en JPG o PNG, valida el archivo, genera una clasificacion entre `Sana`, `Neumonia` y `COVID-19`, guarda el estudio en PostgreSQL y emite un informe JSON en MinIO.

Inputs:
- Imagen medica en JPG, JPEG o PNG.
- Clave del objeto subido a MinIO, cuando la imagen entra desde el dashboard.

Outputs:
- Clase predicha.
- Probabilidades por clase.
- Confianza de la prediccion.
- `study_id` persistido.
- Informe JSON consultable desde MinIO.

Restricciones:
- Tamano maximo de 5 MB.
- No se aceptan extensiones o MIME types fuera de JPG/PNG.
- Toda prediccion debe ir acompanada de nota clinica de limitacion.

Criterios de aceptacion:
- Una imagen valida devuelve HTTP 200 y queda registrada en `radiology_studies`.
- Una imagen invalida devuelve HTTP 400.
- El dashboard muestra el resultado y el objeto de informe.

## Componente 2: pipeline Big Data

Descripcion funcional:
El pipeline Spark ingiere un CSV de estudios radiologicos, valida registros, detecta duplicados, separa datos rechazados, escribe datos limpios y registra la ejecucion.

Inputs:
- `data/incoming/radiology_studies.csv`.

Outputs:
- Datos limpios en `data/processed/radiology_clean`.
- Registro en `pipeline_runs`.
- Informe JSON en `pipeline-reports/`.
- Eventos de calidad si hay datos rechazados.

Restricciones:
- Columnas obligatorias: `study_id`, `patient_age`, `patient_sex`, `image_object_key`, `label`, `acquisition_date`, `source`.
- Etiquetas validas: `Sana`, `Neumonia`, `COVID-19`.

Criterios de aceptacion:
- El job se ejecuta con `docker compose --profile pipeline up pipeline`.
- Los registros duplicados o incompletos quedan rechazados.
- El dashboard refleja la ultima ejecucion.

## Componente 3: entrenamiento CNN

Descripcion funcional:
El modulo `model-trainer` entrena una CNN ResNet18 para clasificar radiografias en tres clases.

Inputs:
- Dataset en `data/radiology_dataset/train/<clase>` y `data/radiology_dataset/val/<clase>`.

Outputs:
- Modelo `models/radiology_cnn_resnet18.pt`.
- Metricas `models/radiology_cnn_metrics.json`.
- Matriz de confusion.

Restricciones:
- El entrenamiento esta en perfil Docker `training` para no hacer pesado el arranque normal.
- El uso de pesos preentrenados es opcional mediante `TRAINING_PRETRAINED=true`.

Criterios de aceptacion:
- Si falta el dataset, el contenedor informa la estructura esperada.
- Si el dataset existe, genera modelo y metricas.

## Componente 4: dashboard operativo

Descripcion funcional:
El dashboard permite subir radiografias, revisar predicciones, consultar almacenamiento MinIO y ver metricas operativas del sistema.

Inputs:
- Imagen de radiografia.
- Datos agregados desde `/metrics`, `/studies/history` y `/quality/events`.

Outputs:
- Vista previa.
- Resultado individual.
- Historico de estudios.
- Estado del pipeline y eventos de calidad.

Criterios de aceptacion:
- El dashboard funciona aunque el backend no tenga datos.
- Los nuevos estudios aparecen en el panel tras procesar imagenes.
