"""Consultas de solo lectura que usan las pantallas (desplegables, listados...)."""


def listar_alumnos_activos(cursor):
    """Devuelve [(id, 'Nombre Apellidos'), ...] de los alumnos activos, ordenados por nombre."""
    cursor.execute("""
        SELECT id, nombre || ' ' || apellidos
        FROM alumno
        WHERE activo = 1
        ORDER BY nombre, apellidos
    """)
    return cursor.fetchall()

def listar_profesores_activos(cursor):
    """Devuelve [(id, 'Nombre Apellidos'), ...] de los profesores activos, ordenados por nombre."""
    cursor.execute("""
        SELECT id, nombre || ' ' || apellidos
        FROM profesor
        WHERE activo = 1
        ORDER BY nombre, apellidos
    """)
    return cursor.fetchall()

def listar_actividades(cursor):
    """Devuelve [(id, nombre), ...] de las actividades, ordenadas por nombre."""
    cursor.execute("""
        SELECT id, nombre
        FROM actividades
        ORDER BY nombre
    """)
    return cursor.fetchall()

def listar_tipos_cuota(cursor):
    """Devuelve [(id, nombre, precio), ...] de los tipos de cuota, ordenadas por nombre."""
    cursor.execute("""
        SELECT id, nombre, precio
        FROM tipo_cuota
        ORDER BY nombre
    """)
    return cursor.fetchall()

def listar_cuotas_pendientes(cursor):
    """Devuelve [(id_cuota, nombre y apellidos, mes_cuota, importe), ...] de las cuotas pendientes de pago."""
    cursor.execute("""
        SELECT cuotas.id, alumno.nombre || ' ' || alumno.apellidos, cuotas.mes_cuota, cuotas.importe
        FROM cuotas
        JOIN alumno ON cuotas.id_alumno = alumno.id
        WHERE cuotas.pago_realizado = 0
        ORDER BY cuotas.mes_cuota, alumno.nombre
    """)
    return cursor.fetchall()

def listar_facturas(cursor):
    """Devuelve [(id_factura, fecha, nombre y apellidos, tipo_cuota, mes_cuota, importe), ...] las facturas emitidas."""
    cursor.execute("""
        SELECT factura.id, factura.fecha_factura, alumno.nombre || ' ' || alumno.apellidos,
            tipo_cuota.nombre, cuotas.mes_cuota, cuotas.importe
        FROM factura
        JOIN cuotas ON factura.id_cuota = cuotas.id
        JOIN alumno ON factura.id_alumno = alumno.id
        JOIN tipo_cuota ON cuotas.id_tipo_cuota = tipo_cuota.id
        ORDER BY factura.id DESC
    """)
    return cursor.fetchall()

def listar_alumnos_con_cuotas(cursor, mes):
    """Devuelve [(nombre, apellidos, email, teléfono, fecha_alta, pagada), ...] de los alumnos activos y el estado de su cuota de un mes dado."""
    cursor.execute("""
        SELECT alumno.nombre, alumno.apellidos, alumno.email, alumno.telefono,
            alumno.fecha_alta, cuotas.pago_realizado
        FROM alumno
        LEFT JOIN cuotas ON cuotas.id_alumno = alumno.id AND cuotas.mes_cuota = ?
        WHERE alumno.activo = 1
        ORDER BY alumno.nombre, alumno.apellidos
    """, (mes, ))
    return cursor.fetchall()

def listar_cuotas_facturables(cursor):
    """Devuelve [(id_cuota, nombre y apellidos, mes_cuota, importe), ...] de las cuotas pagadas que aún no tienen factura."""
    cursor.execute("""
        SELECT cuotas.id, alumno.nombre || ' ' || alumno.apellidos, cuotas.mes_cuota, cuotas.importe
        FROM cuotas
        JOIN alumno ON cuotas.id_alumno = alumno.id
        WHERE cuotas.pago_realizado = 1
        AND cuotas.id NOT IN (SELECT id_cuota FROM factura)
        ORDER BY cuotas.mes_cuota, alumno.nombre
    """)
    return cursor.fetchall()

def id_factura_de_cuota(cursor, id_cuota):
    """Devuelve el id de la factura asociada a una cuota, o None si no existe."""
    cursor.execute("SELECT id FROM factura WHERE id_cuota = ?", (id_cuota,))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None

def obtener_usuario(cursor, email):
    """Devuelve el password_hash, rol y nombre del usuario con ese email, o None si no existe."""
    cursor.execute("SELECT password, rol, nombre FROM usuarios WHERE email = ?", (email,))
    return cursor.fetchone()

def esta_inscrito(cursor, id_alumno, id_actividad):
    """Devuelve True si el alumno está inscrito en la actividad, False si no."""
    cursor.execute("""
        SELECT 1
        FROM inscripciones
        WHERE id_alumno = ? AND id_actividades = ?
    """, (id_alumno, id_actividad))
    return cursor.fetchone() is not None