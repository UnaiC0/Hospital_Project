<!--
SYNC IMPACT REPORT
==================
Version change: (uninitialized template) → 1.0.0
Bump rationale: MAJOR — primera ratificación. Se sustituyen todos los
placeholders del template por principios y normas concretas. Al no existir
versión previa publicada con principios materiales, se adopta 1.0.0 como
línea base estable según semver.

Principios renombrados / definidos:
  - [PRINCIPLE_1_NAME] → I. Seguridad Clínica y Limitación de Diagnóstico
  - [PRINCIPLE_2_NAME] → II. Calidad y Validación de Datos
  - [PRINCIPLE_3_NAME] → III. Reproducibilidad de Modelos y Pipelines
  - [PRINCIPLE_4_NAME] → IV. Pruebas Antes que Implementación (NO NEGOCIABLE)
  - [PRINCIPLE_5_NAME] → V. Observabilidad y Auditabilidad

Secciones añadidas:
  - Restricciones Adicionales (stack, contenedores, almacenamiento)
  - Flujo de Desarrollo y Puertas de Calidad
  - Governance

Secciones eliminadas: ninguna (sustitución directa de los placeholders).

Plantillas verificadas:
  - ✅ .specify/templates/plan-template.md — referencia genérica a
    "Constitution Check"; compatible con los principios definidos.
  - ✅ .specify/templates/spec-template.md — alineado, no requiere cambios.
  - ✅ .specify/templates/tasks-template.md — alineado, no requiere cambios.
  - ✅ .specify/templates/constitution-template.md — base de este documento.
  - ✅ CLAUDE.md — referencia al plan vigente, sin contradicciones.

Follow-up TODOs: ninguno. Fecha de ratificación confirmada por el usuario.
-->

# Hospital Project Constitution

## Core Principles

### I. Seguridad Clínica y Limitación de Diagnóstico

Ninguna predicción del sistema (radiología, triage u otros componentes
clínicos) se considera diagnóstico autónomo. Toda salida que pueda interpretarse
como conclusión médica DEBE acompañarse de:

- Clase predicha, probabilidades por clase y confianza explícita.
- Nota de limitación clínica visible para el usuario final, indicando que el
  resultado es asistivo y requiere validación profesional.
- Trazabilidad al `study_id` y al modelo (nombre + versión) que produjo la
  predicción.

Rationale: el sistema procesa imágenes y datos sanitarios. La omisión del
disclaimer o de la trazabilidad transformaría una herramienta de apoyo en un
diagnóstico de hecho, lo que es inaceptable legal y éticamente.

### II. Calidad y Validación de Datos

Toda entrada al sistema DEBE pasar por validación explícita antes de
persistirse o alimentar un modelo:

- Imágenes: extensión y MIME en `{JPG, JPEG, PNG}`, tamaño ≤ 5 MB.
- Datasets tabulares del pipeline: columnas obligatorias presentes
  (`study_id`, `patient_age`, `patient_sex`, `image_object_key`, `label`,
  `acquisition_date`, `source`) y etiquetas en el conjunto cerrado
  `{Sana, Neumonía, COVID-19}`.
- Los registros rechazados NO se descartan en silencio: se escriben en una
  zona de rechazo y generan un evento de calidad consultable.
- Los duplicados se detectan por `study_id` y se tratan como rechazo.

Rationale: la calidad del modelo y de las métricas operativas depende de la
disciplina en la frontera de entrada. Aceptar datos inválidos contamina
métricas, entrenamientos y decisiones clínicas downstream.

### III. Reproducibilidad de Modelos y Pipelines

Cada artefacto entregable DEBE poder regenerarse desde el repositorio:

- Los modelos persistidos (`models/*.pt`, `models/*.joblib`) se acompañan de
  un archivo de métricas (`*_metrics.json`) y de la matriz de confusión cuando
  aplique.
- Los entrenamientos viven bajo el perfil Docker `training` y se invocan con
  parámetros explícitos (p. ej. `TRAINING_PRETRAINED`).
- Las ejecuciones del pipeline Spark se registran en `pipeline_runs` con
  identificador, timestamps y resultado, y producen un informe JSON en
  `pipeline-reports/`.
- Cambios en el contrato de modelo se reflejan en `ml/model_contract.json`
  antes de fusionarse.

Rationale: sin reproducibilidad no hay auditoría posible ni recuperación
ante incidentes. Las métricas y contratos versionados son el único puente
fiable entre código, modelo y datos.

### IV. Pruebas Antes que Implementación (NO NEGOCIABLE)

Toda funcionalidad nueva o modificada en `backend/`, `dashboard/` y `pipeline/`
DEBE incorporar pruebas automatizadas que fallen antes de la implementación y
pasen después (ciclo Red-Green-Refactor):

- Pruebas de contrato para endpoints HTTP que cambien firma o respuesta.
- Pruebas de integración para flujos que crucen servicios (backend ↔
  PostgreSQL ↔ MinIO, dashboard ↔ backend, pipeline ↔ almacenamiento).
- Las pruebas viven en los directorios `tests/` ya existentes en cada
  componente; no se acepta lógica nueva sin cobertura asociada.

Rationale: la composición de servicios (FastAPI, Flask, Spark, PostgreSQL,
MinIO) hace que los fallos sean caros de reproducir manualmente. Las pruebas
son el contrato ejecutable que garantiza que un cambio no rompe otro
componente.

### V. Observabilidad y Auditabilidad

Todo componente DEBE emitir señales suficientes para diagnosticar incidentes
sin acceder a logs locales del desarrollador:

- Logs estructurados (clave-valor o JSON) con `study_id` o `run_id` cuando
  exista.
- Endpoints `/metrics`, `/studies/history` y `/quality/events` mantenidos
  como contrato del dashboard.
- Los eventos de calidad de datos y los `pipeline_runs` persisten en
  PostgreSQL; no se aceptan métricas exclusivamente en memoria.
- Cualquier predicción se puede reconstruir a partir del `study_id`, el
  objeto en MinIO y la fila en `radiology_studies`.

Rationale: el dashboard operativo y la memoria técnica del proyecto exigen
poder rendir cuentas de cada estudio procesado. La observabilidad no es un
extra: es parte del producto.

## Restricciones Adicionales

- **Stack obligatorio**: Python para backend (FastAPI), dashboard (Flask) y
  pipeline (PySpark); PostgreSQL como almacén relacional; MinIO como object
  storage; PyTorch/torchvision para la CNN; scikit-learn/joblib para triage.
- **Contenedores**: todo componente desplegable DEBE tener `Dockerfile` y
  estar orquestado por `docker-compose.yml`. Los flujos pesados
  (`pipeline`, `training`) se aíslan tras perfiles Docker para no encarecer
  el arranque normal.
- **Datos**: el dataset crudo vive en `data/incoming/`, el limpio en
  `data/processed/`, los modelos en `models/`. Ninguna ruta absoluta del
  desarrollador se acepta en código.
- **Idioma**: documentación funcional (`docs/SDD.md`, memorias) en español;
  identificadores de código y mensajes técnicos en inglés cuando coincidan
  con convenciones de las librerías.

## Flujo de Desarrollo y Puertas de Calidad

- Cada cambio se especifica con `/speckit-specify`, se planifica con
  `/speckit-plan` y se descompone con `/speckit-tasks` antes de implementar.
- La sección "Constitution Check" de cada `plan.md` DEBE listar
  explícitamente cómo cumple cada uno de los cinco principios o justificar
  la desviación.
- Las PRs hacia `main` requieren:
  1. Pruebas verdes en el componente modificado.
  2. Actualización de `docs/SDD.md` si cambia un criterio de aceptación.
  3. Actualización de `*_metrics.json` y `model_contract.json` si cambia el
     modelo.
- Los hooks de `.specify/extensions.yml` (commits automáticos por fase) se
  mantienen habilitados salvo decisión explícita del responsable.

## Governance

Esta constitución prevalece sobre cualquier otra práctica o convención
implícita del repositorio. Las enmiendas se realizan mediante:

1. Propuesta en una rama dedicada que modifique
   `.specify/memory/constitution.md` y, si aplica, las plantillas
   dependientes en `.specify/templates/`.
2. Aplicación de versionado semántico:
   - **MAJOR** para retiradas o redefiniciones incompatibles de principios.
   - **MINOR** para nuevos principios o expansiones materiales.
   - **PATCH** para aclaraciones, redacción o correcciones no semánticas.
3. Aprobación por revisión de PR antes de fusionar a `main`.
4. Actualización del informe de sincronización (encabezado HTML) y de
   `LAST_AMENDED_DATE`.

El cumplimiento se verifica en cada revisión de PR mediante la sección
"Constitution Check" del plan. La complejidad introducida (nuevos servicios,
dependencias, formatos) DEBE justificarse contra los principios. Para
orientación de desarrollo en tiempo de ejecución, consultar `CLAUDE.md` y el
plan vigente referenciado desde él.

**Version**: 1.0.0 | **Ratified**: 2026-05-18 | **Last Amended**: 2026-05-18
