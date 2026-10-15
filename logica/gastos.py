from db.db import actualizar_gasto, insertar_gastos
CATEGORIAS_GASTOS = ["Alquiler", "Suministros", "Sueldos", "Material", "Mantenimiento", "Otros"]


def comprobar_gasto(categoria, importe):
    """Reglas de un gasto: importe positivo y categoría de la lista.
    Devuelve None si todo está bien, o el texto del error."""
    if importe <= 0:
        return "importe no válido"
    if categoria not in CATEGORIAS_GASTOS:
        return "categoria no válida"
    return None


def registrar_gasto(cursor, fecha, concepto, categoria, importe):
    """Registra un gasto nuevo.
    Devuelve True, False, 'importe no válido' o 'categoria no válida'."""
    error = comprobar_gasto(categoria, importe)
    if error:
        return error
    return insertar_gastos(cursor, fecha, concepto, categoria, importe)


def modificar_gasto(cursor, id_gasto, fecha, concepto, categoria, importe):
    """Cambia un gasto existente con las mismas reglas que el alta.
    Devuelve True, False, 'no existe', 'importe no válido' o 'categoria no válida'."""
    error = comprobar_gasto(categoria, importe)
    if error:
        return error
    return actualizar_gasto(cursor, id_gasto, fecha, concepto, categoria, importe)
