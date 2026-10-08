import pandas as pd
from datetime import date
def calcular_ingresos_por_mes(cursor):

    df = pd.read_sql_query("""

        SELECT cuotas.mes_cuota, cuotas.importe 
        FROM cuotas
        WHERE cuotas.pago_realizado =1
    """, cursor.connection)

    ingresos_por_mes = df.groupby("mes_cuota")["importe"].sum()
    return ingresos_por_mes

def calcular_ingresos_por_anio(cursor):

    df = pd.read_sql_query("""
        SELECT cuotas.mes_cuota, cuotas.importe
        FROM cuotas
        WHERE cuotas.pago_realizado =1
    """, cursor.connection)

    df["anio"] = pd.to_datetime(df["mes_cuota"]).dt.year

    ingresos_por_anio = df.groupby("anio")["importe"].sum()
    return ingresos_por_anio

def actividad_mas_usada(cursor):
    df = pd.read_sql_query("""
        SELECT actividades.nombre, COUNT(*) as num_alumnos
        FROM inscripciones
        JOIN actividades ON inscripciones.id_actividades = actividades.id
        JOIN  alumno ON inscripciones.id_alumno = alumno.id
        WHERE alumno.activo = 1 
        GROUP BY actividades.nombre
        
    """, cursor.connection)
    df_ordenado = df.sort_values(by="num_alumnos", ascending=False)
    return df_ordenado

def alumnos_nuevos_por_mes(cursor):
    df = pd.read_sql_query("SELECT fecha_alta FROM alumno", cursor.connection)
    df["mes_alta"] = pd.to_datetime(df["fecha_alta"]).dt.to_period("M")
    resultado = df.groupby("mes_alta").size()
    return resultado

def alumnos_nuevos_por_anio(cursor):
    df = pd.read_sql_query("SELECT fecha_alta FROM alumno", cursor.connection)
    df["anio_alta"] = pd.to_datetime(df["fecha_alta"]).dt.year
    resultado = df.groupby("anio_alta").size()
    return resultado

def numero_pagos_pendientes(cursor):
    cursor.execute("SELECT COUNT(*) FROM cuotas WHERE pago_realizado = 0")
    resultado = cursor.fetchone()
    return resultado[0]

def alumnos_activos(cursor):
    cursor.execute("SELECT COUNT(*) FROM alumno WHERE activo = 1")
    return cursor.fetchone()[0]

def ingresos_mes_actual(cursor):
    mes = date.today().strftime("%Y-%m-01")
    cursor.execute("""
        SELECT COALESCE(SUM(importe),0) 
        FROM cuotas 
        WHERE pago_realizado =1 
        AND mes_cuota = ?
    """,(mes,))
    return cursor.fetchone()[0]

def alumnos_nuevos_mes_actual(cursor):
    mes = date.today().strftime("%Y-%m")
    cursor.execute(""" 
        SELECT COUNT(*) 
        FROM alumno 
        WHERE strftime('%Y-%m', fecha_alta) = ?
    """,(mes,))
    return cursor.fetchone()[0]

def nombre_actividad_mas_usada(cursor):
    df = actividad_mas_usada(cursor)
    if df.empty:
        return "—"
    return df.iloc[0]["nombre"]