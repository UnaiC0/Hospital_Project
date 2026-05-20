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
        ("B.", "Anexo: variables de entorno", True),
        ("C.", "Anexo: comandos de ejecucion", True),
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
        section("1.3", "Estado de la entrega"),
        highlight(
            "El proyecto cumple <b>todos los requisitos minimos del enunciado</b> en su "
            "alcance tecnico: modelo de IA, pipeline Big Data, dos sistemas de almacenamiento, "
            "automatizaciones, dashboard, containerizacion con un solo comando, calidad de "
            "datos, logging y documentacion. Los dos modelos de IA (Random Forest de triaje y "
            "CNN ResNet18 de radiologia) estan entrenados, persistidos en <i>/models</i> y "
            "cargados en caliente por el backend al iniciar."
        ),
        bullets([
            "Infraestructura Docker Compose: <b>9 servicios</b> operativos con healthchecks y volumenes persistentes.",
            "Backend FastAPI modular con <b>5 routers</b> (health, triage, radiology, quality, metrics).",
            "Dashboard Flask modular con app factory, blueprints de autenticacion y vistas operativas.",
            "Pipeline Spark modular separando validacion, transformacion, escritura y reporte.",
            "<b>Dos modelos</b> de IA entrenados y operativos: triaje Random Forest (accuracy 80.6 % sobre 8.000 muestras) y CNN ResNet18 (accuracy 95.04 % en validacion y 93.94 % en test).",
            "Cobertura de tests amplia: 18 archivos de tests en backend y 6 en dashboard.",
            "Acceso directo por HTTP a backend (:8000) y dashboard (:8501); HTTPS fuera de alcance del prototipo.",
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
        subsection("Imagenes de radiografias de torax (no estructurado)"),
        p(
            "Las imagenes son los datos no estructurados centrales del sistema. Se aceptan "
            "los formatos JPG, JPEG y PNG con un tamano maximo de 5 MB. La validacion se "
            "realiza en dos niveles: cliente (Flask) y servidor (FastAPI), comprobando "
            "extension declarada, tipo MIME y contenido binario real mediante Pillow para "
            "evitar archivos malformados o tipos enganados."
        ),
        p(
            "Para entrenamiento del modelo CNN se preve la incorporacion de un dataset "
            "publico como el <b>COVID-19 Radiography Database</b> (Kaggle, ~21k imagenes) "
            "siguiendo la estructura de directorios "
            "<i>data/radiology_dataset/{train,val}/{Sana,Neumonia,COVID-19}/</i>."
        ),
        subsection("CSV de estudios radiologicos (tabular, lote)"),
        p(
            "El pipeline Spark procesa lotes desde <i>data/incoming/radiology_studies.csv</i> "
            "con cabecera y las siguientes columnas obligatorias:"
        ),
        bullets([
            "<b>study_id</b>: identificador unico del estudio.",
            "<b>patient_age</b>: edad del paciente.",
            "<b>patient_sex</b>: M, F o U.",
            "<b>image_object_key</b>: clave del objeto en MinIO.",
            "<b>label</b>: etiqueta clinica (Sana, Neumonia, COVID-19).",
            "<b>acquisition_date</b>: fecha de adquisicion.",
            "<b>source</b>: equipo o departamento origen.",
        ]),
        subsection("Datos sinteticos para entrenamiento de triaje"),
        p(
            "El triaje se entrena con un dataset sintetico generado por "
            "<i>ml/train_triage.py</i>, inspirado en los protocolos <b>MEWS</b> (Modified "
            "Early Warning Score) y <b>NEWS2</b> (National Early Warning Score 2) utilizados "
            "en hospitales del Reino Unido y Espana. La generacion incluye:"
        ),
        bullets([
            "8.000 muestras sinteticas con variables continuas (edad, frecuencia cardiaca, saturacion, presion, frecuencia respiratoria, temperatura) y binarias (sintomas).",
            "Etiquetas calculadas con reglas MEWS/NEWS2 acotadas a cuatro niveles: <i>low</i>, <i>medium</i>, <i>high</i>, <i>critical</i>.",
            "Ruido de etiquetado del 6 % introducido deliberadamente para forzar generalizacion y evitar memorizacion.",
            "Division 80/20 entre entrenamiento y test, estratificada por clase.",
        ]),
        section("3.2", "Proceso de ingesta"),
        bullets([
            "<b>Ingesta desde dashboard</b>: el usuario sube una imagen por formulario HTML; Flask valida en cliente y delega al backend.",
            "<b>Ingesta desde API</b>: clientes externos pueden invocar <i>POST /predict</i> directamente con la imagen binaria.",
            "<b>Ingesta de lotes</b>: el pipeline Spark se dispara con <i>docker compose --profile pipeline up pipeline</i> y lee el CSV indicado por <i>PIPELINE_INPUT_PATH</i>.",
            "<b>Ingesta para entrenamiento</b>: el modulo <i>model-trainer</i> lee imagenes desde la estructura de directorios esperada en <i>data/radiology_dataset/</i>.",
        ]),
        section("3.3", "Limpieza y validacion"),
        p("La validacion se aplica de forma consistente en cada etapa del pipeline:"),
        bullets([
            "<b>Imagenes</b>: extension JPG/JPEG/PNG, tamano <= 5 MB, MIME real verificado con Pillow, deteccion de coherencia entre extension y formato real (rechazo de JPEG renombrado como PNG).",
            "<b>CSV tabular</b>: comprobacion de columnas obligatorias, validacion de tipos, recorte de espacios en blanco, etiquetas validas, no valores nulos en campos clave.",
            "<b>Detection de duplicados</b>: por <i>image_object_key</i>; ambos duplicados se rechazan.",
            "<b>Separacion de registros</b>: validos van a <i>data/processed/radiology_clean</i>; rechazados se documentan en el informe del run.",
            "<b>Eventos de calidad</b>: cualquier rechazo genera un evento de severidad <i>medium</i> en la tabla <i>quality_events</i>; un fallo de pipeline genera evento <i>high</i>.",
        ]),
        section("3.4", "Transformaciones aplicadas"),
        bullets([
            "<b>Spark</b>: normalizacion de strings (trim), conversion de tipos, calculo de columnas derivadas y particionado del DataFrame para escritura.",
            "<b>Imagenes (entrenamiento)</b>: resize a 224x224, conversion a tensor, normalizacion con la media y desviacion estandar de ImageNet (<i>mean=[0.485, 0.456, 0.406]</i>, <i>std=[0.229, 0.224, 0.225]</i>).",
            "<b>Augmentations en training</b>: horizontal flip aleatorio (p=0.5) y rotacion +/-8 grados para reducir overfitting con datasets pequenos.",
            "<b>Imagenes (inferencia ResNet18)</b>: resize a 224x224, conversion a tensor RGB, normalizacion con la misma media y desviacion utilizadas en entrenamiento (parametros de ImageNet) y forward a traves de la red en modo <i>eval</i>.",
        ]),
        section("3.5", "Almacenamiento final"),
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
        section("4.2", "Diseno del pipeline de datos"),
        p(
            "El pipeline de datos se concibe en cuatro fases claras: <b>ingesta</b>, "
            "<b>validacion</b>, <b>transformacion</b> y <b>servicio</b>. Cada fase es "
            "independiente y testeable, y el pipeline Spark esta modularizado en submodulos "
            "(<i>validators</i>, <i>transforms</i>, <i>writers</i>, <i>reports</i>) para "
            "facilitar mantenimiento."
        ),
        bullets([
            "<b>Ingesta</b>: dashboard (imagenes individuales), API (clientes externos), pipeline Spark (lotes CSV).",
            "<b>Validacion</b>: esquema, tipos, integridad, calidad de imagen.",
            "<b>Transformacion</b>: preprocesamiento de imagen, limpieza tabular, derivacion de campos.",
            "<b>Servicio</b>: API REST tipada, dashboard web, MinIO API S3.",
        ]),
        section("4.3", "Infraestructura containerizada"),
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
        section("4.4", "Relacion entre componentes"),
        p(
            "El flujo end-to-end de un estudio radiologico atraviesa cinco fronteras de "
            "integracion:"
        ),
        bullets([
            "<b>1. Navegador --&gt; Dashboard</b>: HTTP con cookie de sesion firmada (SECRET_KEY), HttpOnly, SameSite=Lax.",
            "<b>2. Dashboard --&gt; MinIO</b>: subida directa de la imagen a <i>uploads/&lt;uuid&gt;.&lt;ext&gt;</i> mediante boto3.",
            "<b>3. Dashboard --&gt; Backend</b>: POST <i>/predict</i> con la imagen y la clave de objeto ya conocida.",
            "<b>4. Backend --&gt; Servicios internos</b>: inferencia, persistencia en PostgreSQL (pool) y en MinIO (informe JSON), todo en una sola transaccion ACID.",
            "<b>5. Respuesta</b>: el dashboard renderiza resultado, probabilidades, banderas de calidad y enlace al informe.",
        ]),
        section("4.5", "Capa de seguridad"),
        bullets([
            "<b>Autenticacion local</b>: usuarios admin y doctor con contrasenas hash Werkzeug (PBKDF2-SHA256, 1M iteraciones).",
            "<b>Roles</b>: admin ve almacenamiento MinIO y todas las metricas; doctor accede a radiologia y resultados.",
            "<b>Sesiones</b>: cookie firmada con SECRET_KEY de longitud >= 32 bytes; expira al cerrar el navegador.",
            "<b>Puertos restringidos</b>: todos los puertos publicados estan enlazados a 127.0.0.1, no a 0.0.0.0.",
            "<b>Variables sensibles</b>: externalizadas en <i>.env</i> con la sintaxis <i>${VAR:?Set VAR in .env}</i> que falla rapido si faltan.",
            "<b>Credenciales nunca en repositorio</b>: <i>.env</i>, certificados y artefactos sensibles excluidos por <i>.gitignore</i>.",
        ]),
        PageBreak(),
    ]
    return out


def build_ch5_models() -> list:
    out: list = [
        chapter(5, "Modelos de Inteligencia Artificial"),
        section("5.1", "Modelo de triaje (Random Forest calibrado)"),
        subsection("Justificacion de la arquitectura"),
        p(
            "El triaje clinico opera sobre datos tabulares de baja dimensionalidad (~17 "
            "variables tras one-hot encoding de sintomas). Para este tipo de problema se "
            "ha seleccionado un <b>Random Forest</b> con 400 arboles y profundidad maxima "
            "12, posteriormente <b>calibrado isotonicamente</b> con CalibratedClassifierCV "
            "para producir probabilidades clinicamente interpretables. La eleccion se "
            "justifica por:"
        ),
        bullets([
            "<b>Interpretabilidad</b>: feature importances directamente comparables con la intuicion clinica (saturacion y bleeding son las variables top).",
            "<b>Robustez frente a outliers</b>: caracteristica intrinseca de los ensembles de arboles.",
            "<b>Sin necesidad de GPU</b>: entrenable en CPU en menos de 20 segundos.",
            "<b>Buen comportamiento con datasets pequenos</b>: 8.000 muestras son suficientes para generalizar.",
            "<b>Calibracion isotonica</b>: corrige el sesgo de probabilidades hacia 0.5/1 tipico en RF y produce probabilidades clinicamente fiables.",
        ]),
        subsection("Generacion del dataset sintetico"),
        p(
            "El script <i>ml/train_triage.py</i> genera 8.000 muestras a partir de reglas "
            "inspiradas en MEWS y NEWS2. Cada muestra incluye seis variables continuas "
            "(edad, frecuencia cardiaca, saturacion, presion sistolica, frecuencia "
            "respiratoria y temperatura) y diez variables binarias correspondientes a "
            "sintomas frecuentes (dolor toracico, disnea, perdida de conciencia, fiebre, "
            "tos, dolor abdominal, cefalea, mareo, vomitos, sangrado)."
        ),
        p(
            "Las etiquetas se calculan con un sistema de puntuacion que respeta la "
            "logica clinica: hipoxia, taquicardia e hipotension contribuyen al score, los "
            "sintomas red-flag (dolor toracico, disnea, perdida de conciencia, sangrado) "
            "elevan el riesgo, y el resultado se discretiza en cuatro niveles. Se anade un "
            "<b>6 % de ruido</b> en las etiquetas para forzar la generalizacion."
        ),
        subsection("Entrenamiento y calibracion isotonica"),
        bullets([
            "Train/test split estratificado 80/20 con <i>random_state=42</i>.",
            "Entrenamiento del Random Forest con 400 arboles y <i>max_depth=12</i>.",
            "Calibracion isotonica sobre las probabilidades del clasificador base.",
            "Persistencia del modelo calibrado y de las metricas en <i>models/triage_model.joblib</i> y <i>models/triage_metrics.json</i>.",
            "Duracion total del entrenamiento: ~16 segundos en CPU.",
        ]),
        subsection("Metricas y resultados"),
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
        subsection("Justificacion de la arquitectura"),
        p(
            "Para la clasificacion de radiografias se ha seleccionado <b>ResNet18</b>. La "
            "justificacion responde a cuatro criterios:"
        ),
        bullets([
            "<b>Madurez probada</b>: ResNet18 es uno de los backbones mas usados en imagen medica con literatura abundante.",
            "<b>Bajo coste de inferencia</b>: 11.7 M parametros, latencia de inferencia baja incluso en CPU.",
            "<b>Profundidad razonable</b>: 18 capas suficientes para capturar patrones radiologicos sin sobreparametrizar.",
            "<b>Escalabilidad</b>: si se necesita mas capacidad se puede pasar a ResNet50 o EfficientNet sin cambiar el resto del pipeline.",
        ]),
        subsection("Configuracion del entrenamiento"),
        p(
            "El modelo se ha entrenado en GPU (CUDA) sobre un dataset publico de "
            "radiografias de torax con tres clases. La configuracion final usada en la "
            "version 0.2.0 del artefacto se resume en la siguiente tabla."
        ),
        table(
            ["Parametro", "Valor"],
            [
                ["Arquitectura", "ResNet18 (entrenada desde cero)"],
                ["Dispositivo", "CUDA (GPU)"],
                ["Epochs", "5"],
                ["Batch size", "16"],
                ["Learning rate", "5e-4"],
                ["Optimizador", "AdamW"],
                ["Loss", "CrossEntropyLoss con class weights"],
                ["Class weights", "COVID-19=3.73, Sana=1.35, Neumonia=0.50"],
                ["Val split", "20 % estratificado"],
                ["Seed", "42 (reproducibilidad)"],
                ["Duracion total", "1.055 segundos (~17.5 minutos)"],
            ],
            col_widths=[5.0 * cm, 11.5 * cm],
        ),
        p(
            "Los <b>class weights</b> son inversamente proporcionales a la frecuencia de "
            "cada clase. El dataset esta fuertemente desbalanceado (Neumonia es ~7 veces "
            "mas frecuente que COVID-19), y esta ponderacion fuerza al modelo a no "
            "ignorar las clases minoritarias durante el entrenamiento."
        ),
        subsection("Preprocesamiento y data augmentation"),
        table(
            ["Etapa", "Operacion"],
            [
                ["Resize", "224 x 224"],
                ["Normalizacion", "mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]"],
                ["Augmentation (train)", "RandomHorizontalFlip(p=0.5), RandomRotation(8 grados)"],
                ["Conversion", "ToTensor"],
            ],
            col_widths=[4.0 * cm, 12.5 * cm],
        ),
        subsection("Distribucion del dataset"),
        table(
            ["Particion", "COVID-19", "Sana", "Neumonia", "Total"],
            [
                ["Train", "368", "1.013", "2.734", "4.115"],
                ["Validation", "92", "253", "684", "1.029"],
                ["Test", "116", "317", "855", "1.288"],
                ["<b>Total</b>", "<b>576</b>", "<b>1.583</b>", "<b>4.273</b>", "<b>6.432</b>"],
            ],
            col_widths=[3.3 * cm, 3.3 * cm, 3.3 * cm, 3.3 * cm, 3.3 * cm],
        ),
        subsection("Evolucion del entrenamiento por epoch"),
        table(
            ["Epoch", "Train loss", "Train acc", "Val loss", "Val acc"],
            [
                ["1", "0.402", "0.823", "0.221", "0.915"],
                ["2", "0.290", "0.877", "0.321", "0.865"],
                ["3", "0.226", "0.903", "0.200", "0.930"],
                ["4", "0.206", "0.910", "0.274", "0.894"],
                ["<b>5</b>", "<b>0.214</b>", "<b>0.907</b>", "<b>0.147</b>", "<b>0.950</b>"],
            ],
            col_widths=[2.5 * cm, 3.5 * cm, 3.5 * cm, 3.5 * cm, 3.5 * cm],
        ),
        p(
            "El mejor checkpoint corresponde a la epoch 5, con una accuracy de validacion "
            "del <b>95.04 %</b> y la loss mas baja observada. La curva muestra cierta "
            "fluctuacion en validacion (caida en epoch 2 y 4) caracteristica del "
            "entrenamiento desde cero sin warmup; la tendencia general es claramente "
            "ascendente."
        ),
        subsection("Resultados sobre el conjunto de validacion (mejor checkpoint)"),
        p("<b>Accuracy global: 95.04 %</b> &mdash; <b>Loss: 0.147</b>"),
        table(
            ["Clase", "Precision", "Recall", "F1-score", "Soporte"],
            [
                ["COVID-19", "0.899", "<b>0.967</b>", "0.932", "92"],
                ["Sana", "0.901", "0.937", "0.919", "253"],
                ["Neumonia", "0.978", "0.953", "0.965", "684"],
                ["<b>Macro avg</b>", "<b>0.926</b>", "<b>0.952</b>", "<b>0.939</b>", "1.029"],
                ["<b>Weighted avg</b>", "<b>0.952</b>", "<b>0.950</b>", "<b>0.951</b>", "1.029"],
            ],
            col_widths=[3.5 * cm, 3.0 * cm, 3.0 * cm, 3.0 * cm, 4.0 * cm],
        ),
        subsection("Matriz de confusion sobre validacion"),
        table(
            ["Real / Predicho", "COVID-19", "Sana", "Neumonia"],
            [
                ["<b>COVID-19</b>", "<b>89</b>", "1", "2"],
                ["<b>Sana</b>", "3", "<b>237</b>", "13"],
                ["<b>Neumonia</b>", "7", "25", "<b>652</b>"],
            ],
            col_widths=[4.5 * cm, 4.0 * cm, 4.0 * cm, 4.0 * cm],
        ),
        subsection("Resultados sobre el conjunto de test (generalizacion)"),
        p("<b>Accuracy global: 93.94 %</b> &mdash; <b>Loss: 0.168</b>"),
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
        subsection("Tipos de error y matriz de confusion"),
        p(
            "Para el triaje, la matriz de confusion del Random Forest sobre el test set "
            "(1.600 muestras) revela el siguiente comportamiento:"
        ),
        table(
            ["Real / Predicho", "low", "medium", "high", "critical"],
            [
                ["low", "286", "75", "2", "0"],
                ["medium", "58", "488", "36", "1"],
                ["high", "2", "94", "150", "12"],
                ["critical", "0", "2", "28", "366"],
            ],
            col_widths=[4.0 * cm, 3.1 * cm, 3.1 * cm, 3.1 * cm, 3.1 * cm],
        ),
        p(
            "<b>Lectura clinica</b>: los errores se concentran en confusiones entre niveles "
            "adyacentes (low &lt;-&gt; medium, medium &lt;-&gt; high). Las confusiones "
            "<b>saltando dos niveles son raras</b>: solo 2 casos de <i>low</i> clasificados "
            "como <i>high</i> y ninguno como <i>critical</i>. Esta es la propiedad mas "
            "deseable: el modelo nunca \"olvida\" un caso critico clasificandolo como "
            "trivial."
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
        section("6.2", "Fases del pipeline"),
        p("El job Spark <i>radiology_pipeline.py</i> cubre cuatro fases secuenciales:"),
        bullets([
            "<b>1. Ingesta</b>: lectura del CSV desde <i>PIPELINE_INPUT_PATH</i> usando <i>spark.read.csv()</i> con cabecera, inferencia de tipos y opcion <i>multiLine</i>.",
            "<b>2. Validacion</b>: comprobacion de columnas obligatorias, tipos, etiquetas validas y deteccion de duplicados por <i>image_object_key</i>.",
            "<b>3. Transformacion</b>: trim de strings, normalizacion de campos categoricos, recalculo de columnas derivadas.",
            "<b>4. Escritura</b>: persistencia de datos limpios en JSON a <i>PIPELINE_OUTPUT_PATH</i>, registro de ejecucion en PostgreSQL y publicacion de informe JSON en MinIO.",
        ]),
        section("6.3", "Validators, transforms y writers"),
        p(
            "El pipeline esta <b>modularizado</b> en submodulos especializados, cada uno "
            "con una responsabilidad unica:"
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
            "El backend FastAPI sigue una <b>arquitectura en capas</b> con cinco "
            "responsabilidades claramente separadas:"
        ),
        code(
            "backend/app/\n"
            "|- main.py                  app factory, lifespan, middleware\n"
            "|- api/\n"
            "|  |- deps.py               inyeccion de dependencias (lru_cache)\n"
            "|  |- errors.py             handlers de error globales\n"
            "|  '- routers/              5 routers HTTP\n"
            "|      |- health.py\n"
            "|      |- triage.py\n"
            "|      |- radiology.py\n"
            "|      |- quality.py\n"
            "|      '- metrics.py\n"
            "|- services/                logica de negocio\n"
            "|  |- inference_service.py  carga y forward del ResNet18\n"
            "|  |- triage_service.py     orquestacion triaje\n"
            "|  |- triage_model.py       carga del Random Forest\n"
            "|  |- radiology_service.py  flujo completo de prediccion\n"
            "|  |- quality_service.py    gestion de eventos\n"
            "|  |- metrics_service.py    agregados para dashboard\n"
            "|  '- health_service.py     comprobacion de dependencias\n"
            "|- repositories/            acceso a datos (psycopg)\n"
            "|  |- radiology_repository.py\n"
            "|  |- triage_repository.py\n"
            "|  |- quality_repository.py\n"
            "|  '- metrics_repository.py\n"
            "|- db/                      session, pool, schema, transaccion\n"
            "|- storage/                 adaptador S3 (boto3)\n"
            "|- schemas/                 Pydantic (DTOs tipados)\n"
            "|- core/                    config tipada, logging\n"
            "'- utils/                   helpers transversales\n"
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
        section("7.3", "Capa de persistencia"),
        p(
            "El backend utiliza un <b>connection pool</b> de psycopg con tamano configurable "
            "(por defecto 2 a 10 conexiones). El pool se abre en el <i>lifespan</i> de "
            "FastAPI y se cierra al apagarse. Cada operacion compuesta se ejecuta dentro de "
            "una <b>transaccion ACID</b> mediante un context manager que comparte el cursor "
            "entre los repositorios implicados, garantizando que el estudio, los eventos "
            "asociados y los informes JSON queden persistidos atomicamente."
        ),
        p(
            "El esquema de PostgreSQL incluye las tablas <i>radiology_studies</i>, "
            "<i>triage_assessments</i>, <i>quality_events</i> y <i>pipeline_runs</i>, "
            "creadas automaticamente al arranque con reintentos espaciados 2 segundos para "
            "tolerar arranques concurrentes con la base de datos."
        ),
        section("7.4", "Healthchecks y observabilidad"),
        bullets([
            "<b>Liveness</b>: <i>GET /health</i> responde 200 si el servicio esta arriba.",
            "<b>Readiness</b>: verifica conectividad con PostgreSQL y MinIO; devuelve estado por dependencia.",
            "<b>Healthcheck Docker</b>: cada 10 segundos urllib comprueba <i>http://localhost:8000/health</i>.",
            "<b>Logs estructurados</b>: formato JSON con campos timestamp, level, service, message y trace context cuando aplica.",
            "<b>Snapshot de negocio</b>: <i>GET /metrics</i> retorna agregados consumidos por el dashboard (radiografias procesadas, distribucion por clase, triajes por nivel, eventos abiertos por severidad, ultima ejecucion del pipeline).",
        ]),
        PageBreak(),
    ]
    return out


def build_ch8_dashboard() -> list:
    out: list = [
        chapter(8, "Dashboard"),
        section("8.1", "Arquitectura Flask"),
        p(
            "El dashboard utiliza Flask con el patron <b>app factory</b> y <b>blueprints</b>. "
            "Esto permite separar la creacion de la aplicacion de su configuracion, facilita "
            "el testing con clientes efimeros y permite registrar grupos de rutas como "
            "modulos independientes."
        ),
        code(
            "dashboard/app/\n"
            "|- factory.py               create_app() con config tipada\n"
            "|- auth/                    Werkzeug, sesiones firmadas, roles\n"
            "|- blueprints/\n"
            "|  |- auth.py               /login, /logout\n"
            "|  '- main.py               /, /upload, /history, /events, /storage\n"
            "|- services/                cliente HTTP del backend, cliente MinIO\n"
            "|- presenters/              traduccion de respuestas API a vistas\n"
            "|- triage/                  servicios y formularios de triaje\n"
            "|- validation/              validacion de imagenes en cliente\n"
            "|- core/                    config tipada, logging JSON\n"
            "'- templates / static       Jinja2, CSS, JS minimo\n"
        ),
        section("8.2", "Autenticacion y roles"),
        bullets([
            "<b>Hash de contrasenas</b>: PBKDF2-SHA256 con 1.000.000 iteraciones (Werkzeug).",
            "<b>Variables sensibles</b>: <i>ADMIN_USERNAME</i>, <i>ADMIN_PASSWORD_HASH</i>, <i>USER_USERNAME</i>, <i>USER_PASSWORD_HASH</i> definidas en <i>.env</i>.",
            "<b>Dos roles</b>: <i>admin</i> (acceso a almacenamiento MinIO y todas las vistas) y <i>user</i> (solo radiologia y resultados).",
            "<b>Cookie de sesion</b>: firmada con <i>SECRET_KEY</i> (>= 32 bytes), HttpOnly, SameSite=Lax, Secure en produccion (controlable con <i>SESSION_COOKIE_SECURE</i>).",
            "<b>Proteccion CSRF</b>: tokens generados por sesion para formularios criticos.",
            "<b>Decorator <i>login_required</i></b>: aplicado a todas las rutas que no son <i>/login</i>.",
        ]),
        section("8.3", "Vistas principales"),
        table(
            ["Ruta", "Plantilla", "Funcion"],
            [
                ["GET /login", "login.html", "Formulario de autenticacion"],
                ["GET /", "index.html", "Dashboard principal con metricas y atajos"],
                ["GET /upload", "upload.html", "Formulario de subida de radiografia"],
                ["POST /upload", "result.html", "Resultado de la clasificacion"],
                ["GET /triage", "triage.html", "Formulario de evaluacion de triaje"],
                ["POST /triage", "triage_result.html", "Resultado del triaje"],
                ["GET /history", "history.html", "Historial de estudios y triajes"],
                ["GET /events", "events.html", "Eventos de calidad abiertos"],
                ["GET /storage", "storage.html", "(admin) consola de MinIO embebida"],
                ["GET /logout", "-", "Invalidacion de sesion"],
            ],
            col_widths=[3.5 * cm, 3.5 * cm, 9.5 * cm],
        ),
        section("8.4", "Integracion con backend y MinIO"),
        bullets([
            "<b>Cliente HTTP del backend</b>: servicio interno con timeout, manejo de errores y mapeo de respuestas a presenters.",
            "<b>Cliente MinIO con boto3</b>: subida directa de imagenes desde el navegador a <i>uploads/&lt;uuid&gt;.&lt;ext&gt;</i>.",
            "<b>Visualizacion del resultado</b>: imagen original incrustada en base64, probabilidades por clase, banderas de calidad y enlace al informe JSON en MinIO.",
            "<b>Historico</b>: paginacion y ordenacion descendente por timestamp.",
            "<b>Estado del pipeline</b>: el dashboard consume <i>GET /metrics</i> y renderiza un panel con la ultima ejecucion del job Spark.",
        ]),
        PageBreak(),
    ]
    return out


def build_ch9_automation() -> list:
    out: list = [
        chapter(9, "Automatizaciones"),
        section("9.1", "Creacion automatica de bucket MinIO"),
        p(
            "El adaptador <i>ObjectStorage</i> incluye un metodo <i>ensure_bucket()</i> "
            "que crea el bucket si no existe, controlado por la bandera "
            "<i>MINIO_AUTO_CREATE_BUCKET</i>. Esto elimina la friccion de tener que "
            "preparar el bucket manualmente antes del primer arranque."
        ),
        section("9.2", "Generacion automatica de informes JSON"),
        bullets([
            "<b>Por estudio radiologico</b>: cada llamada a <i>/predict</i> persiste un JSON en <i>radiology-reports/&lt;study_id&gt;.json</i> con resultado, probabilidades, metadatos y nota clinica.",
            "<b>Por triaje</b>: cada llamada a <i>/triage</i> persiste un JSON en <i>triage-reports/&lt;triage_id&gt;.json</i> con score, nivel de riesgo, prioridad recomendada y desglose por variable.",
            "<b>Por ejecucion de pipeline</b>: cada run del job Spark publica un JSON en <i>pipeline-reports/&lt;run_id&gt;.json</i> con distribucion de clases, rechazos y duplicados.",
        ]),
        section("9.3", "Eventos de calidad automaticos"),
        p(
            "Los eventos se generan dentro de la misma transaccion que la operacion que los "
            "dispara, garantizando consistencia ACID. Si la operacion falla, los eventos no "
            "quedan huerfanos."
        ),
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
        section("9.4", "Procesamiento batch del pipeline"),
        bullets([
            "El job Spark se ejecuta bajo demanda con <i>docker compose --profile pipeline up pipeline</i>.",
            "Procesa todo el CSV de entrada en una sola pasada, validando, transformando, escribiendo y reportando.",
            "El resultado queda inmediatamente accesible para el dashboard via las metricas del backend.",
            "Cualquier fallo del job genera evento <i>high</i> automaticamente y se registra en <i>pipeline_runs</i> con status <i>failed</i>.",
        ]),
        section("9.5", "Healthchecks y reinicios"),
        bullets([
            "<b>Backend</b>: healthcheck con urllib cada 10 segundos contra <i>/health</i>; reinicio automatico si falla.",
            "<b>PostgreSQL</b>: healthcheck con <i>pg_isready</i> cada 10 segundos.",
            "<b>MinIO</b>: healthcheck con <i>mc ready local</i> cada 10 segundos.",
            "<b>restart: always</b> en backend, dashboard, db, minio, spark, spark-worker: reinicio automatico ante cualquier caida.",
            "<b>restart: \"no\"</b> en pipeline y trainers: se ejecutan una sola vez (jobs batch).",
            "<b>depends_on con condition</b>: el backend solo arranca cuando db y minio estan saludables.",
        ]),
        PageBreak(),
    ]
    return out


def build_ch10_integrations() -> list:
    out: list = [
        chapter(10, "Integraciones"),
        section("10.1", "Flujo completo de datos end-to-end"),
        p(
            "El recorrido completo de un estudio radiologico, desde que el usuario sube la "
            "imagen hasta que el informe queda persistido y disponible para consulta, "
            "atraviesa los siguientes pasos:"
        ),
        code(
            "1. Usuario autenticado abre /upload en dashboard\n"
            "2. Dashboard valida formato/tamano en cliente (JS)\n"
            "3. Dashboard sube imagen a MinIO bajo uploads/<uuid>.<ext>\n"
            "4. Dashboard hace POST /predict al backend con imagen + object_key\n"
            "5. Backend valida imagen con Pillow (MIME real, contenido)\n"
            "6. Backend ejecuta InferenceService.predict()\n"
            "7. Backend abre transaccion (Unit of Work)\n"
            "   7.1. INSERT en radiology_studies (PostgreSQL)\n"
            "   7.2. PUT en radiology-reports/<id>.json (MinIO)\n"
            "   7.3. INSERT en quality_events si COVID o baja confianza (PostgreSQL)\n"
            "   7.4. COMMIT atomico\n"
            "8. Backend devuelve respuesta JSON tipada\n"
            "9. Dashboard renderiza resultado en result.html\n"
            "10. Usuario puede descargar el informe desde el enlace MinIO\n"
        ),
        section("10.2", "Conexiones entre modulos"),
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
        section("10.3", "Variables de entorno y configuracion externalizada"),
        p(
            "La configuracion se carga de forma <b>tipada al arranque</b> (fail-fast). Si "
            "una variable obligatoria falta, el servicio aborta inmediatamente con un "
            "mensaje claro. La sintaxis <i>${VAR:?Set VAR in .env}</i> en docker-compose.yml "
            "fuerza este comportamiento."
        ),
        p(
            "Las variables se agrupan logicamente en cinco bloques: PostgreSQL, MinIO, "
            "autenticacion del dashboard, parametros de entrenamiento y configuracion del "
            "pipeline. El detalle completo se documenta en el <b>Anexo B</b>."
        ),
        PageBreak(),
    ]
    return out


def build_ch11_quality() -> list:
    out: list = [
        chapter(11, "Calidad, testing y CI/CD"),
        section("11.1", "Cobertura de tests"),
        p(
            "El proyecto incluye una suite de tests automatizados organizada en dos capas "
            "(unit y api/web). La estrategia es usar <b>dobles que respetan los contratos "
            "reales</b> de las interfaces, no MagicMock genericos, lo que permite que los "
            "cambios de infraestructura (por ejemplo migracion a connection pool) no rompan "
            "los tests."
        ),
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
            "Las suites se ejecutan con <i>pytest --cov=app --cov-report=term</i> en cada "
            "modulo. La cobertura de la logica de negocio supera el 90 % en el backend."
        ),
        section("11.2", "Validacion de calidad de datos"),
        bullets([
            "<b>En el cliente</b>: JavaScript verifica extension y tamano antes de la subida.",
            "<b>En el servidor (FastAPI)</b>: Pillow comprueba el contenido binario real, no solo el MIME declarado.",
            "<b>En el pipeline (Spark)</b>: validacion de schema, deteccion de duplicados, etiquetas validas, no nulos en campos clave.",
            "<b>Generacion automatica de eventos</b>: cualquier registro rechazado o problema de calidad genera una entrada en <i>quality_events</i>.",
            "<b>Dashboard de calidad</b>: vista dedicada en <i>/events</i> que lista eventos abiertos por severidad.",
        ]),
        section("11.3", "Logging centralizado"),
        p(
            "Todos los servicios (backend, dashboard, pipeline) utilizan el modulo "
            "<i>logging</i> de Python configurado en formato JSON estructurado. Cada linea "
            "de log incluye timestamp ISO 8601, level, servicio, mensaje y contexto "
            "adicional (request_id, study_id, run_id cuando aplica). Esto facilita el "
            "agregado en herramientas de log management futuras (ELK, Loki)."
        ),
        section("11.4", "Pipeline CI (GitHub Actions)"),
        bullets([
            "Workflow <i>.github/workflows/ci.yml</i> dispara en cada push y pull request.",
            "Ejecuta <i>pytest --cov</i> sobre backend y dashboard.",
            "Valida la sintaxis de <i>docker-compose.yml</i> con <i>docker compose config</i>.",
            "Falla rapido ante cualquier fallo de test o de validacion.",
            "Garantiza que la rama principal mantiene siempre los tests en verde.",
        ]),
        PageBreak(),
    ]
    return out


def build_ch12_justification() -> list:
    out: list = [
        chapter(12, "Justificaciones tecnicas y alternativas"),
        section("12.1", "Eleccion de PostgreSQL + MinIO"),
        p(
            "<b>Alternativas evaluadas</b>: MySQL, MongoDB, SQLite, GridFS, sistema de "
            "archivos local, Amazon S3, Azure Blob.<br/>"
            "<b>Decision</b>: PostgreSQL 16 + MinIO.<br/>"
            "<b>Motivo</b>: PostgreSQL ofrece transacciones ACID solidas, JSONB para datos "
            "semiestructurados, indices parciales y agregados condicionales que simplifican "
            "consultas de metricas. MinIO ofrece la API S3 estandar, permitiendo migrar a "
            "AWS S3 real con un simple cambio de configuracion. MongoDB se descarto porque "
            "la mayoria de datos tienen esquema estable y se benefician de garantias "
            "relacionales. GridFS fragmentaria el almacenamiento entre dos sistemas "
            "distintos (estructurado y binario en Mongo) complicando los backups."
        ),
        section("12.2", "Eleccion de Spark sobre Dask y Beam"),
        p(
            "<b>Alternativas evaluadas</b>: Dask, Apache Beam, pandas con procesamiento por "
            "lotes.<br/>"
            "<b>Decision</b>: Apache Spark 3.5.8 con PySpark.<br/>"
            "<b>Motivo</b>: Spark es el estandar de facto en entornos hospitalarios y de "
            "investigacion biomedica con grandes volumenes. Dask es atractivo para "
            "workloads numpy-centric pero menos maduro para SQL y joins. Apache Beam ofrece "
            "portabilidad multi-runner que excede el alcance del prototipo. Aunque el "
            "volumen del prototipo es pequeno, la eleccion de Spark prepara la plataforma "
            "para escalado horizontal real."
        ),
        section("12.3", "Eleccion de Random Forest para triaje"),
        p(
            "<b>Alternativas evaluadas</b>: Logistic Regression, Gradient Boosting (XGBoost, "
            "LightGBM), red neuronal tabular (MLP), reglas deterministas puras.<br/>"
            "<b>Decision</b>: Random Forest con 400 arboles y calibracion isotonica.<br/>"
            "<b>Motivo</b>: la interpretabilidad clinica es obligatoria en triaje (cada "
            "decision debe poder explicarse a un facultativo). Random Forest ofrece feature "
            "importances directamente comparables con la intuicion clinica. XGBoost habria "
            "dado quizas un 1-2 % mas de accuracy pero a costa de complejidad de tuning y "
            "explicabilidad. Las redes neuronales tabulares no estan justificadas para 17 "
            "features con 8.000 muestras. La calibracion isotonica corrige el sesgo de "
            "probabilidades tipico en RF."
        ),
        section("12.4", "Eleccion de ResNet18 para clasificacion radiologica"),
        p(
            "<b>Alternativas evaluadas</b>: CNN propia, ResNet50, EfficientNet-B0, Vision "
            "Transformer (ViT), DenseNet121.<br/>"
            "<b>Decision</b>: ResNet18 con transfer learning opcional desde ImageNet.<br/>"
            "<b>Motivo</b>: balance entre capacidad (11.7M parametros) y coste de "
            "inferencia (latencia &lt; 50 ms en CPU). Literatura medica abundante con "
            "este backbone. Transfer learning eficaz incluso con datasets hospitalarios "
            "pequenos. ResNet50 anadiria 14M parametros sin ganancia clara en datasets "
            "pequenos. ViT requiere muchos mas datos para entrenar desde cero. EfficientNet "
            "es competitiva pero menos estandar en literatura clinica."
        ),
        section("12.5", "Eleccion de FastAPI + Flask"),
        p(
            "<b>Alternativas para backend</b>: Flask, Django REST, Litestar.<br/>"
            "<b>Decision backend</b>: FastAPI.<br/>"
            "<b>Motivo</b>: tipado fuerte mediante Pydantic, generacion automatica de "
            "OpenAPI consumible desde el dashboard de pruebas, soporte asincrono nativo, "
            "ecosistema maduro de inyeccion de dependencias. Flask habria requerido capas "
            "adicionales (Marshmallow, Flask-RESTX) para alcanzar la misma validacion."
        ),
        p(
            "<b>Alternativas para dashboard</b>: Streamlit, Dash, FastAPI con Jinja, SPA "
            "(React/Vue).<br/>"
            "<b>Decision dashboard</b>: Flask con Jinja y blueprints.<br/>"
            "<b>Motivo</b>: Streamlit no permite personalizacion visual suficiente para una "
            "UI medica. Dash esta orientado a visualizacion analitica, no a flujos "
            "transaccionales con autenticacion. Un SPA habria sobredimensionado el proyecto."
        ),
        section("12.6", "Eleccion de Docker Compose"),
        p(
            "<b>Alternativas evaluadas</b>: Kubernetes (kind / minikube), Nomad, "
            "podman-compose.<br/>"
            "<b>Decision</b>: Docker Compose.<br/>"
            "<b>Motivo</b>: el enunciado pide explicitamente que cualquier persona pueda "
            "levantar el sistema con un unico comando. Kubernetes anadiria una curva de "
            "aprendizaje desproporcionada para un prototipo. La migracion futura a "
            "Kubernetes es factible reutilizando los Dockerfiles existentes."
        ),
        section("12.7", "Alternativas descartadas"),
        bullets([
            "<b>SQLAlchemy ORM</b>: descartado en favor de psycopg directo + repositorios; el proyecto no necesita el overhead de un ORM completo y SQL puro es mas predecible para consultas analiticas.",
            "<b>Conexion por request</b>: descartado en favor de psycopg_pool para evitar el coste de handshake TLS y autenticacion en cada peticion.",
            "<b>pgbouncer externo</b>: descartado por anadir un servicio mas; el pool del cliente es suficiente para la carga del prototipo.",
            "<b>Pipelines schedulados con cron</b>: descartado para esta entrega; el pipeline se ejecuta on-demand. Migracion futura a Airflow o Prefect documentada en el capitulo 14.",
            "<b>Telemetria externa (Datadog, New Relic)</b>: descartado por preservar control de datos sensibles y reducir dependencia de SaaS de terceros.",
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
        p(
            "<b>Justificacion de la combinacion</b>: Claude Code excele en cambios "
            "extensos sobre el repositorio con validacion automatizada (ideal para la "
            "fase de consolidacion); Codex resulta mas agil para autocompletado puntual; "
            "ChatGPT es eficaz como pizarra conceptual. Las tres herramientas estan "
            "explicitamente listadas en el enunciado como aceptadas."
        ),
        section("13.2", "Ejemplos representativos de prompts"),
        p(
            "A continuacion se presentan seis prompts representativos del proceso de "
            "desarrollo, organizados por fase. Cada uno incluye el texto enviado a la "
            "herramienta, el resultado obtenido, la valoracion y el aprendizaje extraido."
        ),
        subsection("Prompt 1 — Auditoria inicial del repositorio"),
        code(
            "Herramienta: Claude Code\n"
            "Fase: Auditoria inicial\n\n"
            "Prompt:\n"
            "  Revisa que todo lo del enunciado se cumple. Analiza el repositorio\n"
            "  completo y dame un informe de que falta y que esta mal."
        ),
        bullets([
            "<b>Resultado</b>: la IA identifico que el backend era un monolito en un solo archivo, que no habia tests, que el clasificador radiologico activo era un baseline estadistico sin modelo entrenado, y que faltaban pipeline Spark funcional, calidad de datos, automatizaciones y documentacion tecnica completa.",
            "<b>Valoracion</b>: acierto total. La auditoria fue precisa y accionable.",
            "<b>Aprendizaje</b>: dar a la IA acceso al enunciado junto con el repositorio permite detectar la brecha entre lo pedido y lo entregado mejor que una revision manual rapida.",
        ]),
        subsection("Prompt 2 — Modularizacion del backend"),
        code(
            "Herramienta: Claude Code\n"
            "Fase: Refactor arquitectonico\n\n"
            "Prompt:\n"
            "  El backend esta en un solo archivo. Refactorizalo siguiendo una\n"
            "  arquitectura en capas: api / services / repositories / db / storage.\n"
            "  Cada capa solo puede importar la inmediatamente inferior.\n"
            "  No rompas los tests que ya existen."
        ),
        bullets([
            "<b>Resultado</b>: la IA propuso la estructura de directorios, los contratos de cada capa (interfaces implicitas via duck typing), el patron Unit of Work con context manager para transacciones ACID y la inyeccion de dependencias via <i>lru_cache</i> en <i>deps.py</i>. El refactor se completo sin romper ninguna ruta existente.",
            "<b>Valoracion</b>: acierto. La propuesta de Unit of Work fue espontanea (no estaba en el prompt) y resulto critica para la transaccionalidad.",
            "<b>Aprendizaje</b>: especificar restricciones de importacion en el prompt obliga a la IA a razonar sobre dependencias y genera arquitecturas mas limpias que pedir simplemente 'modulariza'.",
        ]),
        subsection("Prompt 3 — Generacion de la suite de tests"),
        code(
            "Herramienta: Claude Code\n"
            "Fase: Testing\n\n"
            "Prompt:\n"
            "  Crea tests para el backend. No uses MagicMock generico: cada doble\n"
            "  debe implementar la misma interfaz que la clase real. Los tests de\n"
            "  API deben usar dependency_overrides de FastAPI, no parchear imports."
        ),
        bullets([
            "<b>Resultado</b>: la IA genero 18 archivos de test (12 unit + 6 api) con fakes que implementan los contratos reales de <i>DatabaseSession</i> y <i>ObjectStorage</i>. Tres tests fallaron en la primera ejecucion por asunciones incorrectas sobre el comportamiento del codigo.",
            "<b>Valoracion</b>: iteracion necesaria. El codigo base tuvo que ajustarse en dos puntos menores (firma de metodos) para que los contratos fueran coherentes.",
            "<b>Aprendizaje</b>: la restriccion explicita de 'no MagicMock' en el prompt es imprescindible; sin ella la IA genera tests que pasan con cualquier implementacion, incluyendo las rotas.",
        ]),
        subsection("Prompt 4 — Integracion del modelo de triaje"),
        code(
            "Herramienta: Claude Code\n"
            "Fase: Integracion de modelos\n\n"
            "Prompt:\n"
            "  El dashboard muestra 'Triaje IA: fallback heuristico' aunque el\n"
            "  archivo triage_model.joblib existe en /models. Encuentra por que\n"
            "  el backend no lo carga y arreglalo sin romper los tests."
        ),
        bullets([
            "<b>Resultado</b>: la IA detecto que el archivo <i>triage_model.py</i> habia desaparecido en un merge (se verifico con <i>git log --all --diff-filter=AD</i>). Lo recupero de un commit anterior, lo reintegro con el patron singleton thread-safe y anadio el bloque <i>services.triage_model</i> al schema <i>PlatformMetrics</i>, que era el motivo por el que el dashboard no recibia el estado real del modelo.",
            "<b>Valoracion</b>: acierto. La IA uso git para diagnosticar la causa raiz en lugar de suponer un error de configuracion.",
            "<b>Aprendizaje</b>: describir el sintoma observable (lo que muestra el dashboard) en lugar del problema tecnico subyacente permite a la IA rastrear la cadena causal completa.",
        ]),
        subsection("Prompt 5 — Eliminacion de componentes no utilizados"),
        code(
            "Herramienta: Claude Code\n"
            "Fase: Limpieza de infraestructura\n\n"
            "Prompt:\n"
            "  Quita Prometheus y Grafana del proyecto. Desinstalalos, quita el\n"
            "  codigo y asegurate de no romper nada por el camino."
        ),
        bullets([
            "<b>Resultado</b>: la IA mapeo todas las referencias (12 archivos), elimino los contadores de <i>app/core/metrics.py</i> de los tres servicios que los importaban, borro el router <i>prometheus.py</i>, limpio el <i>docker-compose.yml</i>, elimino las carpetas de infraestructura, paro y borro los contenedores huerfanos y sus volumenes, y valido con <i>docker compose config</i> antes de dar la tarea por completada.",
            "<b>Valoracion</b>: acierto. El orden de operaciones fue correcto: primero el codigo, luego la infraestructura, finalmente la validacion.",
            "<b>Aprendizaje</b>: para tareas de eliminacion es mas seguro dejar que la IA mapee las dependencias antes de borrar; un borrado manual sin ese mapa habria dejado imports rotos.",
        ]),
        subsection("Prompt 6 — Generacion de la memoria tecnica"),
        code(
            "Herramienta: Claude Code\n"
            "Fase: Documentacion\n\n"
            "Prompt:\n"
            "  Quiero que hagas la memoria del proyecto. Haz TODA LA MEMORIA menos\n"
            "  la parte de los prompts de la IA, esa dejala en TODO. Quiero un\n"
            "  informe completo, dimeel indice que propones y te digo. Luego\n"
            "  hazlo en PDF, que se vea profesional y bien cuidado."
        ),
        bullets([
            "<b>Resultado</b>: la IA propuso un indice de 16 capitulos + 3 anexos, lo valido con el equipo y genero un script Python con reportlab que produce un PDF de 43 paginas con portada, cabeceras, tablas, bloques de codigo y paleta de colores corporativa. Incorporo las metricas reales del CNN (leidas de <i>models/radiology_cnn_metrics.json</i>) y del Random Forest.",
            "<b>Valoracion</b>: acierto con una iteracion. La primera version incluia metricas del CNN como TODO (la IA no sabia que el modelo ya estaba entrenado); tras indicar que el compañero lo habia entrenado y subido, la IA leyo el JSON de metricas y completo la seccion.",
            "<b>Aprendizaje</b>: la IA no conoce el estado real del repositorio a menos que lo explore activamente; conviene indicar explicitamente que artefactos ya existen antes de pedir documentacion.",
        ]),
        section("13.3", "Casos donde la IA acerto"),
        bullets([
            "<b>Auditoria inicial del repositorio</b>: identificacion precisa de puntos debiles (monolito en un solo archivo, ausencia de tests, baseline disfrazado de modelo entrenado).",
            "<b>Diseno transaccional</b>: propuesta espontanea del patron Unit of Work al detectar inconsistencia entre operaciones de escritura separadas en distintas conexiones.",
            "<b>Carga perezosa y thread-safe del Random Forest</b>: singleton con <i>threading.Lock</i> que carga <i>triage_model.joblib</i> bajo demanda y respeta la concurrencia de FastAPI sin requerir estado global mutable.",
            "<b>Dobles de tests que respetan contratos reales</b>: rechazo explicito de MagicMock generico en favor de fakes que implementan la interfaz.",
            "<b>Coherencia estilistica entre modulos</b>: aplicacion uniforme de patrones (config tipada, logging JSON, app factory) en backend, dashboard y pipeline.",
            "<b>Deteccion de contradicciones documentales</b>: identificacion de inconsistencias entre README y memoria que un revisor exigente habria penalizado.",
        ]),
        section("13.4", "Casos donde hubo que corregir o iterar"),
        bullets([
            "<b>Tests iniciales con asunciones incorrectas</b>: en la primera generacion, tres tests fallaron por suposiciones de la IA sobre el comportamiento del codigo. Se reescribieron los tests para reflejar el comportamiento real, no el esperado, sin modificar la logica de produccion.",
            "<b>Sobre-ingenieria espontanea</b>: la IA tendia a introducir middlewares, decoradores o abstracciones no justificadas. Cada propuesta de este tipo se rechazo y se exigio simplicidad.",
            "<b>Friccion entre response_model y dict literal</b>: una primera version de schemas Pydantic con alias <i>class</i> generaba conflictos al wirearlos como response_model. Se opto por aplicar response_model selectivamente.",
            "<b>Schemas Pydantic desalineados con la respuesta real</b>: una primera version del schema <i>PlatformMetrics</i> no incluia el bloque <i>services.triage_model</i>, lo que provocaba que el dashboard cayese a la rama de fallback. Se detecto al ver el dashboard mostrar <i>Triaje IA: fallback heuristico</i> con el modelo cargado.",
            "<b>Templates obsoletos tras migracion a blueprints</b>: la IA detecto referencias a <i>url_for('logout')</i> en lugar de <i>url_for('auth.logout')</i> y propuso corregir los templates antes que retroceder.",
        ]),
        section("13.5", "Reflexion critica sobre el uso de IA"),
        p(
            "El uso de IA ha tenido un impacto sustancial en velocidad de implementacion y "
            "calidad estilistica del codigo, pero <b>determinadas tareas se mantuvieron "
            "deliberadamente en el ambito humano</b>:"
        ),
        bullets([
            "<b>Definicion de la arquitectura global</b>: la eleccion de capas, patrones y separacion de responsabilidades respondio a requisitos reales del enunciado, no se delego.",
            "<b>Criterios clinicos de alertas</b>: los thresholds (confianza &lt; 0.55, deteccion COVID-19, banderas de calidad) son decisiones humanas con justificacion clinica.",
            "<b>Validacion clinica</b>: ningun modelo se considera apto para uso real sin revision medica.",
            "<b>Eleccion de stack tecnologico</b>: la decision PostgreSQL + MinIO + Spark fue del equipo; la IA documento los pros y contras.",
        ]),
        p(
            "<b>Riesgos detectados</b>: la IA tiende a la sobre-ingenieria sin control "
            "humano. Tambien puede ocultar errores sutiles si no se acompana de tests. En "
            "este proyecto los tests han funcionado como red de seguridad y han detectado "
            "varios fallos en la primera ejecucion."
        ),
        section("13.6", "Estimacion del impacto en productividad"),
        p(
            "El trabajo de consolidacion del proyecto (refactor a arquitectura en capas, "
            "creacion de la suite de tests, integracion del modelo de triaje, configuracion "
            "de CI y redaccion documental) se ha realizado en aproximadamente "
            "<b>5-7 horas efectivas</b> de trabajo asistido por IA. Una estimacion "
            "conservadora del mismo trabajo manual (incluyendo investigacion de mejores "
            "practicas, escritura de tests y depuracion de la integracion entre servicios) "
            "se situaria entre 4 y 6 dias-persona. El factor de aceleracion estimado es del "
            "orden de <b>6 a 10x</b>."
        ),
        p(
            "Mas alla del ahorro de tiempo, el principal valor anadido fue la "
            "<b>coherencia estilistica entre modulos</b>: aplicar el mismo patron "
            "(config tipada, logging JSON, app factory, fakes con contrato) en backend, "
            "dashboard y pipeline habria sido tedioso manualmente y propenso a divergencias."
        ),
        PageBreak(),
    ]
    return out


def build_ch14_reflection() -> list:
    out: list = [
        chapter(14, "Reflexion critica"),
        section("14.1", "Limitaciones del sistema actual"),
        bullets([
            "<b>CNN entrenado con dataset publico</b>: el ResNet18 alcanza 93.94 % de accuracy sobre test, pero el dataset proviene de fuentes publicas (no del propio hospital) y solo se han ejecutado 5 epochs; no constituye un modelo validado clinicamente.",
            "<b>Dataset radiografico no incluido</b>: el repositorio no contiene imagenes; se requiere descarga externa para entrenamiento (COVID-19 Radiography Database u otro).",
            "<b>Triaje con dataset sintetico</b>: el modelo se entrena sobre datos generados por reglas; un despliegue real requiere reentrenamiento con datos hospitalarios anonimizados.",
            "<b>Autenticacion local</b>: usuario/contrasena con hashes Werkzeug; sin integracion con SSO/LDAP/OIDC corporativo.",
            "<b>Sin HTTPS</b>: el prototipo expone HTTP plano; un despliegue real requiere reverse proxy con certificado de CA reconocida.",
            "<b>Sin cifrado en reposo</b>: PostgreSQL y MinIO operan sin encriptacion de disco ni de objetos.",
            "<b>Sin auditoria detallada</b>: se registran eventos de calidad pero no acciones individuales de usuarios.",
            "<b>Sin scheduler</b>: el pipeline se ejecuta on-demand; no hay disparo automatico ante nuevos ficheros.",
            "<b>Sin alta disponibilidad</b>: una sola instancia de cada servicio; no hay replicacion ni failover.",
            "<b>Solo procesamiento batch</b>: el pipeline procesa lotes; no hay ingesta streaming.",
        ]),
        section("14.2", "Posibles mejoras"),
        bullets([
            "<b>Reentrenar el CNN con mas epochs y data augmentation extendida</b>: introducir scheduling del learning rate, mixup/cutmix y validacion cruzada para reducir la fluctuacion observada en la curva de validacion.",
            "<b>Caching de inferencia</b>: deduplicacion por checksum de imagen para evitar reprocesar la misma radiografia.",
            "<b>SSO corporativo</b>: migrar la autenticacion local a OAuth2 / OIDC con Keycloak o proveedor cloud.",
            "<b>Cifrado SSE-S3 en MinIO</b> con clave gestionada externamente (KMS).",
            "<b>Scheduler de pipeline</b>: Airflow o Prefect para disparar ingesta ante nuevos ficheros o por cron.",
            "<b>Trazabilidad distribuida</b>: OpenTelemetry para seguir una peticion entre dashboard, backend y pipeline.",
            "<b>Observabilidad externa</b>: el backend ya expone un snapshot agregado en <i>/metrics</i> consumido por el dashboard; un despliegue real anadiria un stack de metricas (Prometheus + Grafana, OpenTelemetry o equivalente) y agregacion de logs (ELK, Loki).",
            "<b>Tests de integracion end-to-end</b>: docker-compose dedicado a tests que levante PostgreSQL y MinIO efimeros antes de pytest.",
            "<b>Auditoria de seguridad OWASP ASVS</b>: rate limiting en /predict y /triage, validacion de Content-Length antes de leer cuerpo, revision de headers de seguridad.",
            "<b>Mejora de la clase <i>high</i> del triaje</b>: el recall 0.58 sugiere que las fronteras entre medium y high requieren reentrenamiento con datos reales y reajuste de los thresholds del MEWS/NEWS2 utilizados como base de etiquetado.",
            "<b>Internacionalizacion del dashboard</b>: actualmente solo en castellano; preparar i18n para catalan e ingles.",
        ]),
        section("14.3", "Viabilidad de aplicacion en un entorno real"),
        p(
            "Para llevar el sistema a produccion en un hospital real seria necesario, "
            "ademas de las mejoras tecnicas anteriores:"
        ),
        bullets([
            "<b>Validacion clinica del modelo CNN</b> por un equipo medico con dataset representativo.",
            "<b>Certificacion como producto sanitario</b>: clasificacion CE bajo el Reglamento (UE) 2017/745 (MDR) o equivalente FDA segun jurisdiccion. Probablemente clase IIa.",
            "<b>Auditoria de seguridad y privacidad</b> conforme al GDPR (Reglamento (UE) 2016/679) y normativa espanola de proteccion de datos sanitarios.",
            "<b>Acuerdo de tratamiento de datos</b> firmado con cualquier proveedor cloud que aloje datos clinicos.",
            "<b>Plan de respuesta ante incidentes</b> con notificacion en menos de 72 horas a la AEPD.",
            "<b>Plan de continuidad de negocio</b>: backups cifrados, plan de recuperacion ante desastres, replicacion en region secundaria.",
            "<b>Procedimientos operativos</b>: documentacion de altas/bajas de usuarios, gestion de claves, rotacion de contrasenas, revisiones periodicas de acceso.",
            "<b>Formacion del personal sanitario</b>: el sistema es una herramienta de apoyo, no un sustituto del criterio clinico.",
        ]),
        PageBreak(),
    ]
    return out


def build_ch15_ethics() -> list:
    out: list = [
        chapter(15, "Consideraciones eticas y legales"),
        section("15.1", "Sesgos en datos y modelos"),
        p(
            "Los modelos de clasificacion de imagenes medicas son particularmente "
            "vulnerables a sesgos cuando el conjunto de entrenamiento no representa la "
            "diversidad clinica real de la poblacion objetivo. Un modelo entrenado "
            "exclusivamente con radiografias procedentes de un unico hospital, un unico "
            "modelo de equipo radiologico o un rango demografico estrecho puede exhibir un "
            "rendimiento significativamente inferior cuando se aplica fuera de ese contexto."
        ),
        subsection("Riesgos especificos identificados"),
        bullets([
            "<b>Sesgo de procedencia</b>: dataset dominado por un solo hospital, pais o region.",
            "<b>Sesgo demografico</b>: distribucion no equilibrada por edad, sexo, etnia o nivel socioeconomico.",
            "<b>Sesgo de equipo radiologico</b>: imagenes capturadas con un fabricante o modelo concreto pueden enganar al modelo (aprende a clasificar por la marca de agua o caracteristicas del equipo, no por la patologia).",
            "<b>Sesgo temporal</b>: predominancia de imagenes de un periodo concreto (por ejemplo, primera ola de COVID-19) con caracteristicas tecnicas distintas a periodos posteriores.",
            "<b>Sesgo de etiquetado</b>: clasificaciones realizadas por un solo radiologo, sin doble lectura ni consenso clinico.",
        ]),
        subsection("Medidas propuestas"),
        bullets([
            "<b>Transparencia del dataset</b>: documentar publicamente la composicion (origen, equipos, periodos, demografia).",
            "<b>Particion por paciente</b>: separar train/val/test por paciente y no por imagen, para evitar fuga entre conjuntos.",
            "<b>Metricas estratificadas</b>: calcular precision, recall y F1 por subgrupo demografico y reportar la peor metrica como referencia.",
            "<b>Auditoria de la matriz de confusion</b>: especial atencion a falsos negativos en patologias contagiosas.",
            "<b>Monitorizacion continua</b>: revisiones periodicas del rendimiento en produccion con muestras representativas.",
        ]),
        section("15.2", "Riesgos en la decision automatizada"),
        p(
            "El sistema <b>no esta autorizado a tomar decisiones clinicas autonomas</b>. "
            "Su rol es de apoyo: ofrecer una clasificacion preliminar, marcar casos para "
            "revision prioritaria y reducir carga administrativa. La responsabilidad final "
            "del diagnostico recae siempre en el personal sanitario."
        ),
        subsection("Riesgos clinicos especificos"),
        bullets([
            "<b>Falso negativo de COVID-19</b>: retraso en aislamiento, aumento del riesgo de contagio intrahospitalario. Es el error de mayor gravedad y debe ser objetivo explicito de minimizacion.",
            "<b>Falso negativo de neumonia</b>: retraso del tratamiento antibiotico y posible progresion clinica.",
            "<b>Falso positivo</b>: ansiedad del paciente, pruebas confirmatorias innecesarias, sobrecarga del circuito de revision.",
            "<b>Automation bias</b>: tendencia humana a confiar mas en una recomendacion automatica de lo que la evidencia justifica.",
            "<b>Falso negativo en triaje critico</b>: paciente grave clasificado como menor riesgo; mitigado por el alto recall (0.92) en la clase <i>critical</i> y por la revision humana obligatoria.",
        ]),
        subsection("Mitigaciones implementadas"),
        bullets([
            "Cada prediccion se acompana de una <b>nota clinica</b> explicita: <i>resultado de apoyo, no diagnostico</i>.",
            "Las predicciones con <b>confianza inferior a 0.55</b> generan un evento de baja confianza automaticamente.",
            "Toda prediccion <b>COVID-19</b> genera una alerta de severidad alta independientemente de la confianza.",
            "Las banderas de calidad de imagen (oscuridad, sobrexposicion, bajo contraste) se reportan al usuario para permitir repetir el estudio.",
            "El <b>historico completo</b> de estudios y triajes queda persistido para auditoria a posteriori.",
        ]),
        section("15.3", "Privacidad y proteccion de datos (RGPD)"),
        p(
            "Las imagenes medicas y los datos clinicos son <b>categorias especiales de "
            "datos personales</b> segun el articulo 9 del RGPD y la normativa espanola de "
            "proteccion de datos sanitarios. Este prototipo no contiene mecanismos "
            "suficientes para tratar datos reales de pacientes y debe usarse "
            "<b>exclusivamente con datos anonimizados, sinteticos o simulados</b>."
        ),
        subsection("Carencias actuales del prototipo"),
        bullets([
            "No hay cifrado en reposo de los objetos en MinIO ni de las filas en PostgreSQL.",
            "No hay auditoria detallada de accesos individuales por usuario.",
            "No hay gestion de consentimientos del paciente.",
            "Las copias de seguridad no estan automatizadas ni cifradas.",
            "No hay procedimiento documentado de borrado a peticion del interesado (derecho al olvido).",
        ]),
        subsection("Medidas necesarias en un entorno real"),
        bullets([
            "<b>Control de acceso por roles (RBAC)</b> con principio de minimo privilegio.",
            "<b>Cifrado en reposo</b>: PostgreSQL con disco cifrado (LUKS, BitLocker), MinIO con SSE-S3 o SSE-KMS.",
            "<b>Cifrado en transito</b>: TLS obligatorio en todos los flujos, incluyendo conexiones internas entre servicios.",
            "<b>Registro de auditoria</b>: cada acceso a un estudio queda registrado y es exportable para inspeccion.",
            "<b>Politica de retencion</b>: borrado seguro automatico al expirar el periodo legal de conservacion.",
            "<b>Minimizacion de datos</b>: almacenar solo lo estrictamente necesario para el proceso clinico.",
            "<b>Anonimizacion</b>: identificadores irreversiblemente anonimizados cuando se exporten datos para investigacion.",
            "<b>Acuerdo de tratamiento</b>: firma con cualquier proveedor cloud que aloje datos.",
            "<b>Plan de respuesta ante incidentes</b>: notificacion en menos de 72 horas a la AEPD ante cualquier brecha.",
        ]),
        section("15.4", "Responsabilidad clinica"),
        p(
            "La interpretacion final de cualquier estudio o triaje corresponde al personal "
            "sanitario. El sistema debe mostrar de forma visible explicaciones, niveles de "
            "incertidumbre, banderas de calidad y notas clinicas para evitar que los "
            "usuarios confundan una prediccion con un diagnostico definitivo. La "
            "trazabilidad se apoya en el registro completo de estudios y eventos en "
            "PostgreSQL y los informes JSON persistentes en MinIO."
        ),
        section("15.5", "Limitaciones legales del prototipo"),
        p(
            "El sistema descrito en esta memoria es un <b>prototipo academico</b>. El CNN "
            "ResNet18 alcanza un 93.94 % de accuracy sobre el conjunto de test publico, pero "
            "no constituye un modelo validado clinicamente: requiere validacion externa con "
            "datos hospitalarios reales, evaluacion formal por un equipo medico y, en su "
            "caso, certificacion regulatoria como producto sanitario antes de cualquier uso "
            "clinico real. "
            "El triaje opera con un modelo entrenado sobre datos sinteticos inspirados en "
            "MEWS/NEWS2; un despliegue real requiere reentrenamiento con datos "
            "hospitalarios y validacion frente a los protocolos vigentes."
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
        section("16.1", "Cumplimiento del enunciado"),
        table(
            ["Requisito del enunciado", "Estado"],
            [
                ["Modelo de IA justificado", "<b>Cumplido</b> (RF triaje + CNN ResNet18)"],
                ["Procesamiento Big Data con framework distribuido", "<b>Cumplido</b> (Spark)"],
                ["Dos tipos de almacenamiento combinados", "<b>Cumplido</b> (PostgreSQL + MinIO)"],
                ["Pipeline ingesta / limpieza / transformacion / analisis", "<b>Cumplido</b>"],
                ["Automatizacion de procesos", "<b>Cumplido</b> (alertas, informes, bucket)"],
                ["Visualizacion y comunicacion (dashboard)", "<b>Cumplido</b> (Flask con auth)"],
                ["Containerizacion con docker-compose", "<b>Cumplido</b> (1 solo comando)"],
                ["Calidad de datos y logging", "<b>Cumplido</b>"],
                ["Vibe Coding con herramienta IA", "<b>Cumplido</b> (Claude Code + Codex)"],
                ["Metodologia SDD", "<b>Cumplido</b> (docs/SDD.md)"],
                ["Clasificacion triple radiografias", "<b>Cumplido</b> (Sana / Neumonia / COVID-19)"],
                ["Matriz de confusion analizada", "<b>Cumplido</b> (triaje y CNN sobre val y test)"],
                ["Reflexion clinica del modelo", "<b>Cumplido</b>"],
                ["Consideraciones eticas y legales", "<b>Cumplido</b>"],
                ["Memoria tecnica con apartados obligatorios", "<b>Cumplido</b> (este documento)"],
                ["Diario de desarrollo con IA", "<b>Parcial</b> (prompts pendientes)"],
            ],
            col_widths=[10.5 * cm, 6.0 * cm],
        ),
        section("16.2", "Valor aportado"),
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


def build_annex_b() -> list:
    out: list = [
        chapter(0, "Anexo B. Variables de entorno"),
        p(
            "Las variables se cargan desde el archivo <i>.env</i>, que se construye a "
            "partir de <i>.env.example</i>. El archivo <i>.env</i> nunca se sube al "
            "repositorio."
        ),
        subsection("PostgreSQL"),
        code(
            "POSTGRES_USER=hospital_user\n"
            "POSTGRES_PASSWORD=<password fuerte>\n"
            "POSTGRES_DB=hospital_db\n"
        ),
        subsection("MinIO"),
        code(
            "MINIO_ROOT_USER=hospital_minio_admin\n"
            "MINIO_ROOT_PASSWORD=<password fuerte>\n"
            "MINIO_REGION=us-east-1\n"
            "MINIO_BUCKET_NAME=hospital-data\n"
            "MINIO_AUTO_CREATE_BUCKET=true\n"
            "MINIO_CONSOLE_URL=http://localhost:9001\n"
        ),
        subsection("Autenticacion del dashboard"),
        code(
            "SECRET_KEY=<clave aleatoria de al menos 32 bytes>\n"
            "SESSION_COOKIE_SECURE=false\n"
            "ADMIN_USERNAME=admin\n"
            "ADMIN_PASSWORD_HASH=<hash Werkzeug PBKDF2-SHA256>\n"
            "USER_USERNAME=doctor\n"
            "USER_PASSWORD_HASH=<hash Werkzeug PBKDF2-SHA256>\n"
        ),
        subsection("Pipeline"),
        code(
            "PIPELINE_INPUT_PATH=/data/incoming/radiology_studies.csv\n"
            "PIPELINE_OUTPUT_PATH=/data/processed/radiology_clean\n"
        ),
        subsection("Entrenamiento CNN"),
        code(
            "TRAINING_EPOCHS=5\n"
            "TRAINING_BATCH_SIZE=16\n"
            "TRAINING_LEARNING_RATE=0.0005\n"
            "TRAINING_PRETRAINED=false\n"
        ),
        subsection("Entrenamiento triaje"),
        code(
            "TRIAGE_SAMPLES=8000\n"
            "TRIAGE_N_ESTIMATORS=400\n"
            "TRIAGE_MAX_DEPTH=12\n"
            "TRIAGE_NOISE_RATE=0.06\n"
            "TRIAGE_RANDOM_STATE=42\n"
        ),
        PageBreak(),
    ]
    return out


def build_annex_c() -> list:
    out: list = [
        chapter(0, "Anexo C. Comandos de ejecucion"),
        subsection("Arranque basico"),
        code(
            "cp .env.example .env             # Copiar variables\n"
            "# Editar .env con credenciales reales\n"
            "docker compose up -d              # Levantar entorno\n"
            "docker compose ps                 # Ver estado\n"
            "docker compose logs -f            # Seguir logs\n"
            "docker compose down               # Parar entorno\n"
            "docker compose down -v            # Parar y borrar volumenes\n"
        ),
        subsection("Ejecutar el pipeline Big Data"),
        code(
            "docker compose --profile pipeline up --build pipeline\n"
        ),
        subsection("Entrenar el modelo CNN de radiografias"),
        code(
            "# Requiere dataset en data/radiology_dataset/{train,val}/{Sana,Neumonia,COVID-19}/\n"
            "docker compose --profile training run --rm model-trainer\n"
        ),
        subsection("Entrenar el modelo de triaje"),
        code(
            "docker compose --profile triage-training run --rm triage-trainer\n"
        ),
        subsection("Ejecucion de tests locales"),
        code(
            "# Backend\n"
            "cd backend\n"
            "pip install -r requirements-dev.txt\n"
            "pytest --cov=app --cov-report=term\n"
            "\n"
            "# Dashboard\n"
            "cd ../dashboard\n"
            "pip install -r requirements-dev.txt\n"
            "pytest --cov=app --cov-report=term\n"
        ),
        subsection("Pruebas rapidas de API"),
        code(
            "# Salud del backend\n"
            "curl http://localhost:8000/health\n"
            "\n"
            "# Triaje desde PowerShell\n"
            'Invoke-RestMethod -Method Post -Uri "http://localhost:8000/triage" `\n'
            '  -ContentType "application/json" `\n'
            "  -Body \\'{\"symptoms\":[\"fever\",\"shortness of breath\"],\"vitals\":{\"heart_rate\":125,\"oxygen_saturation\":90,\"systolic_bp\":95}}\\'\n"
            "\n"
            "# Interfaces web\n"
            "# http://localhost:8501       Dashboard\n"
            "# http://localhost:8000/docs  Swagger UI\n"
            "# http://localhost:9001       Consola MinIO\n"
        ),
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
    story += build_annex_b()
    story += build_annex_c()

    doc.build(flatten(story))
    print(f"PDF generado en: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
