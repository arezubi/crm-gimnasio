from db.consultas import obtener_estado_cuota
from datetime import date

from db.db import insertar_factura

def facturar_cuota(cursor, id_cuota, fecha_factura=None):
    """
    Función para generar facturas para una cuota específica.

    Parámetros:
    cursor: Objeto cursor de la base de datos.
    id_cuota: ID de la cuota para la cual se generarán las facturas.
    fecha_factura: Fecha de la factura (opcional, por defecto es hoy).

    Retorna:
    True, False, 'duplicado', 'no pagada' o 'no existe'
    """

    estado = obtener_estado_cuota(cursor, id_cuota)

    if estado is None:
        print("No se encontró la cuota especificada.")
        return "no existe"
    
    id_alumno, pagada = estado
    if not pagada:
        print("La cuota no ha sido pagada. No se puede generar la factura.")
        return "no pagada"
    
    if fecha_factura is None:
        fecha_factura = date.today().isoformat()

    return insertar_factura(cursor, id_cuota, id_alumno, fecha_factura)


def numero_factura(id_factura, fecha_factura):
    """id 3 del año 2026 -> 'F-2026-0003'"""
    return f"F-{fecha_factura[:4]}-{id_factura:04d}"