from datetime import date
from db.consultas import obtener_estado_cuota, obtener_precio_tipo_cuota
from db.db import insertar_cuota, guardar_pago

def crear_cuota_mensual(cursor, id_alumno, id_tipo_cuota, mes_cuota):
    """
    Función para crear una cuota mensual para un alumno.
    El importe se copia del precio actual del tipo de cuota, así un cambio de precio no altera las cuotas ya creadas

    Parámetros:
    cursor: Objeto cursor de la base de datos.
    id_alumno: ID del alumno para el cual se creará la cuota.
    id_tipo_cuota: ID del tipo de cuota.
    mes_cuota: Mes al que corresponde la cuota.

    Retorna:
    True, False, 'duplicado' o 'no existe'
    """
    precio = obtener_precio_tipo_cuota(cursor, id_tipo_cuota)
    if precio is None:
        return "no existe"
    return insertar_cuota(cursor, id_alumno, id_tipo_cuota, mes_cuota, precio)

def marcar_cuota_pagada(cursor, id_cuota):
    """
    Marca una cuota como pagada.

    Parámetros:
    cursor: Objeto cursor de la base de datos.
    id_cuota: ID de la cuota a marcar como pagada.

    Retorna:
    True, False, 'ya pagada' o 'no existe'
    """
    estado = obtener_estado_cuota(cursor, id_cuota)
    if estado is None:
        return "no existe"
    
    id_alumno, pagada = estado
    if pagada:
        return "ya pagada"
    fecha_pago = date.today().isoformat()  
    return guardar_pago(cursor, id_cuota, fecha_pago)