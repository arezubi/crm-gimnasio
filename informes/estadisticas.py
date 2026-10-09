import pandas as pd
from datetime import date

def calcular_ingresos_por_mes(cursor, anio=None):
    """Suma de importes pagados por mes ('YYYY-MM-01'). Si se indica anio, solo ese año."""
    df = pd.read_sql_query("""
        SELECT cuotas.mes_cuota, cuotas.importe
        FROM cuotas
        WHERE cuotas.pago_realizado =1
    """, cursor.connection)

    if anio is not None:
        df = df[df["mes_cuota"].str.startswith(str(anio))]

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

def alumnos_nuevos_por_mes(cursor, anio=None):
    """Altas por mes (índice tipo Period 'YYYY-MM'). Si se indica anio, solo ese año."""
    df = pd.read_sql_query("SELECT fecha_alta FROM alumno", cursor.connection)
    df["mes_alta"] = pd.to_datetime(df["fecha_alta"]).dt.to_period("M")
    if anio is not None:
        df = df[df["mes_alta"].dt.year == anio]
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

def anios_con_datos(cursor):
    """Años en los que hay cuotas o altas de alumnos, más el actual. Del más reciente al más antiguo."""
    cursor.execute("""
        SELECT substr(mes_cuota, 1, 4) FROM cuotas
        UNION
        SELECT substr(fecha_alta, 1, 4) FROM alumno
    """)
    anios = {int(fila[0]) for fila in cursor.fetchall() if fila[0]}
    anios.add(date.today().year)
    return sorted(anios, reverse=True)

def ingresos_ultimos_meses(cursor, num_meses=6):
    """Devuelve (meses, importes) de los últimos num_meses meses, incluido el actual.
    Los meses sin ingresos aparecen con 0."""
    hoy = date.today()
    meses = []
    anio, mes = hoy.year, hoy.month
    for _ in range(num_meses):
        meses.append(f"{anio}-{mes:02d}-01")
        mes -= 1
        if mes == 0:
            anio, mes = anio - 1, 12
    meses.reverse()

    ingresos = calcular_ingresos_por_mes(cursor)
    importes = [ingresos.get(m, 0) for m in meses]
    return meses, importes

def cuotas_pendientes_antiguas(cursor, limite=5):
    """Las cuotas sin pagar más antiguas: (alumno, mes_cuota, importe)."""
    cursor.execute("""
        SELECT alumno.nombre || ' ' || alumno.apellidos, cuotas.mes_cuota, cuotas.importe
        FROM cuotas
        JOIN alumno ON cuotas.id_alumno = alumno.id
        WHERE cuotas.pago_realizado = 0
        ORDER BY cuotas.mes_cuota
        LIMIT ?
    """, (limite,))
    return cursor.fetchall()

def asistencias_del_mes(cursor, anio, mes, id_alumno=None, id_actividad=None):
    """Asistencias de un mes: lista de (fecha, id_actividad, actividad, id_alumno, alumno).
    Si se indica id_alumno o id_actividad, filtra por ellos."""
    sql = """
        SELECT asistencia.fecha_asistencia, actividades.id, actividades.nombre,
               alumno.id, alumno.nombre || ' ' || alumno.apellidos
        FROM asistencia
        JOIN actividades ON asistencia.id_actividades = actividades.id
        JOIN alumno ON asistencia.id_alumno = alumno.id
        WHERE strftime('%Y-%m', asistencia.fecha_asistencia) = ?
    """
    parametros = [f"{anio}-{mes:02d}"]
    # Los filtros se añaden con ? igual que el resto: nunca metemos valores dentro del texto SQL
    if id_alumno is not None:
        sql += " AND alumno.id = ?"
        parametros.append(id_alumno)
    if id_actividad is not None:
        sql += " AND actividades.id = ?"
        parametros.append(id_actividad)
    sql += " ORDER BY asistencia.fecha_asistencia, actividades.nombre"
    cursor.execute(sql, parametros)
    return cursor.fetchall()

def asistencia_por_alumno(cursor, anio, mes, id_actividad=None):
    """Para cada alumno activo: (id, alumno, nº de asistencias del mes, última asistencia del mes).
    Incluye a los que no han venido (con 0). Ordenado de más a menos asistencias."""
    filtro_actividad = "AND asistencia.id_actividades = ?" if id_actividad is not None else ""
    parametros = [f"{anio}-{mes:02d}"]
    if id_actividad is not None:
        parametros.append(id_actividad)
    # LEFT JOIN con las condiciones en el ON: así los alumnos sin asistencias también salen
    cursor.execute(f"""
        SELECT alumno.id, alumno.nombre || ' ' || alumno.apellidos,
               COUNT(asistencia.fecha_asistencia), MAX(asistencia.fecha_asistencia)
        FROM alumno
        LEFT JOIN asistencia ON asistencia.id_alumno = alumno.id
            AND strftime('%Y-%m', asistencia.fecha_asistencia) = ?
            {filtro_actividad}
        WHERE alumno.activo = 1
        GROUP BY alumno.id
        ORDER BY 3 DESC, 2
    """, parametros)
    return cursor.fetchall()
