# Feature Specification: Plataforma hospitalaria de radiologia, pipeline de datos y dashboard operativo

**Feature Branch**: `001-analytics-dashboard`

<!-- **Created**: 2026-05-18 -->

**Status**: Draft

**Input**: User description: "Plataforma integrada para clasificar radiografias de torax mediante un modelo de aprendizaje profundo, ejecutar un proceso por lotes que limpia y valida estudios radiologicos historicos, entrenar el modelo de clasificacion, y ofrecer un dashboard operativo unificado para personal clinico y operativo."

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Clasificacion de radiografias en linea (Priority: P1)

Un usuario clinico sube una radiografia de torax desde el dashboard. El sistema valida el archivo, genera una clasificacion entre las categorias permitidas, guarda el estudio y devuelve un informe consultable con la clase predicha, las probabilidades por clase y una nota clinica de limitacion.

**Why this priority**: Es la funcionalidad nuclear del producto: sin clasificacion no hay valor clinico ni datos que alimenten al resto de modulos.

**Independent Test**: Subir una imagen valida desde la pantalla del dashboard y comprobar que aparece la prediccion, queda registrada en el catalogo de estudios y el informe es consultable.

**Acceptance Scenarios**:

1. **Given** una imagen valida dentro del tamano permitido, **When** el usuario la envia para clasificacion, **Then** el sistema responde con clase, probabilidades, confianza e identificador de estudio, y el estudio queda registrado de forma persistente.
2. **Given** una imagen con formato no permitido o por encima del tamano maximo, **When** se envia, **Then** el sistema la rechaza con un mensaje claro y sin registrar nada.
3. **Given** una prediccion correcta, **When** el dashboard muestra el resultado, **Then** se incluye la nota clinica de limitacion exigida.

---

### User Story 2 - Limpieza por lotes de estudios radiologicos (Priority: P2)

Un operador lanza el proceso por lotes que ingiere un fichero de estudios, valida registros, descarta duplicados o incompletos, separa los datos rechazados y registra la ejecucion para consulta posterior.

**Why this priority**: Habilita la analitica agregada y el control de calidad de los datos clinicos; depende de que exista catalogo de estudios (US1) pero se ejecuta de forma independiente.

**Independent Test**: Colocar un fichero de estudios valido en la ubicacion de entrada, lanzar el proceso y verificar que se generan los datos limpios, queda registro de la ejecucion y se produce un informe de la misma.

**Acceptance Scenarios**:

1. **Given** un fichero con todas las columnas obligatorias y etiquetas validas, **When** se ejecuta el proceso, **Then** se generan datos limpios, queda registro de la ejecucion y se produce un informe consultable.
2. **Given** un fichero con duplicados o columnas faltantes, **When** se ejecuta el proceso, **Then** los registros invalidos quedan separados y se emiten eventos de calidad.
3. **Given** una ejecucion completada, **When** se abre el dashboard, **Then** el panel refleja el resultado de la ultima ejecucion.

---

### User Story 3 - Entrenamiento del modelo de clasificacion (Priority: P3)

Un investigador ejecuta el modulo de entrenamiento sobre un dataset local organizado por clase y obtiene el modelo entrenado, sus metricas y la matriz de confusion.

**Why this priority**: Es necesario para refrescar el modelo periodicamente, pero el sistema puede operar en inferencia con un artefacto preexistente.

**Independent Test**: Ejecutar el entrenamiento con un dataset bien estructurado y comprobar que se generan los tres artefactos esperados.

**Acceptance Scenarios**:

1. **Given** un dataset organizado por clase para entrenamiento y validacion, **When** se lanza el entrenamiento, **Then** se obtienen modelo, metricas y matriz de confusion.
2. **Given** que falta el dataset o tiene una clase ausente, **When** se lanza el entrenamiento, **Then** este informa claramente la estructura esperada y termina con error controlado.
3. **Given** la opcion de pesos preentrenados activada, **When** se entrena, **Then** el proceso parte de pesos preentrenados en lugar de inicializacion aleatoria.

---

### User Story 4 - Dashboard operativo unificado (Priority: P2)

Un usuario operativo accede al dashboard para subir radiografias, revisar el historico de estudios, ver el estado del proceso por lotes y consultar los eventos de calidad detectados.

**Why this priority**: Es la unica superficie de interaccion humana; sin ella las capacidades anteriores no son accesibles para usuarios no tecnicos.

**Independent Test**: Abrir el dashboard contra un entorno sin datos y comprobar que carga sin errores; tras procesar una imagen y un lote, comprobar que los nuevos elementos aparecen en sus paneles.

**Acceptance Scenarios**:

1. **Given** un entorno sin estudios previos, **When** se abre el dashboard, **Then** las vistas se renderizan con estado vacio sin errores.
2. **Given** un estudio recien clasificado, **When** se recarga el dashboard, **Then** el estudio aparece en el historico con su vista previa y resultado individual.
3. **Given** una ejecucion del proceso por lotes completada, **When** se consulta el panel, **Then** se muestra el estado de la ultima ejecucion y los eventos de calidad asociados.

---

### Edge Cases

- Imagen subida con extension valida pero contenido falsificado: debe rechazarse sin clasificar.
- Imagen valida pero el modelo no esta disponible: respuesta de error controlado, sin caer el servicio.
- Fichero de entrada vacio o solo con cabeceras: el proceso termina sin generar datos limpios pero registra una ejecucion vacia.
- Dataset de entrenamiento con clase faltante: el entrenamiento aborta indicando la clase ausente.
- Dashboard accedido cuando el resto del sistema esta caido: las vistas muestran estado degradado sin trazas crudas al usuario.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: El sistema MUST aceptar imagenes en los formatos permitidos (JPG/JPEG/PNG) de hasta 5 MB y rechazar el resto con un mensaje claro.
- **FR-002**: Cada estudio aceptado MUST persistirse en un catalogo consultable y conservar un informe individual asociado.
- **FR-003**: Cada prediccion MUST incluir clase predicha (`Sana`, `Neumonia`, `COVID-19`), probabilidades por clase, confianza y una nota clinica de limitacion.
- **FR-004**: El proceso por lotes MUST validar las columnas obligatorias (`study_id`, `patient_age`, `patient_sex`, `image_object_key`, `label`, `acquisition_date`, `source`) y aceptar solo etiquetas en `{Sana, Neumonia, COVID-19}`.
- **FR-005**: El proceso por lotes MUST separar registros duplicados o incompletos y emitir eventos de calidad cuando existan.
- **FR-006**: Cada ejecucion del proceso por lotes MUST quedar registrada y producir un informe individual consultable.
- **FR-007**: El modulo de entrenamiento MUST generar, a partir de un dataset organizado por clase, el modelo entrenado junto con sus metricas y matriz de confusion.
- **FR-008**: El entrenamiento MUST permitir activar el uso de pesos preentrenados y MUST ejecutarse de forma aislada respecto al arranque normal del sistema.
- **FR-009**: El dashboard MUST permitir subir radiografias y mostrar resultado individual, historico de estudios, estado del proceso por lotes y eventos de calidad.
- **FR-010**: El dashboard MUST renderizar correctamente cuando no haya datos disponibles, mostrando estados vacios sin errores.

### Key Entities

- **RadiologyStudy**: estudio radiologico procesado. Atributos clave: identificador, datos basicos del paciente (edad/sexo), referencia a la imagen, clase predicha, probabilidades, confianza, fecha de adquisicion.
- **PipelineRun**: ejecucion del proceso por lotes. Atributos: identificador, marca temporal, contadores de filas aceptadas/rechazadas, referencia al informe.
- **QualityEvent**: incidencia de calidad detectada por el proceso por lotes o por baja confianza del modelo.
- **RadiologyReport**: informe individual con el detalle de la prediccion y enlace a la imagen original.
- **RadiologyModelArtifact**: modelo entrenado y sus metricas asociadas.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: El 100% de las imagenes invalidas (formato o tamano) se rechazan sin crear registros.
- **SC-002**: Cada imagen valida produce un registro persistente y un informe consultable en la misma operacion.
- **SC-003**: El proceso por lotes procesa un fichero de ejemplo de extremo a extremo sin intervencion manual.
- **SC-004**: Tras una ejecucion del proceso por lotes, el dashboard refleja la nueva ejecucion sin requerir reinicio.
- **SC-005**: El dashboard se carga sin errores incluso cuando no hay datos disponibles.
- **SC-006**: Cuando el dataset esta presente, el entrenamiento genera siempre los tres artefactos esperados (modelo, metricas, matriz de confusion).
- **SC-007**: Un usuario clinico puede completar el flujo de subida y obtencion de resultado de una radiografia en menos de 1 minuto en condiciones normales.

## Assumptions

- Los usuarios clinicos acceden al dashboard desde la red interna del hospital con credenciales gestionadas por el operador.
- La infraestructura subyacente es un unico entorno on-premise; no se considera alta disponibilidad ni multi-region en esta version.
- El almacenamiento de imagenes e informes se centraliza en un unico repositorio de objetos.
- El dataset de entrenamiento se gestiona fuera del repositorio de codigo y se aporta como volumen.
- La nota clinica de limitacion es texto fijo proporcionado por el equipo medico; no requiere personalizacion por estudio.
- El proceso por lotes se ejecuta bajo demanda, no como servicio permanente.
