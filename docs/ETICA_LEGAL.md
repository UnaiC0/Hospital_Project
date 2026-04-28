# Consideraciones eticas y legales

## Sesgos

Los modelos de radiografia pueden aprender sesgos si el dataset no representa edades, sexos, procedencias, equipos radiologicos o condiciones clinicas diversas. Un modelo entrenado con datos de un unico hospital puede fallar al aplicarse en otro entorno.

Medidas propuestas:
- Documentar origen y composicion del dataset.
- Separar entrenamiento, validacion y test por paciente.
- Revisar metricas por subgrupos.
- Analizar matriz de confusion y falsos negativos.

## Riesgos de decision automatizada

El sistema no debe decidir diagnosticos ni altas de pacientes de forma autonoma. Debe actuar como herramienta de apoyo y priorizacion. Los resultados con baja confianza o mala calidad deben enviarse a revision humana.

Riesgos principales:
- Falso negativo de COVID-19: riesgo de contagio y retraso de aislamiento.
- Falso negativo de neumonia: retraso de tratamiento.
- Falso positivo: ansiedad, pruebas innecesarias y sobrecarga operativa.

## Privacidad

Las imagenes medicas y datos clinicos son datos sensibles. El prototipo no incluye autenticacion, cifrado de objetos ni gestion de consentimientos, por lo que solo debe usarse con datos anonimizados o simulados.

Medidas necesarias en un entorno real:
- Control de acceso por roles.
- Cifrado en reposo y en transito.
- Auditoria de accesos.
- Minimizacion de datos.
- Politica de retencion y borrado.

## Limitaciones del sistema

El clasificador activo del backend es un baseline tecnico para demostrar el flujo completo. El modulo CNN queda preparado para entrenamiento, pero requiere dataset real, evaluacion formal y validacion clinica antes de presentarse como modelo util en produccion.

## Responsabilidad

La interpretacion final corresponde al personal sanitario. El sistema debe mostrar explicaciones, incertidumbre y advertencias para evitar que los usuarios confundan una prediccion con un diagnostico definitivo.
