#Generador de la Memoria Tecnica del Hospital Project.
from __future__ import annotations

from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
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


OUTPUT_PATH = Path(__file__).resolve().parent / "Memoria_Tecnica.pdf"

NAVY = colors.HexColor("#0F2547")
BLUE = colors.HexColor("#1F4E8E")
TEAL = colors.HexColor("#2E8B8B")
GRAY = colors.HexColor("#4A4A4A")
LIGHT = colors.HexColor("#EAEFF5")
SOFT = colors.HexColor("#F7F9FC")
CODE_BG = colors.HexColor("#F4F4F4")
WARN = colors.HexColor("#B85C00")
OK_GREEN = colors.HexColor("#1E7E5C")


base = getSampleStyleSheet()

styles = {
    "CoverTitle": ParagraphStyle(
        "CoverTitle", parent=base["Title"], fontName="Helvetica-Bold",
        fontSize=30, leading=36, textColor=NAVY, alignment=TA_CENTER, spaceAfter=18,
    ),
    "CoverSubtitle": ParagraphStyle(
        "CoverSubtitle", parent=base["Title"], fontName="Helvetica",
        fontSize=16, leading=22, textColor=GRAY, alignment=TA_CENTER, spaceAfter=10,
    ),
    "CoverHospital": ParagraphStyle(
        "CoverHospital", parent=base["Title"], fontName="Helvetica-Bold",
        fontSize=18, leading=24, textColor=TEAL, alignment=TA_CENTER, spaceAfter=10,
    ),
    "CoverAuthors": ParagraphStyle(
        "CoverAuthors", parent=base["Normal"], fontName="Helvetica-Bold",
        fontSize=13, leading=18, textColor=NAVY, alignment=TA_CENTER, spaceAfter=4,
    ),
    "CoverMeta": ParagraphStyle(
        "CoverMeta", parent=base["Normal"], fontName="Helvetica",
        fontSize=11, leading=15, textColor=GRAY, alignment=TA_CENTER,
    ),
    "Chapter": ParagraphStyle(
        "Chapter", parent=base["Heading1"], fontName="Helvetica-Bold",
        fontSize=22, leading=28, textColor=NAVY, spaceBefore=10, spaceAfter=14,
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
    "Todo": ParagraphStyle(
        "Todo", parent=base["BodyText"], fontName="Helvetica-Bold",
        fontSize=10, leading=14, textColor=WARN, spaceBefore=4, spaceAfter=4,
        backColor=colors.HexColor("#FFF6E0"), borderPadding=(6, 8, 6, 8),
        leftIndent=4, rightIndent=4,
    ),
    "Highlight": ParagraphStyle(
        "Highlight", parent=base["BodyText"], fontName="Helvetica",
        fontSize=10, leading=14, textColor=colors.black, alignment=TA_JUSTIFY,
        backColor=SOFT, borderPadding=(6, 8, 6, 8),
        leftIndent=4, rightIndent=4, spaceBefore=6, spaceAfter=6,
    ),
    "TOC": ParagraphStyle(
        "TOC", parent=base["Normal"], fontName="Helvetica",
        fontSize=10.5, leading=17, textColor=NAVY,
    ),
    "TOCsub": ParagraphStyle(
        "TOCsub", parent=base["Normal"], fontName="Helvetica",
        fontSize=10, leading=15, textColor=GRAY, leftIndent=18,
    ),
}


class HospitalDocTemplate(BaseDocTemplate):
    def __init__(self, filename: Path, **kwargs):
        super().__init__(
            str(filename),
            pagesize=A4,
            leftMargin=2.2 * cm,
            rightMargin=2.2 * cm,
            topMargin=2.0 * cm,
            bottomMargin=1.8 * cm,
            title="Hospital Project - Memoria Tecnica",
            author="Oriol Fontcuberta, Unai Canet, Albert Garrido",
        )
        frame = Frame(
            self.leftMargin, self.bottomMargin,
            self.width, self.height,
            id="content", showBoundary=0,
        )
        cover = PageTemplate(id="cover", frames=frame, onPage=self._cover_page)
        normal = PageTemplate(id="normal", frames=frame, onPage=self._normal_page)
        self.addPageTemplates([cover, normal])

    def _cover_page(self, canvas, doc):
        canvas.saveState()
        canvas.setFillColor(NAVY)
        canvas.rect(0, A4[1] - 1.5 * cm, A4[0], 1.5 * cm, fill=1, stroke=0)
        canvas.setFillColor(TEAL)
        canvas.rect(0, A4[1] - 1.7 * cm, A4[0], 0.2 * cm, fill=1, stroke=0)
        canvas.setFillColor(TEAL)
        canvas.rect(0, 0, A4[0], 0.9 * cm, fill=1, stroke=0)
        canvas.setFillColor(NAVY)
        canvas.rect(0, 0.9 * cm, A4[0], 0.2 * cm, fill=1, stroke=0)
        canvas.restoreState()

    def _normal_page(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(BLUE)
        canvas.setLineWidth(0.6)
        canvas.line(2 * cm, A4[1] - 1.3 * cm, A4[0] - 2 * cm, A4[1] - 1.3 * cm)
        canvas.setFont("Helvetica-Bold", 9)
        canvas.setFillColor(NAVY)
        canvas.drawString(2 * cm, A4[1] - 1.1 * cm, "Hospital Project")
        canvas.setFont("Helvetica", 8.5)
        canvas.setFillColor(GRAY)
        canvas.drawRightString(A4[0] - 2 * cm, A4[1] - 1.1 * cm,
                               "Memoria Tecnica  -  LaSalle Health Center")
        canvas.setStrokeColor(BLUE)
        canvas.setLineWidth(0.4)
        canvas.line(2 * cm, 1.4 * cm, A4[0] - 2 * cm, 1.4 * cm)
        canvas.setFont("Helvetica", 8.5)
        canvas.setFillColor(GRAY)
        canvas.drawString(2 * cm, 1.0 * cm,
                          "Oriol Fontcuberta  -  Unai Canet  -  Albert Garrido")
        canvas.drawRightString(A4[0] - 2 * cm, 1.0 * cm, f"Pagina {doc.page}")
        canvas.restoreState()


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


def highlight(text: str):
    return Paragraph(text, styles["Highlight"])


def build_cover() -> list:
    return [
        Spacer(1, 3.5 * cm),
        p("Sistema Inteligente de Soporte Hospitalario", "CoverTitle"),
        Spacer(1, 0.4 * cm),
        p("LaSalle Health Center", "CoverHospital"),
        Spacer(1, 1.6 * cm),
        p("MEMORIA TECNICA", "CoverSubtitle"),
        Spacer(1, 0.2 * cm),
        p("Plataforma containerizada de IA y Big Data<br/>para clasificacion radiologica y triaje clinico",
          "CoverMeta"),
        Spacer(1, 2.8 * cm),
        p("Equipo de desarrollo", "CoverMeta"),
        Spacer(1, 0.3 * cm),
        p("Oriol Fontcuberta", "CoverAuthors"),
        p("Unai Canet", "CoverAuthors"),
        p("Albert Garrido", "CoverAuthors"),
        Spacer(1, 2.0 * cm),
        p("Asignatura: Sistemes d'Aprenentatge Automatic / Big Data", "CoverMeta"),
        Spacer(1, 0.3 * cm),
        p(f"Fecha de entrega: {date.today().isoformat()}", "CoverMeta"),
        PageBreak(),
    ]


def build_toc() -> list:
    rows = [
        ("1.", "Resumen ejecutivo", False),
        ("2.", "Descripcion del problema", False),
        ("3.", "Datos", False),
        ("4.", "Arquitectura del sistema", False),
        ("5.", "Modelos de Inteligencia Artificial", False),
        ("6.", "Pipeline de Big Data", False),
        ("7.", "Backend (API REST)", False),
        ("8.", "Dashboard", False),
        ("9.", "Automatizaciones", False),
        ("10.", "Integraciones", False),
        ("11.", "Calidad, testing y CI/CD", False),
        ("12.", "Justificaciones tecnicas y alternativas", False),
        ("13.", "Diario de desarrollo con IA", False),
        ("14.", "Reflexion critica", False),
        ("15.", "Consideraciones eticas y legales", False),
        ("16.", "Conclusiones", False),
        ("A.", "Anexo: estructura del repositorio", True),
    ]
    rendered = [chapter(0, "Indice")]
    for num, title, is_annex in rows:
        style = "TOCsub" if is_annex else "TOC"
        rendered.append(Paragraph(f"<b>{num}</b> &nbsp; {title}", styles[style]))
    rendered.append(PageBreak())
    return rendered


def build_ch1_summary() -> list:
    out: list = [
        chapter(1, "Resumen ejecutivo"),
        section("1.1", "Vision general del sistema"),
        p(
            "Este documento describe la plataforma desarrollada para el hospital ficticio "
            "<b>LaSalle Health Center</b>, una solucion integral de soporte clinico que combina "
            "tecnicas de inteligencia artificial y big data en un entorno containerizado. "
            "El sistema cubre el ciclo completo: ingesta de imagenes radiologicas y datos "
            "tabulares, validacion de calidad, clasificacion automatica (radiografia y "
            "triaje), persistencia dual (PostgreSQL + MinIO), generacion de informes y "
            "visualizacion operativa a traves de un dashboard web con autenticacion."
        ),
        p(
            "La arquitectura se ha disenado siguiendo principios de separacion estricta de "
            "responsabilidades (Layered Architecture y Domain-Driven Design adaptados a "
            "Python), garantizando transaccionalidad ACID en todas las operaciones compuestas "
            "y exposicion de metricas operativas en formato JSON consumibles por el dashboard. "
            "El despliegue se realiza con <b>un unico comando</b> (<i>docker compose up -d</i>) "
            "y cubre nueve servicios containerizados coordinados a traves de una red Docker comun."
        ),
        section("1.2", "Tecnologias clave"),
        bullets([
            "<b>Backend</b>: FastAPI 0.11x con Pydantic, arquitectura en capas (api / services / repositories / db / storage).",
            "<b>Dashboard</b>: Flask con app factory, blueprints, autenticacion local con hashes Werkzeug y sesiones firmadas.",
            "<b>Base de datos relacional</b>: PostgreSQL 16.13 (alpine) con connection pool psycopg 2-10.",
            "<b>Almacenamiento de objetos</b>: MinIO compatible con S3 (boto3).",
            "<b>Procesamiento distribuido</b>: Apache Spark 3.5.8 con un master y un worker.",
            "<b>Modelos IA</b>: Random Forest calibrado (triaje) y ResNet18 (clasificacion radiologica).",
            "<b>Orquestacion</b>: Docker Compose con perfiles (<i>pipeline</i>, <i>training</i>, <i>triage-training</i>).",
            "<b>Tests y CI</b>: pytest con dobles que respetan contratos reales y GitHub Actions.",
        ]),
        PageBreak(),
    ]
    return out


def build_ch2_problem() -> list:
    out: list = [
        chapter(2, "Descripcion del problema"),
        section("2.1", "Contexto del hospital LaSalle Health Center"),
        p(
            "LaSalle Health Center es una organizacion sanitaria de tamano medio en proceso "
            "de transformacion digital. Genera diariamente grandes volumenes de datos "
            "clinicos y operativos (historias clinicas, registros de pacientes, pruebas "
            "diagnosticas, logs de sistemas) que hasta la fecha no se aprovechan "
            "sistematicamente para extraer conocimiento, detectar patrones ni automatizar "
            "tareas repetitivas."
        ),
        p(
            "La direccion del hospital ha contratado al equipo, en su rol de consultora "
            "tecnologica especializada en Inteligencia Artificial y Big Data, para disenar "
            "e implementar una plataforma que aporte valor real en un entorno sanitario, "
            "respetando las restricciones eticas, legales y operativas inherentes al sector."
        ),
        section("2.2", "Necesidades detectadas"),
        bullets([
            "Extraer conocimiento util de grandes volumenes de datos heterogeneos.",
            "Detectar patrones clinicos relevantes en imagenes medicas (radiografias de torax).",
            "Automatizar procesos internos: validacion de datos, generacion de informes, alertas.",
            "Apoyar la toma de decisiones medicas y operativas con metricas y resultados interpretables.",
            "Disponer de una infraestructura reproducible, desplegable con un unico comando y portable a cualquier maquina.",
        ]),
        section("2.3", "Objetivos del proyecto"),
        p("Los objetivos concretos planteados son los siguientes:"),
        bullets([
            "Implementar un sistema de <b>clasificacion triple de radiografias de torax</b> en las categorias <i>Sana</i>, <i>Neumonia</i> y <i>COVID-19</i>.",
            "Disponer de un mecanismo de <b>triaje clinico automatizado</b> que asigne nivel de riesgo y prioridad a partir de sintomas y signos vitales.",
            "Disenar un <b>pipeline Big Data</b> con Spark que ingiera, valide, transforme y registre lotes de estudios.",
            "Combinar dos tipos de almacenamiento: <b>PostgreSQL</b> para datos estructurados y <b>MinIO</b> para datos no estructurados (imagenes, informes JSON).",
            "Exponer una <b>API REST</b> tipada para consumo desde el dashboard y desde clientes externos.",
            "Ofrecer una <b>interfaz web</b> con autenticacion para personal sanitario.",
            "Implementar <b>automatizaciones</b>: generacion de informes, alertas ante eventos relevantes, deteccion de problemas de calidad.",
            "Garantizar <b>despliegue reproducible</b> mediante Docker Compose con un unico fichero de composicion.",
            "Documentar el proceso de forma profesional, incluyendo SDD, diario de IA y consideraciones eticas.",
        ]),
        section("2.4", "Alcance funcional"),
        p(
            "El proyecto es un <b>prototipo funcional end-to-end</b>. Cubre todos los "
            "componentes pedidos por el enunciado. La inferencia radiologica se sirve con "
            "el <b>modelo CNN ResNet18 ya entrenado</b> sobre un dataset publico de "
            "radiografias de torax con tres clases (Sana, Neumonia, COVID-19). El artefacto "
            "persistido es <i>models/radiology_cnn_resnet18.pt</i> y las metricas completas "
            "se encuentran en <i>models/radiology_cnn_metrics.json</i>."
        ),
        p(
            "El triaje clinico se entrega como modelo <b>Random Forest calibrado</b> ya "
            "entrenado y persistido en <i>models/triage_model.joblib</i>, con metricas "
            "documentadas en <i>models/triage_metrics.json</i>. El backend lo carga al "
            "arranque con fallback automatico a un sistema de reglas determinista si el "
            "artefacto no esta presente."
        ),
        PageBreak(),
    ]
    return out


def build_ch3_data() -> list:
    out: list = [
        chapter(3, "Datos"),
        section("3.1", "Fuentes de datos"),
        p(
            "<b>Imagenes radiograficas</b>: JPG/PNG, max 5 MB, validacion en dos niveles "
            "(extension + MIME + contenido Pillow). Para entrenamiento: "
            "<b>COVID-19 Radiography Database</b> (Kaggle) en "
            "<i>data/radiology_dataset/{train,val}/{Sana,Neumonia,COVID-19}/</i>.<br/>"
            "<b>CSV tabular (pipeline)</b>: <i>data/incoming/radiology_studies.csv</i> con "
            "columnas obligatorias <i>study_id, patient_age, patient_sex, image_object_key, "
            "label, acquisition_date, source</i>.<br/>"
            "<b>Dataset sintetico de triaje</b>: 8.000 muestras con 6 vitales + 10 sintomas "
            "binarios, etiquetadas segun reglas MEWS/NEWS2 con 6 % de ruido, split 80/20 "
            "estratificado."
        ),
        section("3.2", "Ingesta, limpieza y transformaciones"),
        bullets([
            "<b>Ingesta</b>: dashboard (imagen individual), API directa (<i>POST /predict</i>), pipeline Spark (lote CSV) y model-trainer (dataset de imagenes).",
            "<b>Imagenes</b>: extension JPG/JPEG/PNG, tamano &lt;= 5 MB, MIME real vs. declarado, rechazo de JPEG renombrado como PNG.",
            "<b>CSV</b>: columnas obligatorias, tipos, no nulos, etiquetas validas; duplicados por <i>image_object_key</i> rechazados; rechazados a informe del run.",
            "<b>Spark</b>: trim de strings, conversion de tipos, columnas derivadas.",
            "<b>Imagenes (CNN)</b>: resize 224x224, tensor RGB, normalizacion ImageNet (mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225]); augmentation en training: RandomHorizontalFlip + RandomRotation(8°).",
        ]),
        section("3.3", "Almacenamiento final"),
        table(
            ["Tipo de dato", "Almacenamiento", "Justificacion"],
            [
                ["Imagenes binarias", "MinIO (uploads/)", "API S3, no estructurado, gran tamano"],
                ["Informes radiografia", "MinIO (radiology-reports/)", "JSON inmutable, asociado a un estudio"],
                ["Informes triaje", "MinIO (triage-reports/)", "JSON, persistente, consultable"],
                ["Informes pipeline", "MinIO (pipeline-reports/)", "JSON con metricas por ejecucion"],
                ["Estudios radiologicos", "PostgreSQL", "Relacional, consultas operativas y agregados"],
                ["Triajes", "PostgreSQL", "Historial estructurado"],
                ["Eventos de calidad", "PostgreSQL", "Indexable, contadores por severidad"],
                ["Ejecuciones pipeline", "PostgreSQL", "Trazabilidad de runs Spark"],
                ["Datos tabulares procesados", "Filesystem (JSON)", "Salida intermedia del pipeline"],
            ],
            col_widths=[4.0 * cm, 4.5 * cm, 8.0 * cm],
        ),
        PageBreak(),
    ]
    return out


def build_ch4_architecture() -> list:
    out: list = [
        chapter(4, "Arquitectura del sistema"),
        section("4.1", "Vision general"),
        p(
            "El sistema sigue una arquitectura de <b>microservicios containerizados</b> "
            "coordinados por Docker Compose. Cada servicio tiene una responsabilidad unica "
            "y se comunica con el resto mediante protocolos estandar (HTTP, S3, PostgreSQL "
            "wire protocol, Spark RPC). Todos los servicios comparten una red Docker comun "
            "(<i>hospital_network</i>) que permite resolver nombres por DNS interno."
        ),
        code(
            "Browser  -->  Dashboard (Flask:8501)\n"
            "                 |\n"
            "                 |-->  Backend (FastAPI:8000)\n"
            "                 |        |\n"
            "                 |        |-->  PostgreSQL (db:5432)\n"
            "                 |        |-->  MinIO (minio:9000)\n"
            "                 |        '-->  Spark (spark:7077)\n"
            "                 |\n"
            "                 '-->  MinIO (uploads directos)\n"
            "\n"
            "Pipeline (Spark job, on-demand)\n"
            "  --> Lee CSV de /data/incoming\n"
            "  --> Escribe limpio en /data/processed\n"
            "  --> Registra ejecucion en PostgreSQL\n"
            "  --> Publica informe JSON en MinIO\n"
            "\n"
            "Model-trainer (entrenamiento CNN, on-demand)\n"
            "  --> Lee dataset de /data/radiology_dataset\n"
            "  --> Persiste artefacto en /models\n"
        ),
        section("4.2", "Infraestructura containerizada"),
        subsection("Servicios Docker Compose"),
        table(
            ["Servicio", "Imagen", "Puerto", "Responsabilidad"],
            [
                ["backend", "hospital-backend (Python 3.11)", "8000", "API REST, inferencia, persistencia"],
                ["dashboard", "hospital-dashboard (Python)", "8501", "UI web, autenticacion, subida"],
                ["db", "postgres:16.13-alpine", "5432", "Datos estructurados"],
                ["minio", "minio:RELEASE.2024-01-11", "9000 / 9001", "Almacenamiento de objetos"],
                ["spark", "spark:3.5.8-python3", "interno", "Master Spark"],
                ["spark-worker", "spark:3.5.8-python3", "interno", "Worker Spark (2 cores / 1 GB)"],
                ["pipeline", "hospital-pipeline", "perfil pipeline", "Job Spark de ingesta y calidad"],
                ["model-trainer", "hospital-model-trainer", "perfil training", "Entrenamiento CNN"],
                ["triage-trainer", "hospital-triage-trainer", "perfil triage-training", "Entrenamiento RF triaje"],
            ],
            col_widths=[3.0 * cm, 4.4 * cm, 3.0 * cm, 6.1 * cm],
        ),
        subsection("Red Docker"),
        p(
            "Todos los servicios viven en la red <i>hospital_network</i> con driver bridge. "
            "Esto permite que el backend referencie PostgreSQL como <i>db:5432</i>, MinIO "
            "como <i>minio:9000</i> y Spark como <i>spark://spark:7077</i> sin necesidad de "
            "exponer puertos al host. Los puertos publicados (backend, dashboard, MinIO, db) "
            "se enlazan a <i>127.0.0.1</i> para evitar exposicion en la red local."
        ),
        subsection("Volumenes persistentes"),
        bullets([
            "<b>postgres_data</b>: persistencia de las tablas relacionales.",
            "<b>minio_data</b>: persistencia de los buckets de objetos.",
            "<b>./data</b> (bind mount): datos de ingesta y procesados compartidos entre pipeline y model-trainer.",
            "<b>./models</b> (bind mount, read-only en backend): artefactos de modelos compartidos.",
        ]),
        subsection("Perfiles de despliegue"),
        p(
            "Docker Compose soporta perfiles para encender servicios opcionales sin "
            "interferir con el arranque por defecto. Esto separa cargas pesadas del flujo "
            "habitual:"
        ),
        bullets([
            "<b>Sin perfil</b>: backend, dashboard, db, minio, spark, spark-worker.",
            "<b>--profile pipeline</b>: lanza el job Spark de ingesta.",
            "<b>--profile training</b>: entrena el modelo CNN ResNet18 sobre el dataset radiografico.",
            "<b>--profile triage-training</b>: entrena el Random Forest de triaje.",
        ]),
        PageBreak(),
    ]
    return out


def build_ch5_models() -> list:
    out: list = [
        chapter(5, "Modelos de Inteligencia Artificial"),
        section("5.1", "Modelo de triaje (Random Forest calibrado)"),
        p(
            "El triaje opera sobre ~17 variables (6 vitales continuas + 10 sintomas binarios). "
            "Se ha elegido un <b>Random Forest con 400 arboles</b> (max_depth=12) con "
            "<b>calibracion isotonica</b> (CalibratedClassifierCV): ofrece feature importances "
            "interpretables clinicamente, entrena en CPU en ~16 s y sus probabilidades son "
            "fiables tras la calibracion. Dataset sintetico de 8.000 muestras generado con "
            "reglas MEWS/NEWS2, 6 % de ruido de etiquetado y split 80/20 estratificado."
        ),
        table(
            ["Metrica", "low", "medium", "high", "critical", "Macro"],
            [
                ["Precision", "0.83", "0.74", "0.69", "0.97", "0.81"],
                ["Recall", "0.79", "0.84", "0.58", "0.92", "0.78"],
                ["F1-score", "0.81", "0.79", "0.63", "0.94", "0.79"],
                ["Soporte", "363", "583", "258", "396", "1.600"],
            ],
            col_widths=[3.0 * cm, 2.4 * cm, 2.4 * cm, 2.4 * cm, 2.4 * cm, 2.4 * cm],
        ),
        p(
            "La <b>accuracy global es 80.6 %</b> sobre 1.600 muestras de test. La clase "
            "<i>critical</i> alcanza una precision de 0.97 y un recall de 0.92, que es "
            "exactamente lo deseable clinicamente: minimizar falsos negativos en los casos "
            "mas graves. La clase <i>high</i> es la mas dificil (recall 0.58), debido a "
            "que se solapa con <i>medium</i> en la frontera; este punto se documenta como "
            "limitacion en la seccion 14."
        ),
        section("5.2", "Modelo CNN ResNet18 (clasificacion triple de radiografias)"),
        p(
            "<b>ResNet18</b> (11.7 M parametros, CUDA) entrenado desde cero, 5 epochs, "
            "batch 16, lr=5e-4, AdamW, CrossEntropyLoss con class weights inversos a la "
            "frecuencia de clase (COVID-19=3.73 &gt; Sana=1.35 &gt; Neumonia=0.50) para "
            "compensar el fuerte desbalance del dataset (6.432 imagenes: 576 COVID-19, "
            "1.583 Sanas, 4.273 Neumonia). Preprocesado: resize 224x224, normalizacion "
            "ImageNet, augmentation RandomHorizontalFlip + RandomRotation(8 grados)."
        ),
        p("<b>Resultados sobre test (conjunto de generalizacion): accuracy 93.94 %</b>"),
        table(
            ["Clase", "Precision", "Recall", "F1-score", "Soporte"],
            [
                ["COVID-19", "<b>0.958</b>", "<b>0.983</b>", "<b>0.970</b>", "116"],
                ["Sana", "0.864", "0.905", "0.884", "317"],
                ["Neumonia", "0.967", "0.946", "0.956", "855"],
                ["<b>Macro avg</b>", "<b>0.930</b>", "<b>0.945</b>", "<b>0.937</b>", "1.288"],
                ["<b>Weighted avg</b>", "<b>0.941</b>", "<b>0.939</b>", "<b>0.940</b>", "1.288"],
            ],
            col_widths=[3.5 * cm, 3.0 * cm, 3.0 * cm, 3.0 * cm, 4.0 * cm],
        ),
        subsection("Matriz de confusion sobre test"),
        table(
            ["Real / Predicho", "COVID-19", "Sana", "Neumonia"],
            [
                ["<b>COVID-19</b>", "<b>114</b>", "2", "0"],
                ["<b>Sana</b>", "2", "<b>287</b>", "28"],
                ["<b>Neumonia</b>", "3", "43", "<b>809</b>"],
            ],
            col_widths=[4.5 * cm, 4.0 * cm, 4.0 * cm, 4.0 * cm],
        ),
        highlight(
            "<b>Lectura clinica clave</b>: en el conjunto de test, el modelo detecta "
            "correctamente <b>114 de 116 casos de COVID-19</b> (recall 0.983). Los 2 falsos "
            "negativos se clasifican como <i>Sana</i>, pero <b>ninguno como Neumonia</b>: "
            "el modelo no confunde COVID con neumonia comun, que es exactamente la "
            "propiedad mas valiosa clinicamente para evitar aislamientos tardios."
        ),
        section("5.3", "Servicio de inferencia y heuristica de respaldo del triaje"),
        p(
            "El backend incorpora dos estrategias de servicio segun el modelo: para "
            "radiologia, <i>InferenceService</i> carga el checkpoint ResNet18 al arrancar "
            "y exige su presencia (sin <i>.pt</i>, el contenedor falla rapido para evitar "
            "predicciones falsas con cualquier sustituto improvisado). Para triaje, "
            "<i>triage_model</i> sigue un patron singleton con <i>threading.Lock</i> que "
            "carga <i>triage_model.joblib</i> bajo demanda en la primera prediccion."
        ),
        p(
            "El servicio de triaje ademas conserva una <b>heuristica de reglas</b> "
            "(<i>_baseline</i> en <i>triage_service.py</i>) que se activa unicamente "
            "cuando el Random Forest no esta disponible (artefacto ausente, version "
            "incompatible o error de carga). Esta heuristica calcula un score basado en "
            "frecuencia cardiaca, saturacion, presion sistolica y sintomas dominantes "
            "(dolor toracico, disnea, perdida de consciencia) y lo mapea a uno de los "
            "cuatro niveles de riesgo. Su rol es estrictamente de <b>safety net</b>: en "
            "operacion normal el flujo invoca siempre al modelo entrenado."
        ),
        highlight(
            "<b>Tres modelos coexisten en el sistema</b>: (1) ResNet18 para radiografia, "
            "(2) Random Forest calibrado para triaje y (3) heuristica de reglas como "
            "fallback unicamente del triaje. En produccion normal corren los dos modelos "
            "entrenados; la heuristica queda como salvaguarda y se identifica en las "
            "respuestas con el <i>model_name</i> <i>hospital-triage-rules-fallback</i>."
        ),
        section("5.4", "Analisis clinico (el porque)"),
        p(
            "<b>Lectura clinica del triaje</b>: los errores se concentran en confusiones "
            "entre niveles adyacentes (low↔medium, medium↔high). Confusiones saltando dos "
            "niveles son raras (2 casos de <i>low</i> como <i>high</i>, 0 como "
            "<i>critical</i>): el modelo nunca clasifica un critico como trivial."
        ),
        subsection("Impacto de falsos negativos"),
        bullets([
            "<b>Falso negativo critical</b>: un paciente critico clasificado como menor riesgo es el peor escenario. En el test: 0 casos de critical clasificados como low, 2 como medium. <b>Recall critical = 0.92</b>.",
            "<b>Falso negativo high</b>: 96 casos de high clasificados como medium o low (recall 0.58). Clinicamente, esto exige un proceso de revision humana para todos los casos <i>medium</i> con flags clinicas.",
            "<b>Falso negativo COVID-19 (CNN)</b>: con recall 0.983 sobre test, el CNN solo erra 2 de 116 COVID, y ambos como <i>Sana</i> (ninguno como Neumonia). Toda prediccion COVID-19 dispara automaticamente un evento de severidad alta en <i>quality_events</i>.",
        ]),
        subsection("Limitaciones tecnicas reales"),
        bullets([
            "El triaje opera con seis variables vitales y diez sintomas; no contempla historia clinica, comorbilidades o resultados analiticos.",
            "El dataset de triaje es sintetico; un despliegue real requeriria reentrenamiento con datos hospitalarios.",
            "El CNN se ha entrenado solo 5 epochs sobre 4.115 imagenes; un despliegue clinico requeriria mas datos, validacion externa y revision por radiologos.",
            "El sistema asume tres clases radiologicas; cualquier patologia distinta sera clasificada incorrectamente.",
        ]),
        PageBreak(),
    ]
    return out


def build_ch6_pipeline() -> list:
    out: list = [
        chapter(6, "Pipeline de Big Data"),
        section("6.1", "Justificacion de Apache Spark"),
        p(
            "Se ha elegido <b>Apache Spark 3.5.8</b> con PySpark como motor de procesamiento "
            "distribuido. Las razones se documentan en detalle en el capitulo 12, pero "
            "resumidamente: Spark es el estandar de facto en entornos hospitalarios y de "
            "investigacion biomedica, ofrece API SQL madura, soporta escalado horizontal "
            "transparente y se integra de forma trivial con almacenamientos compatibles con "
            "S3 (como MinIO)."
        ),
        section("6.2", "Modulos del pipeline"),
        p(
            "El job <i>radiology_pipeline.py</i> cubre cuatro fases (ingesta → validacion → "
            "transformacion → escritura) mediante submodulos especializados:"
        ),
        table(
            ["Modulo", "Archivo", "Responsabilidad"],
            [
                ["validators", "csv_schema.py", "Schema obligatorio, validacion de etiquetas y nulos"],
                ["transforms", "quality_filter.py", "Filtrado de registros invalidos, deteccion duplicados"],
                ["writers", "postgres_writer.py", "Inserciones idempotentes en PostgreSQL"],
                ["writers", "minio_writer.py", "Subida de informes JSON a MinIO"],
                ["reports", "run_report.py", "Construccion del informe por ejecucion"],
                ["core", "spark_factory.py", "Factory de SparkSession con configuracion homogenea"],
                ["core", "config.py", "Carga tipada de variables de entorno"],
                ["core", "logging.py", "Configuracion JSON estructurada para logs"],
            ],
            col_widths=[2.8 * cm, 4.0 * cm, 9.7 * cm],
        ),
        section("6.4", "Persistencia de ejecuciones y reportes"),
        p(
            "Cada ejecucion del pipeline genera:"
        ),
        bullets([
            "Una fila en la tabla <b>pipeline_runs</b> con timestamp, parametros, status y duracion.",
            "Un informe JSON en MinIO bajo <b>pipeline-reports/&lt;run_id&gt;.json</b> con: distribucion de clases en registros aceptados, muestra de hasta 25 registros rechazados, lista de claves duplicadas y resumen estadistico.",
            "Eventos en <b>quality_events</b> si hay rechazos (severidad <i>medium</i>) o si el job falla (severidad <i>high</i>).",
            "Logs estructurados JSON visibles via <i>docker compose logs pipeline</i>.",
        ]),
        p(
            "El dashboard consulta el endpoint <i>GET /metrics</i> del backend para mostrar "
            "el estado de la ultima ejecucion (timestamp, status, contadores de procesados, "
            "rechazados y duplicados). Esto cierra el bucle de visibilidad operativa."
        ),
        PageBreak(),
    ]
    return out


def build_ch7_backend() -> list:
    out: list = [
        chapter(7, "Backend (API REST)"),
        section("7.1", "Estructura modular"),
        p(
            "El backend FastAPI sigue una <b>arquitectura en capas</b>: "
            "<i>api</i> (routers, deps, errors) → <i>services</i> (logica de negocio) → "
            "<i>repositories</i> (psycopg) → <i>db</i> (pool, transaccion) / <i>storage</i> (boto3). "
            "Cada capa solo importa la inmediatamente inferior. La inyeccion de dependencias "
            "usa <i>lru_cache</i> en <i>deps.py</i>; las transacciones ACID se gestionan con "
            "un context manager Unit of Work que comparte cursor entre repositorios."
        ),
        section("7.2", "Endpoints expuestos"),
        table(
            ["Metodo y ruta", "Proposito"],
            [
                ["GET /health", "Healthcheck de dependencias"],
                ["POST /triage", "Evaluar triaje a partir de sintomas y vitales"],
                ["GET /triage/history", "Listar historial de triajes"],
                ["GET /triage/{id}", "Detalle de un triaje"],
                ["GET /triage/{id}/report", "Informe JSON del triaje en MinIO"],
                ["POST /predict", "Clasificar radiografia"],
                ["GET /studies/history", "Listar historial de estudios radiologicos"],
                ["GET /studies/{id}", "Detalle de un estudio"],
                ["GET /studies/{id}/report", "Informe JSON del estudio"],
                ["GET /quality/events", "Listar eventos de calidad"],
                ["PATCH /quality/events/{id}/resolve", "Marcar evento como resuelto"],
                ["GET /metrics", "Snapshot agregado en JSON consumido por el dashboard"],
            ],
            col_widths=[6.5 * cm, 10.0 * cm],
        ),
        PageBreak(),
    ]
    return out


def build_ch8_dashboard() -> list:
    out: list = [
        chapter(8, "Dashboard"),
        p(
            "Flask con patron <b>app factory</b> y <b>blueprints</b> (auth, main). "
            "Autenticacion con hashes PBKDF2-SHA256 (Werkzeug, 1M iteraciones), cookie "
            "firmada con SECRET_KEY, HttpOnly, SameSite=Lax. Dos roles: <i>admin</i> "
            "(todas las vistas + consola MinIO) e <i>user</i> (radiologia y triaje)."
        ),
        table(
            ["Ruta", "Funcion"],
            [
                ["GET / POST /upload", "Subida de radiografia y resultado CNN"],
                ["GET / POST /triage", "Formulario de triaje y resultado RF"],
                ["GET /history", "Historial de estudios y triajes"],
                ["GET /events", "Eventos de calidad abiertos por severidad"],
                ["GET /storage (admin)", "Consola MinIO embebida"],
            ],
            col_widths=[5.5 * cm, 11.0 * cm],
        ),
        bullets([
            "<b>Resultado CNN</b>: imagen en base64, probabilidades por clase, banderas de calidad y enlace al informe JSON.",
            "<b>Estado del sistema</b>: consume <i>GET /metrics</i> del backend y muestra estado del modelo de triaje, pipeline y bucket.",
            "<b>Subida directa a MinIO</b>: imagen subida via boto3 antes de llamar al backend, evitando duplicar trafico.",
        ]),
        PageBreak(),
    ]
    return out


def build_ch9_automation() -> list:
    out: list = [
        chapter(9, "Automatizaciones"),
        p(
            "El sistema implementa cinco automatizaciones sin intervencion manual: "
            "creacion de bucket MinIO al primer arranque (<i>ensure_bucket</i>), "
            "generacion de informes JSON por prediccion/triaje/pipeline, "
            "emision de eventos de calidad en la misma transaccion ACID, "
            "procesamiento batch Spark on-demand y healthchecks con reinicios automaticos."
        ),
        subsection("Eventos de calidad automaticos"),
        table(
            ["Trigger", "Severidad", "Origen"],
            [
                ["Prediccion COVID-19", "high", "Backend, en /predict"],
                ["Confianza inferior a 0.55", "medium", "Backend, en /predict"],
                ["Banderas de calidad de imagen", "medium", "Backend, en /predict"],
                ["Registros rechazados por pipeline", "medium", "Pipeline Spark"],
                ["Pipeline failure", "high", "Pipeline Spark"],
                ["Triaje critico", "high", "Backend, en /triage"],
            ],
            col_widths=[5.5 * cm, 2.5 * cm, 8.5 * cm],
        ),
        subsection("Healthchecks y reinicios"),
        bullets([
            "<b>restart: always</b> en backend, dashboard, db, minio, spark, spark-worker; <b>restart: no</b> en pipeline y trainers (jobs batch).",
            "<b>Backend</b>: urllib contra <i>/health</i> cada 10 s. <b>PostgreSQL</b>: <i>pg_isready</i> cada 10 s. <b>MinIO</b>: <i>mc ready local</i> cada 10 s.",
            "<b>depends_on + condition: service_healthy</b>: el backend no arranca hasta que db y minio esten sanos.",
        ]),
        PageBreak(),
    ]
    return out


def build_ch10_integrations() -> list:
    out: list = [
        chapter(10, "Integraciones"),
        section("10.1", "Conexiones entre modulos"),
        table(
            ["Origen", "Destino", "Protocolo", "Proposito"],
            [
                ["dashboard", "backend", "HTTP / REST", "Solicitar prediccion / triaje, leer metricas"],
                ["dashboard", "minio", "S3 (boto3)", "Subida directa de imagenes"],
                ["backend", "db", "psycopg / pool 2-10", "Persistir estudios, triajes, eventos"],
                ["backend", "minio", "S3 (boto3)", "Subir informes JSON"],
                ["backend", "modelo (joblib)", "filesystem (read-only)", "Cargar Random Forest de triaje"],
                ["pipeline", "spark", "Spark RPC", "Ejecutar el job distribuido"],
                ["pipeline", "db", "psycopg", "Registrar ejecuciones y eventos"],
                ["pipeline", "minio", "S3 (boto3)", "Publicar informes de ejecucion"],
            ],
            col_widths=[2.8 * cm, 2.8 * cm, 3.4 * cm, 7.5 * cm],
        ),
        PageBreak(),
    ]
    return out


def build_ch11_quality() -> list:
    out: list = [
        chapter(11, "Calidad, testing y CI/CD"),
        section("11.1", "Cobertura de tests"),
        table(
            ["Componente", "Archivos de test", "Tipo"],
            [
                ["Backend - unit", "12 archivos", "Services, config, validacion, logging"],
                ["Backend - api", "6 archivos", "FastAPI TestClient con dependency_overrides"],
                ["Dashboard - unit", "4 archivos", "Servicios, validacion, presenters, auth"],
                ["Dashboard - web", "2 archivos", "Flask test client con blueprints"],
                ["Total", "24 archivos de test", "Cubriendo logica de negocio"],
            ],
            col_widths=[4.5 * cm, 4.5 * cm, 7.5 * cm],
        ),
        p(
            "Estrategia: <b>dobles que respetan los contratos reales</b> (no MagicMock); "
            "tests de API con <i>dependency_overrides</i>. Cobertura &gt; 90 % en logica "
            "de negocio del backend."
        ),
        section("11.2", "Calidad de datos, logging y CI"),
        bullets([
            "<b>Cliente</b>: JavaScript verifica extension y tamano antes de la subida.",
            "<b>Servidor (FastAPI)</b>: Pillow comprueba el contenido binario real, no solo el MIME.",
            "<b>Pipeline (Spark)</b>: schema, duplicados por <i>image_object_key</i>, etiquetas validas, no nulos en campos clave.",
            "<b>Eventos automaticos</b>: cada rechazo genera entrada en <i>quality_events</i>; vista <i>/events</i> en dashboard.",
            "<b>Logs JSON estructurados</b>: timestamp ISO 8601, level, servicio, request_id / study_id en backend, dashboard y pipeline.",
            "<b>CI GitHub Actions</b>: <i>pytest --cov</i> + <i>docker compose config</i> en cada push/PR; falla rapido.",
        ]),
        PageBreak(),
    ]
    return out


def build_ch12_justification() -> list:
    out: list = [
        chapter(12, "Justificaciones tecnicas y alternativas"),
        p(
            "Las decisiones de stack priorizan reproducibilidad, interpretabilidad clinica "
            "y alineacion con estandares del sector."
        ),
        table(
            ["Decision", "Alternativas evaluadas", "Motivo principal"],
            [
                ["PostgreSQL + MinIO",
                 "MySQL, MongoDB, SQLite, GridFS, S3",
                 "ACID garantizado + JSONB; API S3 estandar (migracion trivial a AWS S3 real)"],
                ["Apache Spark 3.5.8",
                 "Dask, Apache Beam, pandas batch",
                 "Estandar hospitalario; SQL maduro; escalado horizontal preparado para produccion"],
                ["Random Forest + calibracion isotonica",
                 "XGBoost, LightGBM, MLP, reglas puras",
                 "Feature importances interpretables clinicamente; calibracion corrige sesgo de probabilidades en RF"],
                ["ResNet18 + transfer learning",
                 "CNN propia, ResNet50, EfficientNet, ViT",
                 "Balance capacidad/latencia (&lt; 50 ms CPU); backbone estandar en literatura clinica"],
                ["FastAPI (backend)",
                 "Flask, Django REST, Litestar",
                 "Tipado Pydantic, OpenAPI automatico, soporte asincrono nativo"],
                ["Flask + Jinja (dashboard)",
                 "Streamlit, Dash, SPA React/Vue",
                 "Flujos transaccionales con auth; Streamlit no permite personalizacion medica suficiente"],
                ["Docker Compose",
                 "Kubernetes, Nomad, podman-compose",
                 "Un solo comando de despliegue; enunciado lo exige explicitamente"],
            ],
            col_widths=[3.3 * cm, 4.7 * cm, 8.5 * cm],
        ),
        bullets([
            "<b>SQLAlchemy ORM descartado</b>: psycopg directo + repositorios es mas predecible para consultas analiticas.",
            "<b>Conexion por request descartada</b>: psycopg_pool evita el coste de handshake en cada peticion.",
            "<b>Scheduler diferido</b>: pipeline on-demand; migracion a Airflow/Prefect documentada en capitulo 14.",
        ]),
        PageBreak(),
    ]
    return out


def build_ch13_diario() -> list:
    out: list = [
        chapter(13, "Diario de desarrollo con IA"),
        section("13.1", "Herramientas utilizadas y justificacion"),
        p(
            "El proyecto se ha desarrollado utilizando de forma combinada varias "
            "herramientas de IA generativa, cada una con un proposito definido:"
        ),
        bullets([
            "<b>Claude Code</b> (Anthropic, Claude Opus 4.7): utilizado por el equipo para refactor de modulos, generacion de tests, redaccion de documentacion tecnica y revision de coherencia entre componentes. Capacidad de edicion directa de archivos y ejecucion de comandos shell para validacion en tiempo real.",
            "<b>Codex de OpenAI</b>: utilizado en fases iniciales para generar el esqueleto del backend, dashboard y docker-compose. Documentado en commits anteriores a la rama actual.",
            "<b>ChatGPT (GPT-4)</b>: consultado puntualmente para resolver dudas conceptuales (calibracion isotonica, eleccion de buckets de histograma, patrones de Spark).",
        ]),
        section("13.2", "Ejemplos representativos de prompts"),
        p(
            "A continuacion se presentan cuatro prompts representativos del proceso de "
            "desarrollo, organizados por fase."
        ),
        subsection("Prompt 1 — Auditoria inicial del repositorio"),
        code(
            "Herramienta: Claude Code  |  Fase: Auditoria inicial\n\n"
            "Prompt: Revisa que todo lo del enunciado se cumple. Analiza el\n"
            "  repositorio completo y dame un informe de que falta y que esta mal."
        ),
        bullets([
            "<b>Resultado</b>: backend monolito en un solo archivo, sin tests, clasificador radiologico como baseline estadistico, sin pipeline Spark funcional ni documentacion.",
            "<b>Aprendizaje</b>: dar a la IA el enunciado junto con el repositorio detecta la brecha mejor que una revision manual rapida.",
        ]),
        subsection("Prompt 2 — Modularizacion del backend"),
        code(
            "Herramienta: Claude Code  |  Fase: Refactor arquitectonico\n\n"
            "Prompt: El backend esta en un solo archivo. Refactorizalo siguiendo\n"
            "  arquitectura en capas: api / services / repositories / db / storage.\n"
            "  Cada capa solo puede importar la inmediatamente inferior.\n"
            "  No rompas los tests que ya existen."
        ),
        bullets([
            "<b>Resultado</b>: la IA propuso estructura de directorios, contratos de cada capa, patron Unit of Work espontaneo (no estaba en el prompt) e inyeccion de dependencias via <i>lru_cache</i>.",
            "<b>Aprendizaje</b>: especificar restricciones de importacion obliga a razonar sobre dependencias y genera arquitecturas mas limpias.",
        ]),
        subsection("Prompt 3 — Generacion de la suite de tests"),
        code(
            "Herramienta: Claude Code  |  Fase: Testing\n\n"
            "Prompt: Crea tests para el backend. No uses MagicMock generico: cada\n"
            "  doble debe implementar la misma interfaz que la clase real. Los tests\n"
            "  de API deben usar dependency_overrides de FastAPI, no parchear imports."
        ),
        bullets([
            "<b>Resultado</b>: 18 archivos de test (12 unit + 6 api) con fakes que implementan contratos reales. Tres tests fallaron en la primera ejecucion por asunciones incorrectas.",
            "<b>Aprendizaje</b>: la restriccion 'no MagicMock' es imprescindible; sin ella la IA genera tests que pasan con cualquier implementacion, incluyendo las rotas.",
        ]),
        subsection("Prompt 4 — Eliminacion de componentes no utilizados"),
        code(
            "Herramienta: Claude Code  |  Fase: Limpieza de infraestructura\n\n"
            "Prompt: Quita Prometheus y Grafana del proyecto. Desinstalalos, quita\n"
            "  el codigo y asegurate de no romper nada por el camino."
        ),
        bullets([
            "<b>Resultado</b>: la IA mapeo 12 archivos afectados, elimino contadores de tres servicios, borro el router prometheus.py, limpio docker-compose.yml, paro contenedores huerfanos y valido con <i>docker compose config</i>.",
            "<b>Aprendizaje</b>: para tareas de eliminacion es mas seguro mapear dependencias antes de borrar; un borrado manual habria dejado imports rotos.",
        ]),
        section("13.3", "Aciertos, correcciones e impacto"),
        bullets([
            "<b>Aciertos</b>: auditoria inicial precisa; Unit of Work espontaneo; singleton thread-safe del RF; dobles de tests con contratos reales; coherencia estilistica entre modulos.",
            "<b>Correcciones necesarias</b>: tres tests fallaron en primera ejecucion (asunciones incorrectas); sobre-ingenieria rechazada en varias propuestas; schema <i>PlatformMetrics</i> sin bloque <i>services.triage_model</i> (detectado al ver el fallback en dashboard).",
            "<b>Tareas en ambito humano</b>: arquitectura global, thresholds clinicos (confianza 0.55, alertas COVID-19), eleccion de stack.",
            "<b>Impacto en productividad</b>: consolidacion estimada en 5-7 horas efectivas vs. 4-6 dias-persona manualeses (factor ~6-10x). Principal valor: coherencia estilistica uniforme entre backend, dashboard y pipeline.",
        ]),
        PageBreak(),
    ]
    return out


def build_ch14_reflection() -> list:
    out: list = [
        chapter(14, "Reflexion critica"),
        section("14.1", "Limitaciones del sistema actual"),
        bullets([
            "<b>CNN con dataset publico (5 epochs)</b>: accuracy 93.94 % sobre test, pero no constituye modelo validado clinicamente; requiere datos hospitalarios reales.",
            "<b>Dataset radiografico no incluido</b>: se requiere descarga externa (COVID-19 Radiography Database u otro) para reentrenar.",
            "<b>Triaje sintetico</b>: entrenado con datos generados por reglas MEWS/NEWS2; despliegue real exige reentrenamiento con datos anonimizados hospitalarios.",
            "<b>Sin HTTPS ni cifrado en reposo</b>: HTTP plano; PostgreSQL y MinIO sin encriptacion de disco/objetos.",
            "<b>Sin scheduler ni HA</b>: pipeline on-demand, una sola instancia de cada servicio, sin failover.",
        ]),
        section("14.2", "Posibles mejoras"),
        bullets([
            "<b>Reentrenar CNN</b>: mas epochs, scheduling de lr, mixup/cutmix y validacion cruzada.",
            "<b>SSO corporativo</b>: OAuth2 / OIDC con Keycloak o proveedor cloud.",
            "<b>Cifrado SSE-S3 en MinIO</b> con KMS; disco cifrado (LUKS) para PostgreSQL.",
            "<b>Scheduler de pipeline</b>: Airflow o Prefect para ingesta automatica ante nuevos ficheros.",
            "<b>Observabilidad externa</b>: stack Prometheus + Grafana o OpenTelemetry sobre el endpoint <i>/metrics</i> ya disponible.",
            "<b>Mejora clase <i>high</i> del triaje</b>: recall 0.58; reentrenamiento con datos reales y ajuste de thresholds MEWS/NEWS2.",
        ]),
        section("14.3", "Viabilidad en produccion real"),
        bullets([
            "<b>Validacion clinica CNN</b> por equipo medico con dataset representativo del hospital.",
            "<b>Certificacion MDR</b>: clasificacion CE bajo Reglamento (UE) 2017/745, probablemente clase IIa.",
            "<b>Auditoria GDPR</b> y normativa espanola de proteccion de datos sanitarios.",
            "<b>Plan de incidentes</b>: notificacion a la AEPD en menos de 72 horas ante cualquier brecha.",
            "<b>Formacion del personal</b>: el sistema es herramienta de apoyo, no sustituto del criterio clinico.",
        ]),
        PageBreak(),
    ]
    return out


def build_ch15_ethics() -> list:
    out: list = [
        chapter(15, "Consideraciones eticas y legales"),
        section("15.1", "Sesgos en datos y modelos"),
        p(
            "Los modelos de imagen medica son vulnerables a sesgos cuando el dataset "
            "no representa la diversidad clinica real. Riesgos identificados: sesgo de "
            "procedencia (un solo hospital), sesgo demografico, sesgo de equipo radiologico "
            "(el modelo aprende la marca del scanner, no la patologia), sesgo temporal y "
            "sesgo de etiquetado (un solo radiologo sin doble lectura)."
        ),
        bullets([
            "<b>Particion por paciente</b>: separar train/val/test por paciente para evitar fuga entre conjuntos.",
            "<b>Metricas estratificadas</b>: precision/recall/F1 por subgrupo demografico; reportar la peor como referencia.",
            "<b>Monitorizacion continua</b>: revisiones periodicas del rendimiento en produccion con muestras representativas.",
        ]),
        section("15.2", "Riesgos en la decision automatizada"),
        p(
            "El sistema <b>no esta autorizado a tomar decisiones clinicas autonomas</b>. "
            "La responsabilidad final recae siempre en el personal sanitario."
        ),
        bullets([
            "<b>Falso negativo COVID-19</b>: retraso en aislamiento; mitigado con recall 0.983 y alerta automatica de severidad alta.",
            "<b>Falso negativo triaje critico</b>: mitigado con recall 0.92 en clase <i>critical</i> y revision humana obligatoria.",
            "<b>Automation bias</b>: cada prediccion incluye nota explicita '<i>resultado de apoyo, no diagnostico</i>'.",
            "<b>Baja confianza</b>: predicciones con confianza &lt; 0.55 generan evento automatico de revision.",
        ]),
        section("15.3", "Privacidad (RGPD) y limitaciones legales"),
        p(
            "Las imagenes y datos clinicos son <b>categorias especiales de datos personales</b> "
            "(Art. 9 RGPD). Este prototipo debe usarse <b>exclusivamente con datos "
            "anonimizados, sinteticos o simulados</b>. Carencias actuales: sin cifrado en "
            "reposo, sin auditoria de accesos individuales, sin gestion de consentimientos, "
            "sin derecho al olvido automatizado. En un entorno real seria obligatorio: RBAC, "
            "TLS en todos los flujos, cifrado SSE-S3/KMS, auditoria exportable, politica de "
            "retencion y acuerdo de tratamiento con proveedores cloud."
        ),
        p(
            "El CNN ResNet18 (accuracy 93.94 % sobre test publico) no constituye un modelo "
            "validado clinicamente: requiere validacion externa, evaluacion medica formal y "
            "certificacion MDR (Reglamento (UE) 2017/745, probablemente clase IIa) antes de "
            "cualquier uso real. El triaje con dataset sintetico exige reentrenamiento con "
            "datos hospitalarios y validacion frente a protocolos MEWS/NEWS2 vigentes."
        ),
        PageBreak(),
    ]
    return out


def build_ch16_conclusions() -> list:
    out: list = [
        chapter(16, "Conclusiones"),
        p(
            "El proyecto ha cumplido los objetivos planteados en el enunciado: una "
            "plataforma integral de soporte hospitalario que combina IA y Big Data, "
            "desplegable con un unico comando, con dos modelos de IA operativos, pipeline "
            "Spark de procesamiento por lotes, almacenamiento dual estructurado y no "
            "estructurado, dashboard con autenticacion, automatizaciones de alertas y "
            "calidad, y documentacion profesional acompanada de tests automatizados."
        ),
        section("16.1", "Valor aportado"),
        p(
            "Mas alla del cumplimiento estricto del enunciado, el proyecto aporta valor en "
            "tres dimensiones:"
        ),
        bullets([
            "<b>Calidad de ingenieria</b>: arquitectura en capas con separacion estricta, transaccionalidad ACID, dobles de tests que respetan contratos, configuracion tipada fail-fast, logging estructurado.",
            "<b>Reproducibilidad</b>: cualquier persona puede levantar el sistema con <i>docker compose up -d</i> y reproducir el flujo end-to-end sin friccion. Los modelos se entrenan en perfiles dedicados.",
            "<b>Honestidad tecnica</b>: el sistema documenta abiertamente sus limitaciones (CNN entrenado solo 5 epochs sobre dataset publico, dataset sintetico de triaje, ausencia de cifrado, ausencia de SSO) y reconoce que es un prototipo no apto para uso clinico real sin trabajo adicional.",
        ]),
        section("16.3", "Cierre"),
        p(
            "El sistema demuestra que es posible disenar e implementar una plataforma "
            "hospitalaria realista en un entorno academico, equilibrando el alcance "
            "tecnico con las consideraciones eticas y legales propias del sector "
            "sanitario. El stack tecnologico elegido (Python, FastAPI, Flask, PostgreSQL, "
            "MinIO, Spark, Docker, scikit-learn, PyTorch) es directamente transferible a "
            "un entorno profesional, y la arquitectura permite evolucionar a un despliegue "
            "real con cambios incrementales: anadir SSO, habilitar cifrado en reposo, "
            "incorporar un stack de observabilidad externo y certificar el modelo CNN "
            "clinicamente."
        ),
        highlight(
            "El proyecto se entrega como prototipo funcional end-to-end, documentado, "
            "testeado y reproducible, sentando una base solida sobre la que un equipo "
            "real podria construir un producto sanitario completo."
        ),
        PageBreak(),
    ]
    return out


def build_annex_a() -> list:
    out: list = [
        chapter(0, "Anexo A. Estructura del repositorio"),
        code(
            "Hospital_Project/\n"
            "|- backend/                  FastAPI modular\n"
            "|  |- app/\n"
            "|  |  |- api/                routers HTTP\n"
            "|  |  |- services/           logica de negocio\n"
            "|  |  |- repositories/       acceso a datos\n"
            "|  |  |- db/                 session, pool, schema\n"
            "|  |  |- storage/            adaptador S3 (boto3)\n"
            "|  |  |- schemas/            DTOs Pydantic\n"
            "|  |  |- core/               config tipada, logging\n"
            "|  |  '- utils/              helpers transversales\n"
            "|  |- tests/                 unit + api\n"
            "|  |- Dockerfile\n"
            "|  '- requirements.txt\n"
            "|\n"
            "|- dashboard/                Flask con app factory\n"
            "|  |- app/\n"
            "|  |  |- factory.py\n"
            "|  |  |- auth/\n"
            "|  |  |- blueprints/         /login, /, /upload, etc.\n"
            "|  |  |- services/\n"
            "|  |  |- presenters/\n"
            "|  |  |- triage/\n"
            "|  |  |- validation/\n"
            "|  |  '- core/\n"
            "|  |- templates/\n"
            "|  |- static/\n"
            "|  |- tests/                 unit + web\n"
            "|  |- Dockerfile\n"
            "|  '- requirements.txt\n"
            "|\n"
            "|- pipeline/                 Spark job modular\n"
            "|  |- app/\n"
            "|  |  |- core/               config, logging, spark_factory\n"
            "|  |  |- validators/         csv_schema\n"
            "|  |  |- transforms/         quality_filter\n"
            "|  |  |- writers/            postgres_writer, minio_writer\n"
            "|  |  '- reports/            run_report\n"
            "|  |- jobs/\n"
            "|  |  '- radiology_pipeline.py\n"
            "|  |- Dockerfile\n"
            "|  '- requirements.txt\n"
            "|\n"
            "|- ml/                       Entrenamiento de modelos\n"
            "|  |- train_cnn.py           ResNet18 para radiografias\n"
            "|  |- train_triage.py        Random Forest calibrado\n"
            "|  |- model_contract.json\n"
            "|  |- Dockerfile\n"
            "|  '- requirements.txt\n"
            "|\n"
            "|- models/                   Artefactos\n"
            "|  |- triage_model.joblib\n"
            "|  '- triage_metrics.json\n"
            "|\n"
            "|- data/\n"
            "|  |- incoming/              CSV de ingesta\n"
            "|  '- processed/             Salida del pipeline\n"
            "|\n"
            "|- infrastructure/\n"
            "|\n"
            "|- docs/                     Documentacion (este PDF, MD, SDD)\n"
            "|- .github/workflows/        CI con GitHub Actions\n"
            "|- .env.example\n"
            "|- docker-compose.yml\n"
            "|- iniciar_proyecto.bat\n"
            "'- README.md\n"
        ),
        PageBreak(),
    ]
    return out


def flatten(items: list) -> list:
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
    story += build_toc()
    story += build_ch1_summary()
    story += build_ch2_problem()
    story += build_ch3_data()
    story += build_ch4_architecture()
    story += build_ch5_models()
    story += build_ch6_pipeline()
    story += build_ch7_backend()
    story += build_ch8_dashboard()
    story += build_ch9_automation()
    story += build_ch10_integrations()
    story += build_ch11_quality()
    story += build_ch12_justification()
    story += build_ch13_diario()
    story += build_ch14_reflection()
    story += build_ch15_ethics()
    story += build_ch16_conclusions()
    story += build_annex_a()

    doc.build(flatten(story))
    print(f"PDF generado en: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
