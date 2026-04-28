# Diario de desarrollo con IA

## Herramienta utilizada

Se ha utilizado Codex de OpenAI como asistente de desarrollo para analizar el enunciado, revisar el repositorio, proponer arquitectura e implementar ampliaciones.

Justificacion:
- Permite iterar rapidamente sobre codigo Docker, backend, dashboard y documentacion.
- Facilita detectar huecos entre el enunciado y el estado real del proyecto.
- Ayuda a mantener coherencia entre servicios y entregables.

## Prompts representativos

Prompt:
> Mira el enunciado-Hospital.pdf y dime que falta del proyecto.

Resultado:
Se identificaron carencias en modelo Deep Learning, pipeline Big Data, automatizaciones, calidad de datos, monitorizacion y documentacion.

Prompt:
> Vale pues añade lo que falta.

Resultado:
Se implementaron tablas nuevas, endpoints, pipeline Spark, modulo de entrenamiento CNN, dashboard operativo y documentos tecnicos.

## Casos donde la IA acerto

- Detecto que Spark estaba desplegado pero sin jobs.
- Detecto que el clasificador activo no era un modelo clinico entrenado.
- Propuso separar entrenamiento pesado bajo perfil Docker para no bloquear el arranque normal.
- Genero endpoints de metricas y eventos reutilizables por el dashboard.

## Casos donde hubo que corregir o iterar

- El proyecto no incluye dataset real, por lo que no se puede entrenar un modelo final dentro del repositorio sin anadir datos externos.
- El clasificador basal debe documentarse como baseline y no como diagnostico clinico.
- La validacion real de Docker puede depender de Docker Desktop y permisos del host.

## Impacto en productividad

La IA redujo el tiempo de analisis inicial y permitio avanzar en varios frentes en paralelo conceptual: API, dashboard, Docker, pipeline y documentacion. El mayor ahorro estuvo en detectar requisitos omitidos y convertirlos en tareas implementables.

## Reflexion critica

La IA acelera la construccion, pero no sustituye la validacion clinica ni la seleccion responsable de datos. En un proyecto sanitario, el equipo humano debe revisar sesgos, seguridad, trazabilidad, privacidad y consecuencias de errores antes de cualquier uso real.
