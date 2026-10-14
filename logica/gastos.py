from db.db import insertar_gastos
CATEGORIAS_GASTOS = ["Alquiler", "Suministros", "Sueldos", "Material", "Mantenimiento", "Otros"]

def registrar_gasto(cursor, fecha, concepto, categoria, importe):
    """Registra un gasto si el importe es positivo y la categoría es una de las permitidas
    Devuelve True, False, 'importe no válido' o 'categoría no válida'."""
    if importe <= 0:
        return "importe no válido"
    if categoria not in CATEGORIAS_GASTOS:
        return "categoria no válida"
    return insertar_gastos(cursor, fecha, concepto, categoria, importe)
