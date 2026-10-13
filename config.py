import sys
from pathlib import Path

# Dos carpetas distintas:
# - RECURSOS: archivos que solo se leen (estilos, logo). En el .exe van empaquetados dentro.
# - DATOS: archivos que se escriben (base de datos, facturas). En el .exe van al lado del
#   ejecutable, para que no se pierdan al actualizar el programa.
if getattr(sys, "frozen", False):              # True cuando se ejecuta como .exe de PyInstaller
    CARPETA_RECURSOS = Path(sys._MEIPASS)      # la carpeta _internal
    CARPETA_DATOS = Path(sys.executable).parent
else:                                          # ejecutándolo con "python main.py"
    CARPETA_RECURSOS = Path(__file__).resolve().parent
    CARPETA_DATOS = CARPETA_RECURSOS

RUTA_BD = CARPETA_DATOS / "gimnasio.db"
CARPETA_FACTURAS = CARPETA_DATOS / "facturas"
RUTA_ESTILO = CARPETA_RECURSOS / "resources" / "estilo.qss"
RUTA_LOGO = CARPETA_RECURSOS / "assets" / "Logo.svg"

# Datos que aparecen en la cabecera de las facturas. Cámbialos por los reales del gimnasio.
DATOS_GIMNASIO = {
    "nombre": "Spartan Team",
    "cif": "B00000000",
    "direccion": "Calle Ejemplo 1, 28000 Madrid",
    "email": "info@spartanteam.es",
    "telefono": "600 000 000",
}


def leer_estilo():
    """Devuelve el QSS con las rutas de las imágenes (url("resources/...")) convertidas
    en absolutas. Qt las buscaría en la carpeta desde la que se lanza la app.
    Las comillas son necesarias: sin ellas, la "C:" de Windows rompe el QSS."""
    carpeta_recursos = (CARPETA_RECURSOS / "resources").as_posix()
    qss = RUTA_ESTILO.read_text(encoding="utf-8")
    return qss.replace('url("resources/', f'url("{carpeta_recursos}/')
