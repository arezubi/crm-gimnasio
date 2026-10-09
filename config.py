from pathlib import Path

# Rutas absolutas a partir de la carpeta del proyecto, para que la app funcione
# aunque se ejecute desde otra carpeta.
CARPETA_BASE = Path(__file__).resolve().parent

RUTA_BD = CARPETA_BASE / "gimnasio.db"
RUTA_ESTILO = CARPETA_BASE / "resources" / "estilo.qss"
RUTA_LOGO = CARPETA_BASE / "assets" / "Logo.svg"
CARPETA_FACTURAS = CARPETA_BASE / "facturas"

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
    carpeta_recursos = (CARPETA_BASE / "resources").as_posix()
    qss = RUTA_ESTILO.read_text(encoding="utf-8")
    return qss.replace('url("resources/', f'url("{carpeta_recursos}/')
