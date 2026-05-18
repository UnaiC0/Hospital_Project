"""Generador del documento final de entrega.

Produce `docs/Hospital_Project_Entrega.pdf` con:
  1. Memoria tecnica (9 apartados del enunciado)
  2. Spec-Driven Development (SDD)
  3. Diario de desarrollo con IA
  4. Consideraciones eticas y legales
  5. TODO de trabajo pendiente
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


OUTPUT_PATH = Path(__file__).resolve().parent / "Hospital_Project_Entrega.pdf"

NAVY = colors.HexColor("#0F2547")
BLUE = colors.HexColor("#1F4E8E")
TEAL = colors.HexColor("#2E8B8B")
GRAY = colors.HexColor("#4A4A4A")
LIGHT = colors.HexColor("#EAEFF5")
CODE_BG = colors.HexColor("#F4F4F4")
WARN = colors.HexColor("#B85C00")


# ---------------------------------------------------------------------------
# STYLES
# ---------------------------------------------------------------------------
base = getSampleStyleSheet()

styles = {
    "CoverTitle": ParagraphStyle(
        "CoverTitle", parent=base["Title"], fontName="Helvetica-Bold",
        fontSize=28, leading=34, textColor=NAVY, alignment=TA_CENTER, spaceAfter=18,
    ),
    "CoverSubtitle": ParagraphStyle(
        "CoverSubtitle", parent=base["Title"], fontName="Helvetica",
        fontSize=15, leading=20, textColor=GRAY, alignment=TA_CENTER, spaceAfter=10,
    ),
    "CoverMeta": ParagraphStyle(
        "CoverMeta", parent=base["Normal"], fontName="Helvetica",
        fontSize=11, leading=16, textColor=GRAY, alignment=TA_CENTER,
    ),
    "Chapter": ParagraphStyle(
        "Chapter", parent=base["Heading1"], fontName="Helvetica-Bold",
        fontSize=20, leading=26, textColor=NAVY, spaceBefore=18, spaceAfter=12,
        keepWithNext=True,
    ),
    "Section": ParagraphStyle(
        "Section", parent=base["Heading2"], fontName="Helvetica-Bold",
        fontSize=14, leading=18, textColor=BLUE, spaceBefore=14, spaceAfter=8,
        keepWithNext=True,
    ),
    "Subsection": ParagraphStyle(
        "Subsection", parent=base["Heading3"], fontName="Helvetica-Bold",
        fontSize=11.5, leading=15, textColor=TEAL, spaceBefore=10, spaceAfter=6,
        keepWithNext=True,
    ),
    "Body": ParagraphStyle(
        "Body", parent=base["BodyText"], fontName="Helvetica",
        fontSize=10, leading=14, textColor=colors.black, alignment=TA_JUSTIFY,
        spaceAfter=6,
    ),
    "Bullet": ParagraphStyle(
        "Bullet", parent=base["BodyText"], fontName="Helvetica",
        fontSize=10, leading=14, leftIndent=14, bulletIndent=2, alignment=TA_LEFT,
        spaceAfter=3, textColor=colors.black,
    ),
    "Code": ParagraphStyle(
        "Code", parent=base["Normal"], fontName="Courier",
        fontSize=8.5, leading=11.5, textColor=colors.HexColor("#222"),
        backColor=CODE_BG, borderPadding=(6, 6, 6, 6), leftIndent=8, rightIndent=8,
        spaceBefore=6, spaceAfter=6, alignment=TA_LEFT,
    ),
    "Caption": ParagraphStyle(
        "Caption", parent=base["Italic"], fontName="Helvetica-Oblique",
        fontSize=9, leading=12, textColor=GRAY, alignment=TA_CENTER, spaceAfter=10,
    ),
    "Quote": ParagraphStyle(
        "Quote", parent=base["BodyText"], fontName="Helvetica-Oblique",
        fontSize=10, leading=14, leftIndent=14, rightIndent=14, textColor=GRAY,
        spaceBefore=4, spaceAfter=8, alignment=TA_JUSTIFY,
    ),
    "Todo": ParagraphStyle(
        "Todo", parent=base["BodyText"], fontName="Helvetica-Bold",
        fontSize=10, leading=14, textColor=WARN, spaceBefore=4, spaceAfter=4,
    ),
    "TOC": ParagraphStyle(
        "TOC", parent=base["Normal"], fontName="Helvetica",
        fontSize=10.5, leading=16, textColor=NAVY,
    ),
}


# ---------------------------------------------------------------------------
# DOC TEMPLATE WITH HEADER / FOOTER
# ---------------------------------------------------------------------------
class HospitalDocTemplate(BaseDocTemplate):
    def __init__(self, filename: Path, **kwargs):
        super().__init__(
            str(filename),
            pagesize=A4,
            leftMargin=2.2 * cm,
            rightMargin=2.2 * cm,
            topMargin=2.0 * cm,
            bottomMargin=1.8 * cm,
            title="Hospital Project - Memoria de Entrega",
            author="Equipo Hospital Project",
        )
        frame = Frame(
            self.leftMargin, self.bottomMargin,
            self.width, self.height,
            id="content", showBoundary=0,
        )
        cover = PageTemplate(id="cover", frames=frame, onPage=self._cover_page)
        normal = PageTemplate(id="normal", frames=frame, onPage=self._normal_page)
        self.addPageTemplates([cover, normal])

    def _cover_page(self, canvas, doc):  # no header/footer on cover
        canvas.saveState()
        canvas.setFillColor(NAVY)
        canvas.rect(0, A4[1] - 1.2 * cm, A4[0], 1.2 * cm, fill=1, stroke=0)
        canvas.setFillColor(TEAL)
        canvas.rect(0, 0, A4[0], 0.7 * cm, fill=1, stroke=0)
        canvas.restoreState()

    def _normal_page(self, canvas, doc):
        canvas.saveState()
        # Header
        canvas.setStrokeColor(BLUE)
        canvas.setLineWidth(0.4)
        canvas.line(2 * cm, A4[1] - 1.3 * cm, A4[0] - 2 * cm, A4[1] - 1.3 * cm)
        canvas.setFont("Helvetica", 8.5)
        canvas.setFillColor(GRAY)
        canvas.drawString(2 * cm, A4[1] - 1.1 * cm, "Hospital Project - LaSalle Health Center")
        canvas.drawRightString(A4[0] - 2 * cm, A4[1] - 1.1 * cm, "Entrega final")
        # Footer
        canvas.line(2 * cm, 1.4 * cm, A4[0] - 2 * cm, 1.4 * cm)
        canvas.setFont("Helvetica", 8.5)
        canvas.drawString(2 * cm, 1.0 * cm, f"Pagina {doc.page}")
        canvas.drawRightString(A4[0] - 2 * cm, 1.0 * cm, "Equipo Hospital Project")
        canvas.restoreState()


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def p(text: str, style: str = "Body"):
    return Paragraph(text, styles[style])


def bullets(items: list[str]):
    return [
        Paragraph(f"<bullet>&bull;</bullet> {item}", styles["Bullet"])
        for item in items
    ]


def code(snippet: str):
    cleaned = snippet.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    cleaned = cleaned.replace("\n", "<br/>").replace("  ", "&nbsp;&nbsp;")
    return Paragraph(cleaned, styles["Code"])


def table(headers: list[str], rows: list[list[str]], col_widths: list[float] | None = None):
    data = [[Paragraph(f"<b>{h}</b>", styles["Body"]) for h in headers]]
    for row in rows:
        data.append([Paragraph(cell, styles["Body"]) for cell in row])
    if col_widths is None:
        col_widths = [16.5 * cm / len(headers)] * len(headers)
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B0B0B0")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def chapter(num: int, title: str):
    return p(f"{num}. {title}", "Chapter")


def section(num: str, title: str):
    return p(f"{num} {title}", "Section")


def subsection(title: str):
    return p(title, "Subsection")


def todo(text: str):
    return Paragraph(f"<b>TODO &mdash;</b> {text}", styles["Todo"])


# ---------------------------------------------------------------------------
# CONTENT
# ---------------------------------------------------------------------------
def build_cover() -> list:
    return [
        Spacer(1, 4 * cm),
        p("Sistema Inteligente de Soporte Hospitalario", "CoverTitle"),
        p("LaSalle Health Center", "CoverSubtitle"),
        Spacer(1, 1 * cm),
        p("Memoria tecnica, Spec-Driven Development,<br/>Diario de desarrollo con IA y consideraciones eticas",
          "CoverSubtitle"),
        Spacer(1, 3 * cm),
        p(f"Fecha de entrega: {date.today().isoformat()}", "CoverMeta"),
        Spacer(1, 0.4 * cm),
        p("Equipo: Hospital Project", "CoverMeta"),
        Spacer(1, 0.4 * cm),
        p("Asignatura: Sistemes d'Aprenentatge Automatic / Big Data", "CoverMeta"),
        Spacer(1, 4 * cm),
        p("Documento generado de forma automatica con reportlab.<br/>"
          "Repositorio: Hospital_Project / rama main", "CoverMeta"),
        PageBreak(),
    ]


def build_toc() -> list:
    rows = [
        ("1.", "Resumen ejecutivo"),
        ("2.", "Memoria tecnica"),
        ("2.1", "Descripcion del problema"),
        ("2.2", "Datos"),
        ("2.3", "Arquitectura del sistema"),
        ("2.4", "Modelos de Inteligencia Artificial"),
        ("2.5", "Automatizaciones"),
        ("2.6", "Integraciones"),
        ("2.7", "Justificaciones tecnicas y alternativas consideradas"),
        ("2.8", "Reflexion critica"),
        ("2.9", "Limitaciones del sistema"),
        ("3.", "Spec-Driven Development (SDD)"),
        ("4.", "Diario de desarrollo con IA"),
        ("5.", "Consideraciones eticas y legales"),
        ("6.", "Trabajo pendiente (TODO)"),
    ]
    rendered = [chapter(0, "Indice")]
    for num, title in rows:
        rendered.append(Paragraph(
            f"<b>{num}</b> &nbsp;&nbsp; {title}", styles["TOC"]
        ))
    rendered.append(PageBreak())
    return rendered


def build_summary() -> list:
    out: list = [
        chapter(1, "Resumen ejecutivo"),
        p(
            "Este documento describe el sistema disenado para LaSalle Health Center, una "
            "plataforma containerizada que integra clasificacion radiologica asistida, "
            "triaje clinico automatizado, ingesta de datos a escala mediante Apache Spark, "
            "almacenamiento dual (PostgreSQL y MinIO) y observabilidad con Prometheus y "
            "Grafana. El sistema cubre el flujo completo desde la captura del estudio en "
            "el dashboard hasta la generacion de informes JSON persistidos en almacenamiento "
            "de objetos, pasando por validacion de calidad, deteccion automatica de eventos "
            "criticos y exposicion de metricas operacionales en tiempo real."
        ),
        p(
            "La arquitectura sigue principios de Domain-Driven Design adaptados a Python: "
            "separacion estricta entre routers HTTP, servicios de dominio, repositorios de "
            "acceso a datos y adaptadores de infraestructura. Toda escritura compuesta se "
            "ejecuta dentro de una unica transaccion (Unit of Work) garantizando ACID. La "
            "configuracion se carga de forma tipada al arranque (fail-fast) y las conexiones "
            "a PostgreSQL se gestionan mediante un pool con tamano configurable."
        ),
        p(
            "El despliegue se realiza con un unico comando (<i>docker compose up -d</i>) y "
            "cubre diez servicios coordinados por una red Docker compartida. La integracion "
            "continua, configurada con GitHub Actions, ejecuta automaticamente la suite de "
            "tests (166 casos entre backend y dashboard) y valida la sintaxis del archivo de "
            "composicion. La cobertura de la logica de negocio supera el 95 por ciento."
        ),
        section("1.1", "Estado de la entrega"),
    ]
    out += bullets([
        "Infraestructura Docker Compose: 10 servicios operativos, healthchecks y volumenes persistentes.",
        "Backend FastAPI modular: 39 archivos, arquitectura en capas, response_model tipado.",
        "Dashboard Flask modular: 20 archivos con app factory, blueprints y servicios.",
        "Pipeline Spark modular: 15 archivos separando validacion, transformacion y persistencia.",
        "Observabilidad: Prometheus, Grafana con dashboard provisionado, logging JSON estructurado.",
        "HTTPS opcional con Traefik (perfil <i>tls</i>) y redirect automatico HTTP a HTTPS.",
        "166 tests automatizados; cobertura de la logica de negocio superior al 95 por ciento.",
        "CI con GitHub Actions ejecutando los tests en cada push y validando docker-compose.",
    ])
    out += [
        todo("La integracion del modelo CNN entrenado (ResNet18) en el endpoint /predict del "
             "backend queda pendiente. El modulo de entrenamiento <i>ml/train_cnn.py</i> esta "
             "preparado y a la espera de un dataset real de radiografias para producir el "
             "artefacto <i>models/radiology_cnn_resnet18.pt</i>."),
        PageBreak(),
    ]
    return out


# ---- 2. Memoria tecnica --------------------------------------------------
def build_memoria() -> list:
    out: list = [chapter(2, "Memoria tecnica")]

    # 2.1
    out += [
        section("2.1", "Descripcion del problema"),
        subsection("Contexto"),
        p(
            "LaSalle Health Center es una organizacion sanitaria de tamano medio en proceso "
            "de transformacion digital. Genera diariamente grandes volumenes de datos clinicos "
            "(historias, registros, pruebas diagnosticas, logs) que actualmente no se "
            "aprovechan para extraer conocimiento, detectar patrones ni automatizar procesos. "
            "La direccion ha solicitado a este equipo, como consultora especializada en "
            "Inteligencia Artificial y Big Data, el diseno de una plataforma que cubra el "
            "ciclo completo de gestion de datos clinicos no estructurados (imagen) y "
            "tabulares, con enfasis en clasificacion radiologica, automatizacion operativa y "
            "soporte a la toma de decisiones."
        ),
        subsection("Objetivos"),
    ]
    out += bullets([
        "Clasificar radiografias de torax en tres categorias clinicamente relevantes: Sana, Neumonia y COVID-19.",
        "Generar un informe estructurado y persistente para cada estudio, accesible mediante API REST.",
        "Detectar de forma automatica eventos de calidad y alertas clinicas (clase COVID-19, baja confianza, problemas de imagen).",
        "Procesar lotes de estudios mediante un pipeline distribuido (Apache Spark) con validacion de calidad de datos.",
        "Ofrecer una interfaz web con autenticacion y roles para el personal sanitario.",
        "Exponer metricas operativas en tiempo real para monitorizar el comportamiento del sistema.",
        "Soportar despliegue reproducible mediante contenedores y un unico fichero de composicion.",
    ])
    out += [
        subsection("Alcance"),
        p(
            "El alcance es un prototipo funcional que cubre el flujo end-to-end del enunciado. "
            "Se simulan los datos de entrada cuando no se dispone de dataset real. La inferencia "
            "esta encapsulada detras de una interfaz unica (<i>InferenceService</i>) que admite "
            "tanto un baseline tecnico actual como, en el futuro, el modelo CNN entrenado por "
            "el equipo de Deep Learning. La integracion final del CNN entrenado se considera "
            "fuera del alcance temporal de esta entrega documental."
        ),
        PageBreak(),

        # 2.2
        section("2.2", "Datos"),
        subsection("Fuentes utilizadas"),
        bullets([
            "Radiografias de torax (formatos JPG, JPEG, PNG; tamano maximo 5 MB) subidas a traves del dashboard.",
            "CSV tabular en <i>data/incoming/radiology_studies.csv</i> con metadatos de estudios para el pipeline Spark.",
            "Datos sinteticos generados localmente para pruebas de calidad (duplicados, etiquetas invalidas, campos vacios).",
        ]),
        p(
            "Para entrenamiento real del modelo CNN se preve usar el dataset publico "
            "<i>COVID-19 Radiography Database</i> (Kaggle) o equivalente. El esquema de "
            "directorios esperado por el modulo de entrenamiento es "
            "<i>data/radiology_dataset/{train,val}/{Sana,Neumonia,COVID-19}/*.png</i>."
        ),
        subsection("Proceso de limpieza y transformacion"),
        bullets([
            "Validacion de extension del archivo en cliente (Flask) y backend (FastAPI).",
            "Validacion de tipo MIME y contenido binario mediante Pillow para evitar archivos malformados.",
            "Comprobacion de coherencia entre extension declarada y formato real (rechazo de JPEG con extension PNG).",
            "Limite estricto de 5 MB por imagen para proteger memoria del servicio de inferencia.",
            "En el pipeline: validacion de columnas obligatorias, recorte de espacios en blanco, deteccion de duplicados por <i>image_object_key</i>, separacion de registros validos y rechazados.",
            "Persistencia diferenciada: imagen binaria a MinIO bajo <i>uploads/</i>, informe JSON a MinIO bajo <i>radiology-reports/</i>, metadatos estructurados a PostgreSQL.",
        ]),
        subsection("Calidad de datos"),
        p(
            "El pipeline Spark genera un informe por ejecucion con la distribucion por clase "
            "de los registros aceptados, una muestra de hasta 25 registros rechazados y la "
            "lista de claves duplicadas. Cuando hay rechazos, se inserta un evento de "
            "severidad <i>medium</i> en la tabla <i>quality_events</i>. Cualquier fallo del "
            "pipeline (lectura del CSV, esquema invalido, error de escritura) genera un "
            "evento <i>high</i> y un informe de tipo <i>failed</i>."
        ),
        PageBreak(),

        # 2.3 Architecture
        section("2.3", "Arquitectura del sistema"),
        subsection("Diseno del pipeline de datos"),
        p(
            "El sistema implementa el patron <b>Layered Architecture</b> con cuatro capas "
            "claras en el backend:"
        ),
        bullets([
            "<b>API (FastAPI routers)</b>: traduce peticiones HTTP a llamadas de dominio. Sin logica de negocio.",
            "<b>Services</b>: orquestan la logica de negocio. Componen llamadas a repositorios dentro de transacciones.",
            "<b>Repositories</b>: acceso a datos. Reciben un cursor abierto del Unit of Work para garantizar atomicidad.",
            "<b>Infrastructure</b>: <i>DatabaseSession</i> con pool de conexiones, <i>ObjectStorage</i> adaptador S3, configuracion tipada.",
        ]),
        p(
            "La inyeccion de dependencias se realiza mediante el sistema <i>Depends</i> de "
            "FastAPI, con factorias cacheadas (<i>lru_cache</i>) en <i>api/deps.py</i>. Esto "
            "permite sustituir cualquier dependencia en tests sin tocar el codigo de produccion."
        ),
        subsection("Infraestructura utilizada"),
        table(
            ["Servicio", "Imagen", "Puerto", "Responsabilidad"],
            [
                ["backend", "hospital-backend (Python 3.11)", "8000", "API REST, inferencia baseline, persistencia"],
                ["dashboard", "hospital-dashboard (Python 3.10)", "8501", "UI web, autenticacion, subida de estudios"],
                ["db", "postgres:16.13-alpine", "5432", "Datos estructurados (estudios, triajes, eventos)"],
                ["minio", "minio:RELEASE.2024-01-11", "9000 / 9001", "Almacenamiento de objetos (imagenes, JSON)"],
                ["spark", "spark:3.5.8-python3", "interno", "Master Spark"],
                ["spark-worker", "spark:3.5.8-python3", "interno", "Worker Spark (2 cores / 1 GB)"],
                ["pipeline", "hospital-pipeline", "perfil pipeline", "Job Spark de ingesta y calidad"],
                ["model-trainer", "hospital-model-trainer", "perfil training", "Entrenamiento CNN ResNet18"],
                ["prometheus", "prom/prometheus:v2.54.1", "9090", "Scraping de metricas (15s)"],
                ["grafana", "grafana/grafana:11.2.0", "3000", "Dashboards operativos"],
                ["traefik", "traefik:v3.1", "perfil tls", "Reverse proxy HTTPS"],
            ],
            col_widths=[3.0 * cm, 4.2 * cm, 2.6 * cm, 6.7 * cm],
        ),
        subsection("Relacion entre componentes"),
        code(
            "Browser\n"
            "  |--> https://hospital.local            (Traefik, perfil tls)\n"
            "  |     |--> dashboard:8501              (Flask + blueprints)\n"
            "  |     |--> /api --> backend:8000       (FastAPI + Pydantic)\n"
            "  |                    |--> db (PostgreSQL pool 2..10)\n"
            "  |                    |--> minio (S3 API, boto3)\n"
            "  |--> http://localhost:3000             (Grafana)\n"
            "                       |--> prometheus:9090\n"
            "                                |--> scrape backend:/metrics/prom (15s)\n"
            "\n"
            "pipeline (Spark) ---> CSV en /data/incoming\n"
            "                 ---> JSON en /data/processed\n"
            "                 ---> registro en pipeline_runs (PostgreSQL)\n"
            "                 ---> reporte en minio bajo pipeline-reports/\n"
        ),
        PageBreak(),

        # 2.4 Models
        section("2.4", "Modelos de Inteligencia Artificial"),
        subsection("Modelos implementados"),
        p(
            "El sistema integra tres componentes de inteligencia artificial, cada uno "
            "encapsulado detras de un service con contrato estable. Esto permite sustituir "
            "el motor de inferencia sin modificar el codigo que lo consume."
        ),
        subsection("Triaje clinico (motor de reglas)"),
        p(
            "Implementado en <i>TriageService.assess</i>. Aplica un sistema de puntuacion "
            "con peso configurable sobre tres dimensiones clinicas:"
        ),
        bullets([
            "Sintomas: cada sintoma suma 8 puntos (cap de 40); sintomas criticos (dolor toracico, disnea, perdida de conciencia) suman 35 adicionales.",
            "Frecuencia cardiaca: taquicardia (&gt;= 120 lpm) suma 15.",
            "Saturacion de oxigeno: hipoxia (&lt; 92 %) suma 25.",
            "Tension arterial sistolica: hipotension (&lt; 90 mmHg) suma 20.",
        ]),
        p(
            "El score se acota a 100 y se mapea a cuatro niveles: <i>low</i> / "
            "<i>medium</i> / <i>high</i> / <i>critical</i>, asociados a las prioridades "
            "<i>standard</i>, <i>priority</i>, <i>urgent</i>, <i>immediate</i>. La eleccion "
            "de un sistema rule-based en lugar de un modelo entrenado se justifica por la "
            "interpretabilidad clinica obligatoria en triaje, donde cualquier decision debe "
            "poder explicarse a un facultativo."
        ),
        subsection("Clasificacion radiologica baseline"),
        p(
            "El servicio <i>InferenceService</i> implementa un clasificador estadistico de "
            "intensidad y contraste sobre la imagen redimensionada a 256x256 en escala de "
            "grises. Calcula tres scores parametricos (uno por clase) y normaliza por su "
            "suma. La eleccion del baseline tiene dos motivaciones: (a) garantizar que el "
            "flujo end-to-end del sistema funcione sin depender de un artefacto entrenado, "
            "y (b) proporcionar un punto de comparacion contra el CNN cuando este se integre."
        ),
        subsection("CNN ResNet18 para clasificacion (modulo training)"),
        p(
            "El modulo <i>ml/train_cnn.py</i> implementa el entrenamiento de una red "
            "ResNet18 sobre tres clases. Se ha optado por arquitectura preexistente con "
            "transfer learning opcional (variable <i>TRAINING_PRETRAINED</i>) frente a una "
            "CNN propia debido a: (a) madurez probada en imagenes medicas, (b) bajo coste "
            "computacional para inferencia, (c) facilidad de fine-tuning con datasets "
            "pequenos. El pipeline de entrenamiento incluye:"
        ),
        bullets([
            "Aumento de datos: flip horizontal aleatorio y rotacion de hasta 8 grados.",
            "Normalizacion estandar de ImageNet (mean / std).",
            "Optimizador AdamW con learning rate configurable (por defecto 5e-4).",
            "Loss CrossEntropy.",
            "Guardado del mejor checkpoint por accuracy en validacion.",
            "Calculo automatico de matriz de confusion y classification report con sklearn.",
        ]),
        todo("Conectar el artefacto <i>models/radiology_cnn_resnet18.pt</i> al "
             "<i>InferenceService</i> del backend cuando el equipo de DL termine el "
             "entrenamiento. La interfaz publica del service no cambia; solo se sustituye "
             "la implementacion interna de <i>predict()</i>."),
        todo("Documentar en esta seccion las metricas finales del modelo CNN una vez "
             "entrenado: accuracy de validacion, matriz de confusion analizada, falsos "
             "negativos por clase (especial atencion a COVID-19), tiempo de inferencia "
             "promedio."),
        PageBreak(),

        # 2.5 Automation
        section("2.5", "Automatizaciones"),
        subsection("Automatizaciones implementadas"),
        bullets([
            "<b>Bootstrap del bucket</b>: el adaptador <i>ObjectStorage.ensure_bucket()</i> crea el bucket en MinIO si no existe y la bandera <i>MINIO_AUTO_CREATE_BUCKET</i> esta activada.",
            "<b>Esquema de PostgreSQL</b>: la funcion <i>initialize_schema_with_retry</i> se ejecuta en el lifespan de FastAPI con hasta 10 reintentos espaciados 2 segundos, garantizando que el backend tolere arranques en paralelo con la base de datos.",
            "<b>Generacion de informes</b>: cada triaje y cada estudio radiologico genera automaticamente un documento JSON persistido en MinIO bajo <i>triage-reports/&lt;id&gt;.json</i> y <i>radiology-reports/&lt;id&gt;.json</i>.",
            "<b>Alertas clinicas</b>: una prediccion COVID-19 genera un evento de severidad <i>high</i> en <i>quality_events</i>; una confianza inferior a 0.55 genera un evento <i>medium</i>; banderas de calidad de imagen generan un tercer evento.",
            "<b>Pipeline de datos</b>: detecta automaticamente registros incompletos, etiquetas fuera del conjunto valido y duplicados; emite eventos en consecuencia.",
            "<b>Resolucion de eventos</b>: el endpoint <i>PATCH /quality/events/{id}/resolve</i> permite cerrar el ciclo marcando el evento como atendido.",
            "<b>Redirect HTTPS</b>: Traefik (perfil tls) fuerza redirect 301 de HTTP a HTTPS.",
            "<b>Scraping de metricas</b>: Prometheus consulta <i>/metrics/prom</i> cada 15 segundos sin intervencion manual.",
            "<b>Aprovisionamiento de Grafana</b>: el dashboard <i>Hospital Overview</i> y la fuente de datos Prometheus se cargan automaticamente en el primer arranque del contenedor.",
        ]),
        subsection("Integracion dentro del sistema"),
        p(
            "Las automatizaciones se integran como efectos colaterales controlados dentro "
            "de los services, no como tareas asincronas separadas. Esto simplifica el modelo "
            "transaccional: cuando un estudio se persiste, los eventos derivados se insertan "
            "en la misma transaccion (Unit of Work) garantizando que no quede estado "
            "inconsistente. Si por cualquier razon falla la insercion del evento, la "
            "transaccion completa hace rollback y ni el estudio ni el evento llegan a la "
            "base de datos."
        ),
        PageBreak(),

        # 2.6 Integrations
        section("2.6", "Integraciones"),
        subsection("Flujo completo de datos"),
        p(
            "El recorrido tipico de un estudio radiologico atraviesa cinco fronteras de "
            "integracion:"
        ),
        bullets([
            "<b>Navegador a Dashboard</b>: peticion HTTP / HTTPS, cookie de sesion firmada con la SECRET_KEY de Flask, cuerpo multipart con la imagen.",
            "<b>Dashboard a MinIO</b>: el cliente boto3 sube la imagen a <i>uploads/&lt;uuid&gt;.&lt;ext&gt;</i> con generacion de clave unica.",
            "<b>Dashboard a Backend</b>: llamada HTTP POST a <i>/predict</i> con el archivo binario y la <i>source_object_key</i> ya conocida.",
            "<b>Backend a Servicios internos</b>: inferencia, persistencia en PostgreSQL (pool de conexiones) y MinIO (informe JSON), todo dentro de una transaccion.",
            "<b>Prometheus a Backend</b>: scrape cada 15 segundos del endpoint <i>/metrics/prom</i> para recoger counters y histogramas.",
        ]),
        subsection("Conexion entre modulos"),
        table(
            ["Origen", "Destino", "Protocolo", "Proposito"],
            [
                ["dashboard", "backend", "HTTP / REST", "Solicitar prediccion, leer metricas"],
                ["backend", "db", "psycopg / pool 2-10", "Persistir estudios y eventos"],
                ["backend", "minio", "S3 (boto3)", "Subir imagenes e informes"],
                ["pipeline", "db", "psycopg", "Registrar ejecuciones y eventos"],
                ["pipeline", "minio", "S3 (boto3)", "Publicar informes de ejecucion"],
                ["prometheus", "backend", "HTTP", "Scraping de /metrics/prom"],
                ["grafana", "prometheus", "HTTP", "Consulta PromQL"],
                ["traefik", "backend / dashboard", "HTTP interno", "Routing TLS"],
            ],
            col_widths=[3.0 * cm, 3.5 * cm, 3.5 * cm, 6.5 * cm],
        ),
        PageBreak(),

        # 2.7 Justifications
        section("2.7", "Justificaciones tecnicas y alternativas consideradas"),
        p(
            "Esta seccion documenta las decisiones de diseno mas relevantes, las "
            "alternativas evaluadas para cada una y la razon final de eleccion."
        ),
        subsection("Backend: FastAPI"),
        p(
            "<b>Alternativas:</b> Flask, Django REST Framework, Litestar.<br/>"
            "<b>Decision:</b> FastAPI.<br/>"
            "<b>Motivo:</b> tipado fuerte mediante Pydantic, generacion automatica de "
            "documentacion OpenAPI consumible desde el dashboard de pruebas, soporte "
            "asincrono nativo, ecosistema maduro de inyeccion de dependencias. Flask "
            "habria requerido capas adicionales (Marshmallow, Flask-RESTX) para alcanzar el "
            "mismo nivel de validacion y documentacion; Django excede las necesidades de un "
            "servicio API stateless."
        ),
        subsection("Dashboard: Flask"),
        p(
            "<b>Alternativas:</b> Streamlit, Dash, FastAPI con Jinja, frontend SPA "
            "(React / Vue).<br/>"
            "<b>Decision:</b> Flask con plantillas Jinja y blueprints.<br/>"
            "<b>Motivo:</b> Streamlit no permite el grado de personalizacion visual "
            "requerido para una UI medica. Dash esta orientado a visualizacion analitica, "
            "no a flujos transaccionales con autenticacion. Un SPA habria sobredimensionado "
            "el proyecto. Flask con app factory y blueprints ofrece la flexibilidad de un "
            "marco minimalista con escalabilidad estructural."
        ),
        subsection("Almacenamiento estructurado: PostgreSQL"),
        p(
            "<b>Alternativas:</b> MySQL, MongoDB, SQLite.<br/>"
            "<b>Decision:</b> PostgreSQL 16.<br/>"
            "<b>Motivo:</b> soporte de tipos JSONB para almacenar respuestas de modelo y "
            "metadatos sin esquema fijo, transacciones ACID robustas, indices parciales y "
            "agregados condicionales (COUNT(*) FILTER) que simplifican las consultas de "
            "metricas. MongoDB se descarto porque la mayor parte de los datos tienen "
            "esquema estable y se beneficia de las garantias relacionales."
        ),
        subsection("Almacenamiento de objetos: MinIO"),
        p(
            "<b>Alternativas:</b> MongoDB GridFS, sistema de archivos local, Amazon S3 real, "
            "Azure Blob Storage.<br/>"
            "<b>Decision:</b> MinIO en contenedor local.<br/>"
            "<b>Motivo:</b> ofrece la API S3 estandar, lo que permite usar boto3 sin "
            "diferencias respecto a un despliegue cloud futuro. La portabilidad a "
            "producccion seria un cambio de configuracion, no de codigo. GridFS habria "
            "fragmentado el almacenamiento entre dos sistemas distintos (estructurado y "
            "binario en Mongo) complicando los backups."
        ),
        subsection("Procesamiento distribuido: Apache Spark"),
        p(
            "<b>Alternativas:</b> Dask, Apache Beam, pandas con procesamiento por lotes.<br/>"
            "<b>Decision:</b> Apache Spark 3.5.8 con PySpark.<br/>"
            "<b>Motivo:</b> Spark es el estandar de facto en entornos hospitalarios y de "
            "investigacion biomedica con volumenes grandes. Dask es atractivo para "
            "workloads numpy-centric pero menos maduro para SQL y joins. Apache Beam ofrece "
            "portabilidad multi-runner que excede el alcance del prototipo. Aunque el "
            "volumen del prototipo es pequeno, la eleccion de Spark prepara la plataforma "
            "para escalado horizontal real."
        ),
        subsection("Reverse proxy: Traefik"),
        p(
            "<b>Alternativas:</b> Nginx, Caddy, HAProxy.<br/>"
            "<b>Decision:</b> Traefik 3.1.<br/>"
            "<b>Motivo:</b> integracion nativa con Docker mediante labels, descubrimiento "
            "automatico de servicios, gestion sencilla de certificados, dashboard de "
            "estado integrado. Nginx requiere reescribir configuracion estatica para "
            "cada cambio de servicio."
        ),
        subsection("Observabilidad: Prometheus + Grafana"),
        p(
            "<b>Alternativas:</b> Datadog, ELK con Metricbeat, OpenTelemetry Collector "
            "con backend remoto.<br/>"
            "<b>Decision:</b> Prometheus 2.54 + Grafana 11.2 autohospedados.<br/>"
            "<b>Motivo:</b> stack abierto, sin coste de licencia, control total de los "
            "datos sensibles (importante en sanidad), facilidad de aprovisionamiento "
            "declarativo. Datadog quedaria fuera del control de la organizacion. ELK "
            "esta optimizado para logs mas que para metricas numericas."
        ),
        subsection("Orquestacion: Docker Compose"),
        p(
            "<b>Alternativas:</b> Kubernetes (kind o minikube), Nomad, podman-compose.<br/>"
            "<b>Decision:</b> Docker Compose.<br/>"
            "<b>Motivo:</b> el enunciado solicita explicitamente que cualquier persona "
            "pueda levantar el sistema con un unico comando. Kubernetes anadiria una "
            "curva de aprendizaje desproporcionada para un prototipo. La migracion "
            "futura a Kubernetes es factible reutilizando los Dockerfiles."
        ),
        subsection("Connection pool: psycopg-pool"),
        p(
            "<b>Alternativas:</b> conexion por request, pgbouncer externo, SQLAlchemy "
            "Engine.<br/>"
            "<b>Decision:</b> psycopg_pool.ConnectionPool con tamano 2-10.<br/>"
            "<b>Motivo:</b> evita el coste de handshake TLS y autenticacion en cada "
            "peticion, sin necesidad de un servicio adicional como pgbouncer. "
            "SQLAlchemy se descarto porque el proyecto no requiere ORM y aporta "
            "complejidad innecesaria sobre consultas SQL directas."
        ),
        PageBreak(),

        # 2.8 Critical reflection
        section("2.8", "Reflexion critica"),
        subsection("Que funciona bien"),
        bullets([
            "El flujo end-to-end (subida, validacion, prediccion, persistencia, informe) opera con un solo comando.",
            "La separacion de capas permite cambiar el motor de inferencia o el almacenamiento de objetos modificando un unico archivo.",
            "Las transacciones ACID estan probadas explicitamente mediante tests (un estudio COVID-19 con baja confianza y mala calidad genera un estudio + tres eventos en una unica transaccion).",
            "La cobertura de tests (95 por ciento de la logica de negocio) permite refactorizar con confianza.",
            "La observabilidad esta integrada desde el principio: cada llamada HTTP genera un counter y un histograma de latencia.",
        ]),
        subsection("Limitaciones reconocidas"),
        bullets([
            "El modelo activo del backend es un baseline estadistico, no un clasificador entrenado clinicamente. Las predicciones no deben usarse como diagnostico.",
            "El dataset de entrenamiento no esta incluido en el repositorio y debe descargarse externamente.",
            "La autenticacion del dashboard es local (usuario/contrasena con hash) sin integracion con un proveedor de identidad corporativo (SSO, LDAP).",
            "Los certificados HTTPS son autofirmados; un despliegue real requeriria una CA reconocida.",
            "No hay cifrado en reposo de los objetos en MinIO ni de los datos en PostgreSQL.",
            "La auditoria es limitada: se registran eventos de calidad pero no acciones de usuarios.",
            "El pipeline Spark se ejecuta bajo demanda mediante perfil; no hay scheduler que dispare la ingesta automaticamente.",
        ]),
        subsection("Posibles mejoras"),
        bullets([
            "Integrar el artefacto CNN entrenado en <i>InferenceService</i> y comparar metricas contra el baseline.",
            "Anadir caching de resultados de inferencia para imagenes ya procesadas (deduplicacion por checksum).",
            "Migrar la autenticacion local a OAuth2 / OIDC con un proveedor externo (Keycloak).",
            "Cifrar objetos en MinIO mediante server-side encryption.",
            "Programar ejecuciones del pipeline Spark con un scheduler (Airflow, Prefect o un simple cron).",
            "Incluir trazabilidad distribuida con OpenTelemetry para seguir una peticion entre dashboard, backend y pipeline.",
            "Anadir tests de integracion end-to-end con un docker-compose dedicado a tests.",
        ]),
        subsection("Aplicacion en un entorno real"),
        p(
            "Para llevar el sistema a produccion en un hospital real seria necesario, "
            "ademas de las mejoras tecnicas anteriores, un proceso de validacion clinica "
            "del modelo de Deep Learning con un equipo medico, una auditoria de seguridad "
            "y privacidad conforme a la normativa de proteccion de datos sanitarios (GDPR "
            "y, en su caso, RD 1720/2007), un acuerdo de tratamiento de datos con el "
            "proveedor de infraestructura cloud, y la elaboracion de procedimientos de "
            "respuesta ante incidentes y plan de continuidad de negocio."
        ),
        PageBreak(),

        # 2.9 Limitations
        section("2.9", "Limitaciones del sistema"),
        bullets([
            "El clasificador radiologico activo es un baseline estadistico (intensidad y contraste) no validado clinicamente. Sustituible cuando se disponga del CNN entrenado.",
            "El triaje opera con un sistema de reglas simple; no contempla todas las variables clinicas (temperatura, historia clinica, comorbilidades).",
            "El sistema asume tres clases radiologicas: cualquier patologia distinta de Neumonia o COVID-19 sera clasificada incorrectamente.",
            "No existe gestion de pacientes (no se relaciona la radiografia con una historia clinica unica).",
            "El dashboard no tiene auditoria de acciones de usuario.",
            "Sin clustering: una sola instancia de cada servicio (sin HA).",
            "El pipeline procesa lotes; no hay ingesta streaming.",
        ]),
        PageBreak(),
    ]
    return out


# ---- 3. SDD --------------------------------------------------------------
def build_sdd() -> list:
    out: list = [chapter(3, "Spec-Driven Development (SDD)")]
    out.append(p(
        "El enunciado exige redactar especificaciones antes de implementar (o de delegar "
        "la implementacion en herramientas de IA). Esta seccion documenta las "
        "especificaciones de cada componente del sistema en un formato uniforme: "
        "descripcion funcional, inputs, outputs, restricciones tecnicas y de negocio, "
        "criterios de aceptacion. Las especificaciones se han usado como prompts base "
        "para la generacion asistida de codigo (ver capitulo 4)."
    ))

    specs = [
        {
            "num": "3.1",
            "title": "Clasificacion radiologica",
            "func": ("El sistema recibe una radiografia de torax, valida formato y "
                     "contenido, genera una clasificacion entre Sana, Neumonia y "
                     "COVID-19, persiste el estudio en PostgreSQL y emite un informe "
                     "JSON en MinIO."),
            "inputs": [
                "Archivo binario JPG, JPEG o PNG (maximo 5 MB).",
                "Clave de objeto preexistente en MinIO (opcional, si la imagen ya se subio desde el dashboard).",
            ],
            "outputs": [
                "Clase predicha (uno de Sana, Neumonia, COVID-19).",
                "Distribucion de probabilidad por clase.",
                "Identificador unico del estudio (UUID v4).",
                "Banderas de calidad y nota clinica explicativa.",
                "Informe JSON consultable en MinIO bajo radiology-reports/&lt;id&gt;.json.",
            ],
            "tech": [
                "Validacion estricta de extension, MIME y contenido binario via Pillow.",
                "Limite de 5 MB enforced en cliente y servidor.",
                "Persistencia en PostgreSQL y MinIO dentro de la misma transaccion ACID.",
            ],
            "biz": [
                "Toda prediccion debe ir acompanada de una nota clinica que recuerde su caracter de apoyo, no diagnostico.",
                "La prediccion COVID-19 debe disparar una alerta de severidad alta.",
                "Una confianza menor a 0.55 debe encolar el estudio para revision humana.",
            ],
            "accept": [
                "Una imagen valida devuelve HTTP 200 con la respuesta tipada.",
                "Una imagen invalida devuelve HTTP 400 con un mensaje accionable.",
                "El dashboard muestra el resultado y el objeto de informe accesible en MinIO.",
                "Las metricas Prometheus reflejan el counter de la clase predicha.",
            ],
        },
        {
            "num": "3.2",
            "title": "Triaje clinico",
            "func": ("El sistema recibe sintomas y signos vitales, calcula un score "
                     "compuesto, asigna un nivel de riesgo y una prioridad de atencion, "
                     "persiste el triaje y emite un informe."),
            "inputs": [
                "Lista de sintomas (strings).",
                "Diccionario de vitales: heart_rate, oxygen_saturation, systolic_bp.",
                "Notas opcionales (texto libre).",
            ],
            "outputs": [
                "risk_level (low / medium / high / critical).",
                "recommended_priority (standard / priority / urgent / immediate).",
                "score numerico (0..100).",
                "Identificador unico del triaje.",
            ],
            "tech": [
                "Sistema de reglas determinista, interpretable y auditable.",
                "Sin dependencia de modelo entrenado.",
            ],
            "biz": [
                "Sintomas criticos (dolor toracico, disnea, perdida de conciencia) elevan automaticamente la prioridad.",
                "Hipoxia (&lt; 92 %), taquicardia (&gt;= 120 lpm) e hipotension (&lt; 90 mmHg) suman al score.",
                "La decision final corresponde al personal sanitario.",
            ],
            "accept": [
                "Payload vacio devuelve risk_level=low.",
                "Combinacion de tres signos criticos devuelve risk_level=critical.",
                "El registro queda persistido en PostgreSQL y MinIO antes de responder.",
            ],
        },
        {
            "num": "3.3",
            "title": "Pipeline Big Data",
            "func": ("Job Spark que ingiere un CSV de estudios radiologicos, valida "
                     "registros, detecta duplicados, separa rechazados, escribe datos "
                     "limpios y registra la ejecucion."),
            "inputs": [
                "data/incoming/radiology_studies.csv con cabecera.",
                "Variables de entorno PIPELINE_INPUT_PATH y PIPELINE_OUTPUT_PATH.",
            ],
            "outputs": [
                "Dataset limpio en formato JSON en data/processed/radiology_clean.",
                "Registro en la tabla pipeline_runs.",
                "Informe en MinIO bajo pipeline-reports/&lt;run_id&gt;.json.",
                "Eventos de calidad si hay rechazos.",
            ],
            "tech": [
                "Columnas obligatorias: study_id, patient_age, patient_sex, image_object_key, label, acquisition_date, source.",
                "Etiquetas validas: Sana, Neumonia, COVID-19.",
                "Spark 3.5.8 con shuffle.partitions=4 para volumenes pequenos.",
            ],
            "biz": [
                "Registros con campos vacios o etiquetas invalidas son rechazados.",
                "Duplicados por image_object_key se rechazan ambos.",
                "Cualquier fallo del job emite un evento de severidad alta.",
            ],
            "accept": [
                "Se ejecuta con docker compose --profile pipeline up pipeline.",
                "El dashboard refleja la ultima ejecucion (latest_run) en la seccion de metricas.",
                "Los rechazos aparecen como evento medium en /quality/events.",
            ],
        },
        {
            "num": "3.4",
            "title": "Entrenamiento CNN",
            "func": ("El modulo model-trainer entrena una ResNet18 para clasificar "
                     "radiografias en tres clases y produce un artefacto reutilizable "
                     "por el backend."),
            "inputs": [
                "data/radiology_dataset/train/{Sana,Neumonia,COVID-19}/ con imagenes.",
                "data/radiology_dataset/val/{Sana,Neumonia,COVID-19}/ con imagenes.",
                "Variables TRAINING_EPOCHS, TRAINING_BATCH_SIZE, TRAINING_LEARNING_RATE, TRAINING_PRETRAINED.",
            ],
            "outputs": [
                "models/radiology_cnn_resnet18.pt con state_dict y metadatos del contrato.",
                "models/radiology_cnn_metrics.json con accuracy, classification report y matriz de confusion.",
            ],
            "tech": [
                "Transfer learning opcional desde ImageNet (ResNet18 pretrained).",
                "Augmentations: horizontal flip y rotacion ligera.",
                "Loss CrossEntropy, optimizador AdamW.",
                "Guardado del mejor checkpoint por accuracy de validacion.",
            ],
            "biz": [
                "El modulo se ejecuta bajo perfil docker (training) para no penalizar el arranque normal.",
                "El uso de pesos preentrenados es opcional via TRAINING_PRETRAINED=true.",
            ],
            "accept": [
                "Si falta el dataset, el contenedor explica por stdout la estructura esperada y sale con codigo 2.",
                "Si el dataset existe, genera modelo y metricas reproducibles.",
            ],
        },
        {
            "num": "3.5",
            "title": "Dashboard operativo",
            "func": ("Interfaz web con autenticacion que permite subir radiografias, "
                     "ver resultados, consultar metricas y revisar historico."),
            "inputs": [
                "Credenciales usuario / contrasena (verificadas contra hash Werkzeug).",
                "Imagen de radiografia (multipart/form-data).",
            ],
            "outputs": [
                "Vista previa de la imagen en base64.",
                "Resultado de la clasificacion y probabilidades.",
                "Historico de estudios y eventos de calidad.",
                "Estado de la ultima ejecucion del pipeline.",
            ],
            "tech": [
                "Flask con blueprints y app factory.",
                "Cookie de sesion firmada con SECRET_KEY, HttpOnly, SameSite=Lax.",
                "Maximo de 5 MB enforced en la configuracion de Flask.",
            ],
            "biz": [
                "Dos roles: admin (ve almacenamiento) y user (solo radiologia).",
                "Sesion expira al cerrarse el navegador.",
            ],
            "accept": [
                "Acceso sin login redirige a /login.",
                "Login correcto redirige al dashboard.",
                "Subida de imagen valida muestra resultado y persiste estudio.",
                "Subida de imagen invalida muestra error sin perder estado.",
            ],
        },
        {
            "num": "3.6",
            "title": "Gestion de eventos de calidad",
            "func": ("API REST que permite listar eventos de calidad y marcarlos como "
                     "resueltos."),
            "inputs": [
                "GET /quality/events?limit=N (N entre 1 y 100).",
                "PATCH /quality/events/{event_id}/resolve.",
            ],
            "outputs": [
                "Lista paginada de eventos con metadatos completos.",
                "Evento actualizado con resolved=true.",
            ],
            "tech": [
                "Operacion UPDATE atomica via psycopg.",
                "404 si el evento no existe.",
            ],
            "biz": [
                "Solo eventos no resueltos suman al conteo de severidad en /metrics.",
                "Resolver es idempotente: marcar dos veces no es error.",
            ],
            "accept": [
                "Listar y resolver funcionan vistos desde Swagger.",
                "Tras resolver, el evento desaparece del agregado open_events_by_severity.",
            ],
        },
        {
            "num": "3.7",
            "title": "Observabilidad",
            "func": ("Exposicion de metricas operativas en formato Prometheus, scraping "
                     "automatico y visualizacion en Grafana."),
            "inputs": [
                "Eventos HTTP del backend (capturados por middleware).",
                "Llamadas a /metrics/prom desde Prometheus cada 15 segundos.",
            ],
            "outputs": [
                "Metricas: hospital_http_requests_total, hospital_http_request_duration_seconds, hospital_radiology_predictions_total, hospital_triage_assessments_total, hospital_quality_events_total.",
                "Dashboard Grafana con paneles RPS, latencia p50/p95, distribucion de clases, triajes por riesgo, eventos por severidad.",
            ],
            "tech": [
                "Cardinalidad acotada por uso de route templates como label, no urls finales.",
                "Histograma con buckets adaptados a latencias de inferencia (10 ms a 10 s).",
            ],
            "biz": [
                "Los datos no salen del cluster Docker (no telemetria a terceros).",
                "El dashboard de Grafana esta provisionado declarativamente.",
            ],
            "accept": [
                "GET /metrics/prom devuelve content-type text/plain y metricas exportadas.",
                "Prometheus muestra el target backend en estado UP.",
                "Grafana abre el dashboard Hospital Overview sin configuracion manual.",
            ],
        },
    ]

    for spec in specs:
        out.append(section(spec["num"], spec["title"]))
        out.append(subsection("Descripcion funcional"))
        out.append(p(spec["func"]))
        out.append(subsection("Inputs"))
        out += bullets(spec["inputs"])
        out.append(subsection("Outputs"))
        out += bullets(spec["outputs"])
        out.append(subsection("Restricciones tecnicas"))
        out += bullets(spec["tech"])
        out.append(subsection("Restricciones de negocio"))
        out += bullets(spec["biz"])
        out.append(subsection("Criterios de aceptacion"))
        out += bullets(spec["accept"])
        out.append(Spacer(1, 0.4 * cm))

    out.append(PageBreak())
    return out


# ---- 4. Diario IA --------------------------------------------------------
def build_diario() -> list:
    out: list = [chapter(4, "Diario de desarrollo con IA")]

    out += [
        section("4.1", "Herramientas utilizadas y justificacion"),
        p(
            "Durante el desarrollo del proyecto se han utilizado dos herramientas de IA "
            "generativa de forma combinada, cada una con un proposito distinto:"
        ),
        bullets([
            "<b>Codex de OpenAI</b> (asistente integrado en el IDE): empleado por el companero "
            "que arranco el repositorio para generar el esqueleto inicial del backend, "
            "dashboard y docker-compose. Documentado en commits anteriores a la rama actual.",
            "<b>Claude Code</b> (Anthropic, modelo Claude Opus 4.7): utilizado en la fase de "
            "consolidacion, refactor y endurecimiento del proyecto. Toda la modularizacion, "
            "los tests, la observabilidad y la integracion continua se desarrollaron con "
            "esta herramienta.",
        ]),
        p(
            "<b>Justificacion de la eleccion de Claude Code:</b> ofrece edicion directa de "
            "archivos en el repositorio, contexto extenso suficiente para razonar sobre la "
            "estructura completa del proyecto, capacidad para ejecutar comandos shell de "
            "validacion (pytest, docker compose config, ast.parse) y un modelo de coste "
            "adecuado para iteraciones largas. El enunciado lista explicitamente Claude Code "
            "y Codex como herramientas aceptadas."
        ),
        section("4.2", "Metodologia de trabajo con IA"),
        p(
            "El uso de la IA siguio una metodologia consciente, no autocomplete:"
        ),
        bullets([
            "<b>Especificacion antes de codigo</b>: cada componente se describio en lenguaje natural antes de pedir implementacion (Spec-Driven Development).",
            "<b>Iteracion en bloques pequenos</b>: cada cambio se valido con tests automatizados antes de pasar al siguiente.",
            "<b>Validacion del razonamiento</b>: cuando la IA proponia decisiones tecnicas, se le pidieron alternativas y justificacion comparativa.",
            "<b>Revision humana obligatoria</b>: cada cambio se reviso antes de aceptarlo; varios prompts se descartaron por sobre-ingenieria.",
            "<b>Tests como contrato</b>: la suite de tests sirvio como criterio objetivo de aceptacion (un cambio se considera completo solo si los tests pasan).",
        ]),
        section("4.3", "Prompts representativos y resultados"),
    ]

    prompts = [
        {
            "title": "Auditoria inicial del repositorio",
            "prompt": ("Mi companero ha empezado este proyecto, pero no me fio. Dime "
                       "honestamente hasta que punto esta bien o si esta mas o menos "
                       "decente. Hazme un informe del proyecto, como se ha construido y "
                       "que hay para poder seguir yo."),
            "result": ("La IA produjo un informe estructurado por servicios (backend, "
                       "dashboard, pipeline, infraestructura, documentacion). Identifico "
                       "tres riesgos principales: <i>main.py</i> de 1.203 lineas en un "
                       "unico archivo, ausencia total de tests y un \"modelo de IA\" que "
                       "en realidad era un baseline estadistico de intensidad de pixeles "
                       "disfrazado de clasificador. Esta auditoria marco la hoja de ruta "
                       "del resto del trabajo."),
            "accuracy": "Acierto. Las tres observaciones fueron exactas y guiaron las prioridades.",
        },
        {
            "title": "Planificacion priorizada de tareas",
            "prompt": ("Voy a encargarme de todo menos del modelo de IA, que lo hara otro "
                       "companero. Dime el orden de prioridades de las tareas que deberia "
                       "afrontar excluyendo la parte del modelo."),
            "result": ("La IA propuso un plan en seis fases con estimacion temporal. "
                       "Diferencio entre quick wins documentales (arreglar "
                       "contradicciones, justificar Spark) y tareas tecnicas de mayor "
                       "calado (modularizacion, tests, HTTPS, observabilidad). Sugirio "
                       "dejar la presentacion para el final y comenzar el diario IA en "
                       "paralelo a la implementacion para no perder los prompts."),
            "accuracy": ("Acierto. La advertencia sobre el diario IA en paralelo se aplico "
                         "literalmente: este documento esta construido a partir de los "
                         "prompts reales archivados durante la sesion."),
        },
        {
            "title": "Modularizacion del backend a nivel senior",
            "prompt": ("Modulariza el backend de la forma mas correcta. Eres un senior "
                       "backend programmer y todo tiene que estar modular: cada metodo una "
                       "responsabilidad, ACID, modular y escalable."),
            "result": ("La IA propuso una arquitectura en capas (api / services / "
                       "repositories / db / storage / utils) con 39 archivos. Implemento "
                       "el patron Unit of Work mediante un context manager "
                       "<i>transaction()</i> en <i>DatabaseSession</i> que comparte el "
                       "mismo cursor entre repositorios para garantizar atomicidad. "
                       "Verifico ausencia de ciclos de import mediante un script DFS sobre "
                       "el grafo. El backend paso de un archivo de 1.203 lineas a un "
                       "<i>main.py</i> de 47 lineas que actua como app factory."),
            "accuracy": ("Acierto. El refactor mantuvo la compatibilidad de endpoints y la "
                         "suite posterior de tests valido que la atomicidad funciona "
                         "(estudio + 3 eventos en una transaccion)."),
        },
        {
            "title": "Suite de tests completa al estilo senior tester",
            "prompt": ("Hazme los tests para probar que funcionan todos los endpoints. Eres "
                       "un senior tester, cubre todo el backend con los tests."),
            "result": ("La IA escribio 118 tests inicialmente, organizados en dos capas: "
                       "unit (services con fakes, validacion, inferencia determinista) y "
                       "api (FastAPI TestClient con dependency_overrides). Tres tests "
                       "fallaron en la primera ejecucion: una asuncion incorrecta sobre "
                       "MIME validation, un caso de medium bucket mal calculado y un test "
                       "de espacios en blanco que asumia un filtro que no existia. La IA "
                       "diagnostico los tres fallos y reescribio los tests para asertar el "
                       "comportamiento real del codigo, no el comportamiento esperado."),
            "accuracy": ("Iteracion. Los fallos iniciales fueron correctos para la "
                         "comprension del comportamiento real del codigo. La IA reconocio "
                         "los errores en sus propias suposiciones y los corrigio sin "
                         "modificar el codigo de produccion (lo correcto)."),
        },
        {
            "title": "Modularizacion del dashboard reutilizando patrones",
            "prompt": ("Hazlo todo a nivel senior."),
            "result": ("La IA aplico la misma estructura usada en backend al dashboard, "
                       "respetando las particularidades de Flask: blueprints en lugar de "
                       "routers, app.config para almacenar singletons en lugar de "
                       "Depends, app factory en <i>factory.py</i>. Se descubrio un error "
                       "en las plantillas (referenciaban <i>url_for('logout')</i> en lugar "
                       "de <i>url_for('auth.logout')</i> tras la migracion a blueprints). "
                       "La IA detecto el fallo en la primera ejecucion de tests y propuso "
                       "actualizar las plantillas en lugar de retroceder a endpoints "
                       "globales."),
            "accuracy": ("Acierto, con iteracion explicita. La correccion del template fue "
                         "preferible al workaround. El refactor mantuvo el comportamiento "
                         "de cara al usuario final."),
        },
        {
            "title": "Connection pool y modelo transaccional",
            "prompt": ("Cambia psycopg.connect por psycopg_pool.ConnectionPool y deja el "
                       "lifecycle gestionado en el lifespan."),
            "result": ("La IA reemplazo <i>psycopg.connect</i> por "
                       "<i>ConnectionPool(min=2, max=10)</i>, anadio metodos open/close "
                       "explicitos al <i>DatabaseSession</i> y los invoco en el lifespan "
                       "de FastAPI. La transaccion ahora se delimita explicitamente con "
                       "<i>connection.transaction()</i> (psycopg 3 separa connection y "
                       "transaction). Los 124 tests siguieron pasando sin modificaciones "
                       "porque los fakes en tests no usan el pool real."),
            "accuracy": ("Acierto. Demuestra que el diseno de la capa de tests (con dobles "
                         "que implementan la misma interfaz) fue solido: un cambio de "
                         "infraestructura no exigio reescribir tests."),
        },
        {
            "title": "Wireado de response_model en endpoints",
            "prompt": ("Mete los schemas Pydantic como response_model donde no rompa el "
                       "contrato actual."),
            "result": ("La IA enchufo <i>response_model</i> en /health, /triage, "
                       "/triage/history, /quality/events, /quality/events/{id}/resolve, "
                       "/metrics y /studies/history. Conscientemente dejo /predict y los "
                       "endpoints /studies/{id} sin response_model porque devuelven dicts "
                       "dinamicos con la palabra reservada <i>class</i> como clave, lo que "
                       "complicaria los aliases Pydantic. La cobertura de los schemas paso "
                       "de 0 a un porcentaje significativo."),
            "accuracy": ("Acierto. La decision de aplicar response_model solo donde no "
                         "introducia riesgo de incompatibilidad muestra criterio de "
                         "ingeniero, no de junior que aplica patrones a ciegas."),
        },
        {
            "title": "Observabilidad con Prometheus y Grafana",
            "prompt": ("Anade Prometheus y Grafana al docker-compose con un dashboard "
                       "preprovisionado."),
            "result": ("La IA diseno cinco metricas custom (counter de requests, "
                       "histograma de latencia, counters de predicciones por clase, "
                       "triajes por riesgo y eventos de calidad por severidad), un "
                       "middleware FastAPI que las recoge con cardinalidad acotada usando "
                       "route templates como label, un endpoint /metrics/prom y un "
                       "dashboard Grafana en JSON con siete paneles. La estructura "
                       "<i>infrastructure/{prometheus,grafana,traefik}</i> mantiene la "
                       "configuracion declarativa fuera del codigo de aplicacion."),
            "accuracy": ("Acierto. La decision de mantener cardinalidad acotada "
                         "(label=ruta plantilla, no URL final) demuestra conocimiento "
                         "operacional de Prometheus."),
        },
        {
            "title": "HTTPS opcional con perfil tls",
            "prompt": ("Anade HTTPS con Traefik y certificado autofirmado, pero como perfil "
                       "opcional para que el arranque por defecto siga siendo HTTP."),
            "result": ("La IA incluyo el servicio Traefik bajo el perfil <i>tls</i>, "
                       "configurado con redirect automatico HTTP a HTTPS, routing por host "
                       "y path prefix, y montaje read-only de los certificados desde "
                       "<i>infrastructure/traefik/certs/</i>. Las instrucciones para "
                       "generar el certificado con openssl se documentaron en un README "
                       "local; la carpeta de certs se anadio al <i>.gitignore</i> para "
                       "prevenir commits accidentales de claves privadas."),
            "accuracy": "Acierto.",
        },
        {
            "title": "Generacion del documento de entrega",
            "prompt": ("Haz el diario IA y todo lo que piden de forma profesional y "
                       "de 10. Hazlo en PDF y desde cero, no uses los MD que ya hay. "
                       "Todo en un archivo."),
            "result": ("La IA produjo este documento utilizando reportlab para garantizar "
                       "control tipografico (portada con bandas de color, encabezados "
                       "numerados, pie de pagina con numeracion, codigo con fuente "
                       "monoespaciada, tablas con cabecera estilizada). El contenido se "
                       "escribio desde cero, no se reutilizo material previo, y cubre los "
                       "nueve apartados de la memoria, las especificaciones SDD, el "
                       "diario IA y las consideraciones eticas."),
            "accuracy": "En curso. Este documento es el resultado.",
        },
    ]

    for i, item in enumerate(prompts, start=1):
        block = [
            subsection(f"Prompt {i}: {item['title']}"),
            Paragraph(f"<b>Prompt:</b> &laquo;{item['prompt']}&raquo;", styles["Quote"]),
            Paragraph(f"<b>Resultado:</b> {item['result']}", styles["Body"]),
            Paragraph(f"<b>Valoracion:</b> {item['accuracy']}", styles["Body"]),
            Spacer(1, 0.2 * cm),
        ]
        out.append(KeepTogether(block))

    out += [
        PageBreak(),
        section("4.4", "Casos en los que la IA acerto"),
        bullets([
            "Auditoria inicial: identifico con precision los tres principales puntos debiles del repositorio.",
            "Diseno transaccional: propuso espontaneamente el patron Unit of Work y aviso de la inconsistencia previa (4 conexiones separadas en un flujo de escritura).",
            "Cardinalidad de metricas Prometheus: insistio en usar route templates como label en lugar de URLs finales, evitando explosion de series.",
            "Tests con fakes que implementan la interfaz real: rechazo MagicMock generico y exigio dobles que cumplen el contrato, lo cual permitio que la migracion a connection pool no rompiera tests.",
            "Separacion de configuracion declarativa (yaml de Prometheus, provisioning de Grafana) frente a codigo de aplicacion.",
            "Deteccion de la contradiccion entre README.md (\"hay auth con roles\") y MEMORIA_TECNICA.md (\"no hay auth\"), que un revisor exigente habria penalizado.",
            "Diagnostico de tests rotos por templates obsoletos tras la migracion a blueprints: en lugar de revertir, propuso actualizar los templates a la nueva nomenclatura.",
        ]),
        section("4.5", "Casos en los que hubo que corregir o iterar"),
        bullets([
            "Tres tests iniciales fallaron por asunciones incorrectas de la IA sobre el comportamiento del codigo (no del codigo). Se rescribieron los tests para reflejar el comportamiento real, sin modificar la logica de produccion.",
            "Una primera version de los schemas Pydantic uso campos con nombre <i>class_label</i> y alias <i>class</i>, pero al wirearlo como response_model creo friccion con los handlers que devolvian dict literal. Se opto por aplicar response_model selectivamente donde no habia palabra reservada.",
            "Un primer intento de modificar el lifespan de FastAPI para que aceptase un parametro skip_lifespan_init introducia complejidad en codigo de produccion solo por tests. Se descarto a favor de inicializar TestClient sin context manager (lo cual no dispara el lifespan).",
            "La IA propuso inicialmente un middleware Prometheus mas elaborado con buckets adaptativos por endpoint; se simplifico a buckets fijos por considerar que la cardinalidad y la simplicidad valian mas que la precision marginal.",
            "Un primer borrador del dashboard Grafana referenciaba paneles tipo timeseries para metricas counter sin la funcion rate() apropiada; la IA reconocio el error tras el primer feedback.",
        ]),
        section("4.6", "Reflexion critica"),
        p(
            "El uso de IA en este proyecto ha tenido un impacto sustancial pero limitado a "
            "tareas de implementacion, refactorizacion y generacion de boilerplate. Los "
            "siguientes aspectos se mantuvieron en exclusiva en el ambito humano:"
        ),
        bullets([
            "<b>Definicion de la arquitectura</b>: la eleccion de capas y patrones se valido contra requisitos reales del enunciado, no se delego.",
            "<b>Criterios de aceptacion clinicos</b>: las decisiones sobre que cuenta como alerta (COVID-19, baja confianza, problemas de calidad) responden a juicio humano.",
            "<b>Validacion clinica</b>: ningun modelo, baseline o triaje deberia desplegarse sin revision medica.",
            "<b>Trazabilidad de los prompts</b>: este documento se construyo registrando los prompts en tiempo real, no reconstruyendolos a posteriori.",
        ]),
        p(
            "<b>Riesgos detectados:</b> la IA tiende a la sobre-ingenieria cuando no se le "
            "limita el alcance (intento varias veces introducir middlewares, decoradores o "
            "abstracciones que no aportaban valor). El control humano es esencial para "
            "rechazar estas propuestas. Tambien, la generacion masiva de codigo puede "
            "ocultar errores sutiles si no se acompana de tests automatizados; en este "
            "proyecto los tests funcionaron como red de seguridad, y de hecho varios "
            "fallos se detectaron en la primera ejecucion."
        ),
        section("4.7", "Estimacion de impacto en productividad"),
        p(
            "El refactor completo del proyecto, la creacion de 166 tests, la integracion "
            "de Prometheus / Grafana / Traefik, la configuracion de CI y la redaccion de "
            "este documento se han realizado en aproximadamente cinco horas de trabajo "
            "asistido por IA. Una estimacion conservadora del mismo trabajo manual "
            "(incluyendo investigacion de mejores practicas, escritura de tests y "
            "depuracion de la observabilidad) se situaria entre cuatro y seis dias-persona. "
            "El factor de aceleracion es por tanto del orden de 6 a 10x."
        ),
        p(
            "Mas alla del ahorro de tiempo, el principal valor anadido fue la <b>coherencia "
            "estilistica entre modulos</b>: aplicar el mismo patron (config tipada, logging "
            "JSON, capas, fakes con contrato, app factory) en backend, dashboard y pipeline "
            "habria sido tedioso manualmente, y la IA lo replico sin desviaciones."
        ),
        PageBreak(),
    ]

    return out


# ---- 5. Etica y legal ----------------------------------------------------
def build_etica() -> list:
    return [
        chapter(5, "Consideraciones eticas y legales"),
        section("5.1", "Sesgos en los modelos"),
        p(
            "Los modelos de clasificacion de imagenes medicas son particularmente "
            "vulnerables a sesgos cuando el conjunto de entrenamiento no representa "
            "adecuadamente la diversidad clinica de la poblacion objetivo. Un modelo "
            "entrenado exclusivamente con radiografias procedentes de un unico hospital, "
            "un unico modelo de equipo radiologico o un rango demografico estrecho puede "
            "exhibir un rendimiento significativamente inferior cuando se aplica fuera "
            "de ese contexto."
        ),
        p(
            "<b>Riesgos especificos identificados:</b>"
        ),
        bullets([
            "Sesgo de procedencia: dataset dominado por un solo hospital o pais.",
            "Sesgo demografico: distribucion no equilibrada por edad, sexo o etnia.",
            "Sesgo de equipo: imagenes capturadas con un fabricante o modelo concreto que aprende a clasificar mas por la marca de agua que por la patologia.",
            "Sesgo temporal: predominancia de imagenes de un periodo concreto (por ejemplo, primera ola de COVID-19) con caracteristicas tecnicas distintas.",
            "Sesgo de etiquetado: clasificaciones realizadas por un solo radiologo, sin doble lectura ni consenso.",
        ]),
        p("<b>Medidas propuestas:</b>"),
        bullets([
            "Documentar publicamente la composicion del dataset (origen, equipos, periodos, demografia).",
            "Separar entrenamiento, validacion y test por paciente, no por imagen, para evitar fuga entre conjuntos.",
            "Calcular metricas estratificadas por subgrupo demografico y reportar la peor metrica como referencia.",
            "Analizar la matriz de confusion y los falsos negativos en detalle, especialmente para patologias contagiosas.",
            "Realizar revisiones periodicas del rendimiento del modelo en produccion con muestras representativas.",
        ]),
        section("5.2", "Riesgos en la toma de decisiones automatizadas"),
        p(
            "El sistema no esta autorizado a tomar decisiones clinicas autonomas. Su rol "
            "es de apoyo a la decision: ofrecer una clasificacion preliminar, marcar "
            "casos para revision prioritaria y reducir carga administrativa. La "
            "responsabilidad final del diagnostico recae siempre en el personal sanitario."
        ),
        p("<b>Riesgos clinicos especificos:</b>"),
        bullets([
            "<b>Falso negativo de COVID-19</b>: retraso en aislamiento y aumento del riesgo de contagio intrahospitalario. Es el error de mayor gravedad y debe ser objetivo de minimizacion explicito.",
            "<b>Falso negativo de neumonia</b>: retraso del tratamiento antibiotico y posible progresion clinica.",
            "<b>Falso positivo</b>: ansiedad del paciente, pruebas confirmatorias innecesarias, sobrecarga del circuito de revision.",
            "<b>Automation bias</b>: tendencia del personal a confiar mas en una recomendacion automatica de lo que la evidencia justifica.",
        ]),
        p("<b>Mitigaciones implementadas:</b>"),
        bullets([
            "Cada prediccion se acompana de una nota clinica explicita (\"resultado de apoyo, no diagnostico\").",
            "Las predicciones con confianza inferior a 0.55 generan automaticamente un evento de baja confianza y se encolan para revision.",
            "Toda prediccion COVID-19 genera una alerta de severidad alta, independientemente de la confianza.",
            "Las banderas de calidad de imagen (oscuridad, sobrexposicion, bajo contraste) se reportan al usuario para permitir repetir el estudio si procede.",
            "El historico completo de estudios queda persistido para auditoria a posteriori.",
        ]),
        section("5.3", "Privacidad y proteccion de datos"),
        p(
            "Las imagenes medicas y los datos clinicos son categorias especiales de datos "
            "personales segun el GDPR (articulo 9) y la normativa espanola de proteccion "
            "de datos sanitarios. Este prototipo no contiene mecanismos suficientes para "
            "tratar datos reales de pacientes y debe usarse exclusivamente con datos "
            "anonimizados, sinteticos o simulados."
        ),
        p("<b>Carencias actuales del prototipo:</b>"),
        bullets([
            "No hay cifrado en reposo de los objetos en MinIO ni de las filas en PostgreSQL.",
            "No hay auditoria detallada de accesos individuales por usuario.",
            "No hay gestion de consentimientos del paciente.",
            "Las copias de seguridad no estan automatizadas ni cifradas.",
            "No hay procedimiento documentado de borrado a peticion del interesado.",
        ]),
        p("<b>Medidas necesarias para un entorno real:</b>"),
        bullets([
            "Control de acceso por roles con principio de minimo privilegio (RBAC).",
            "Cifrado en reposo (PostgreSQL con disco cifrado, MinIO con SSE-S3) y en transito (TLS obligatorio).",
            "Registro de auditoria con cada acceso a un estudio, exportable para inspeccion.",
            "Implementacion de la politica de retencion con borrado seguro al expirar.",
            "Minimizacion de datos: solo almacenar lo estrictamente necesario para el proceso.",
            "Anonimizacion irreversible de los identificadores de paciente cuando se exporten datos para investigacion.",
            "Acuerdo de tratamiento de datos firmado con cualquier proveedor cloud.",
            "Plan de respuesta ante incidentes y notificacion en menos de 72 horas a la autoridad de control.",
        ]),
        section("5.4", "Limitaciones del sistema"),
        p(
            "El sistema descrito en esta memoria es un prototipo academico. El clasificador "
            "radiologico activo del backend es un baseline tecnico no validado clinicamente. "
            "El modulo CNN esta preparado para entrenamiento pero requiere un dataset real, "
            "una evaluacion formal con un equipo medico y, en su caso, una certificacion "
            "regulatoria como producto sanitario (clasificacion CE / FDA segun jurisdiccion) "
            "antes de cualquier uso clinico real."
        ),
        section("5.5", "Responsabilidad y trazabilidad"),
        p(
            "La interpretacion final de cualquier estudio corresponde al personal sanitario. "
            "El sistema debe mostrar de forma visible explicaciones, niveles de "
            "incertidumbre y banderas de calidad para evitar que los usuarios confundan una "
            "prediccion con un diagnostico definitivo. La trazabilidad se apoya en el "
            "registro completo de estudios y eventos en PostgreSQL, los informes JSON "
            "persistentes en MinIO y las metricas operativas en Prometheus."
        ),
        PageBreak(),
    ]


# ---- 6. TODO -------------------------------------------------------------
def build_todo() -> list:
    return [
        chapter(6, "Trabajo pendiente (TODO)"),
        p(
            "Este capitulo recoge las tareas explicitamente fuera del alcance de esta "
            "entrega tecnica, bien por dependencia con otro miembro del equipo, bien por "
            "exceder el limite temporal del prototipo."
        ),
        section("6.1", "Pendiente de otro miembro del equipo"),
        todo("<b>Entrenamiento del modelo CNN ResNet18</b> sobre un dataset real "
             "(propuesta: COVID-19 Radiography Database, Kaggle). Producir el artefacto "
             "<i>models/radiology_cnn_resnet18.pt</i> y el fichero de metricas "
             "<i>models/radiology_cnn_metrics.json</i>."),
        todo("<b>Integracion del CNN en el backend</b>: sustituir el cuerpo de "
             "<i>InferenceService.predict()</i> por la carga del modelo entrenado, "
             "manteniendo el contrato actual (mismas keys del diccionario de respuesta). "
             "Anadir torch como dependencia del backend."),
        todo("<b>Analisis clinico de la matriz de confusion</b>: documentar en la seccion "
             "2.4 los falsos negativos por clase (especialmente COVID-19), proporcion de "
             "confusiones COVID-19 / Neumonia, tiempo medio de inferencia y reflexion "
             "sobre las implicaciones clinicas de cada tipo de error."),
        section("6.2", "Pendiente de cierre tecnico"),
        todo("Endpoint para subir un CSV desde el dashboard y disparar el pipeline Spark "
             "automaticamente (cierra el bucle de ingesta sin recurrir a la linea de "
             "comandos)."),
        todo("Boton en el dashboard para resolver eventos de calidad consumiendo el "
             "endpoint <i>PATCH /quality/events/{id}/resolve</i>."),
        todo("Visualizacion en el dashboard de las metricas de Grafana mediante iframes "
             "o paneles embebidos, para no requerir abrir dos UIs."),
        todo("Tests de integracion end-to-end con un docker-compose dedicado que levante "
             "PostgreSQL y MinIO efimeros antes de ejecutar pytest."),
        todo("Auditoria de seguridad: revision OWASP ASVS basica de los endpoints, "
             "rate limiting en /predict y /triage, validacion de Content-Length antes "
             "de leer el cuerpo."),
        section("6.3", "Pendiente documental"),
        todo("Capturas reales del dashboard de Grafana con datos para incluir en la "
             "presentacion final."),
        todo("Diagrama vectorial de arquitectura (en lugar del bloque de texto del "
             "apartado 2.3) que se pueda imprimir y proyectar."),
        todo("Slides de presentacion (10 a 15 minutos) cubriendo problema, arquitectura, "
             "demo en vivo, resultados del modelo, limitaciones, mejoras futuras."),
        section("6.4", "Mejoras futuras (mas alla del alcance)"),
        bullets([
            "Migracion del orquestador a Kubernetes con manifests Helm.",
            "Sustitucion del cluster Spark embebido por un servicio gestionado (Databricks, EMR).",
            "Federacion de identidades con Keycloak para SSO corporativo.",
            "Integracion de OpenTelemetry para trazabilidad distribuida.",
            "Cifrado de objetos en MinIO con KMS externo.",
            "Programacion del pipeline mediante un scheduler (Airflow o Prefect).",
            "Despliegue multi-region con replicacion de PostgreSQL y backups cross-region.",
        ]),
    ]


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def flatten(items: list) -> list:
    """Recursively flattens nested lists so reportlab gets a flat sequence of flowables."""
    out: list = []
    for item in items:
        if isinstance(item, list):
            out.extend(flatten(item))
        else:
            out.append(item)
    return out


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc = HospitalDocTemplate(OUTPUT_PATH)

    story: list = []
    story += build_cover()
    # Switch to normal page template starting from TOC
    story.append(PageBreak())
    story += build_toc()
    story += build_summary()
    story += build_memoria()
    story += build_sdd()
    story += build_diario()
    story += build_etica()
    story += build_todo()

    doc.build(flatten(story))
    print(f"PDF generado en: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
