import platform

URL = "https://prod2.seace.gob.pe/seacebus-uiwd-pub/buscadorPublico/buscadorPublico.xhtml"
ANIOS = [2026]
TIMEOUT = 30
OBJETO_CONTRATACION = "Servicio"
LIMITE_PAGINAS = 10
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzyZV2KWBHaqh_bb3fIQel2w_sAojIcD87T5-5wUaN1Bdrog393lDNjhd8ayA2hxuV5/exec"

# ===================================================================

LIMITE_REGISTROS_POR_PAGINA = None
FILTRO_PALABRAS_CLAVE_HABILITADO = True # Deshabilitar para todos los filtros
HABILITAR_ESCANEO_PDF = True

# ===================================================================

#Filtros
FILTRO_ENTIDAD_HABILITADO = False
FILTRO_ENTIDAD_TIPO = "ruc" # Sigla / Ruc / Nombre
FILTRO_ENTIDAD_SIGLA = "MINEDU"
FILTRO_ENTIDAD_RUC = "20131370998"
FILTRO_ENTIDAD_NOMBRE = ""

FILTRO_NOMENCLATURA_HABILITADO = False
FILTRO_NOMENCLATURA = "CONV-PROC-4-2026-CI-UE-PMSAJ-1"

# ===================================================================

# SO

SISTEMA_OPERATIVO = platform.system()

import os

# Si estamos ejecutando dentro de GitHub Actions, el path base será el del repositorio actual
if os.getenv("GITHUB_ACTIONS_ENV") == "true" or os.getenv("GITHUB_ACTIONS") == "true":
    REPO_PATH = os.getcwd()
else:
    REPO_PATH = os.getcwd()

# ===================================================================

# ===================================================================

PALABRAS_CLAVE = [
    "Desarrollo de aplicaciones",
    "Pruebas de software",
    "QA",
    "Testing de aplicaciones",
    "Seguridad de aplicaciones",
    "Servicio de nube",
    "CLOUD",
    "Servicio de Data analitica",
    "Servicio de Data analítica",
    "DATA",
    "Analitica",
    "soporte de desarrollos",
    "Soporte y Mantenimiento",
    "Soporte administrativo",
    "Requerimientos",
    # "Soporte",
    # "Mantenimiento",
    # "Desarrollo",
    "Ciberseguridad",
    "Cyberseguridad",
    "Security",
    "Nube",
    "Movil",
    "Moviles",
    "Software",
    "Gestión de accesos",
    "Mejora continua",
    "Monitoreo de bases de datos",
    "Base de datos",
    "Capacitaciones",
    #"Normativo",
    "Ethical Hacking",
    "Ciberinteligencia",
    "Cibervigilancia",
    "Protección de marca",
    "Análisis de vulnerabilidades",
    "Pentesting",
    "Cybersoc"
]