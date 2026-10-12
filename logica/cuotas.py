from datetime import date
from db.consultas import listar_alumnos_activos, obtener_estado_cuota, obtener_precio_tipo_cuota, ultimo_tipo_cuota
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

def generar_cuotas_del_mes(cursor, mes_cuota):
    """A cada alumno activo se le crea la cuota del mes con el mismo tipo que su última cuota. 
    Los que no tienen ninguna anterior se devuelven en sin_tipo para crearlas a mano. 
    Devuelve (creadas, ya_existentes, sin_tipo)."""
    creadas = 0
    ya_existentes = 0
    sin_tipo = []

    for id_alumno, nombre in listar_alumnos_activos(cursor):
        id_tipo_cuota = ultimo_tipo_cuota(cursor, id_alumno)
        if id_tipo_cuota is None:
            sin_tipo.append(nombre)
            continue 
        resultado = crear_cuota_mensual(cursor, id_alumno, id_tipo_cuota, mes_cuota)
        if resultado is True:
            creadas += 1
        elif resultado == "duplicado":
            ya_existentes += 1
        else:
            print(f"Error al crear cuota para {nombre}: {resultado}")
    return creadas, ya_existentes, sin_tipo
        