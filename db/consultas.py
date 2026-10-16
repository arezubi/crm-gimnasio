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

def listar_profesores(cursor):
    """Devuelve [(id, nombre, apellidos, email, telefono, actividades), ...] de los profesores activos."""
    cursor.execute("""
        SELECT profesor.id, profesor.nombre, profesor.apellidos, profesor.email, 
        profesor.telefono, GROUP_CONCAT(actividades.nombre, ', ')
        FROM profesor
        LEFT JOIN actividades ON actividades.id_profesor = profesor.id
        WHERE profesor.activo =1
        GROUP BY profesor.id
        ORDER BY profesor.nombre, profesor.apellidos
    """)
    return cursor.fetchall()

def listar_actividades(cursor):
    """Devuelve [(id, 'Nombre (Profesor)'), ...] de las actividades, ordenadas por nombre."""
    cursor.execute("""
        SELECT actividades.id, actividades.nombre || ' (' || profesor.nombre || ')'
        FROM actividades
        JOIN profesor ON actividades.id_profesor = profesor.id
        ORDER BY actividades.nombre, profesor.nombre
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
    """Devuelve [(id_alumno, nombre, apellidos, email, teléfono, fecha_alta, pagada), ...] de los alumnos activos y el estado de su cuota de un mes dado."""
    cursor.execute("""
        SELECT alumno.id, alumno.nombre, alumno.apellidos, alumno.email, alumno.telefono,
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
    """Devuelve (password_hash, rol, nombre, id) del usuario con ese email, o None si no existe."""
    cursor.execute("SELECT password, rol, nombre, id FROM usuarios WHERE email = ?", (email,))
    return cursor.fetchone()

def esta_inscrito(cursor, id_alumno, id_actividad):
    """Devuelve True si el alumno está inscrito en la actividad, False si no."""
    cursor.execute("""
        SELECT 1
        FROM inscripciones
        WHERE id_alumno = ? AND id_actividades = ?
    """, (id_alumno, id_actividad))
    return cursor.fetchone() is not None

def obtener_estado_cuota(cursor, id_cuota):
    """Devuelve (id_alumno, pagada) o None si la cuota no existe."""
    cursor.execute("SELECT id_alumno, pago_realizado FROM cuotas WHERE id = ?", (id_cuota,))
    return cursor.fetchone()  

def obtener_precio_tipo_cuota(cursor, id_tipo_cuota):
    """Devuelve el precio del tipo de cuota, o None si no existe."""
    cursor.execute("SELECT precio FROM tipo_cuota WHERE id = ?", (id_tipo_cuota,))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None


def ultimo_tipo_cuota(cursor, id_alumno):
    '''Devuelve el id_tipo_cuota de la cuota más reciente del alumno o None si no tiene ninguna.'''
    cursor.execute(''' 
        SELECT id_tipo_cuota FROM cuotas
        WHERE id_alumno = ?
        ORDER BY mes_cuota DESC
        LIMIT 1 
    ''',(id_alumno,))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None

def obtener_alumno(cursor, id_alumno):
    """Devuelve (nombre, apellidos, fecha_cumpleaños, email, teléfono, contacto_emergencia) del alumno o None si no existe."""
    cursor.execute("""
        SELECT nombre, apellidos, fecha_cumpleaños, email, telefono, contacto_emergencia
        FROM alumno
        WHERE id = ?
    """, (id_alumno,))
    return cursor.fetchone()

def hay_usuarios(cursor):
    """Devuelve True si hay al menos un usuario en la tabla, False si está vacía."""
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    return cursor.fetchone()[0] > 0

def listar_gastos(cursor, anio):
    """Devuelve [(id, fecha, concepto, categoria, importe), ...] de los gastos de un año,
    del más reciente al más antiguo."""
    cursor.execute("""
        SELECT id, fecha, concepto, categoria, importe
        FROM gastos
        WHERE strftime('%Y', fecha) = ?
        ORDER BY fecha DESC
    """, (str(anio),))
    return cursor.fetchall()

def listar_inscritos(cursor, id_actividad):
    """ Devuelve [(id_alumno, 'Nombre Apellidos'), ...] de los alumnos activos inscritos en esa actividad, 
    ordenados por nombre."""
    cursor.execute(""" 
        SELECT inscripciones.id_alumno, alumno.nombre || ' ' || alumno.apellidos
        FROM inscripciones
        JOIN alumno ON inscripciones.id_alumno = alumno.id
        WHERE inscripciones.id_actividades = ?
        AND alumno.activo = 1
        ORDER BY alumno.nombre, alumno.apellidos
    """, (id_actividad,))
    return cursor.fetchall()

def asistentes_del_dia(cursor, id_actividad, fecha):
    """Devuelve el conjunto de id_alumno que ya tienen asistencia ese día en esa actividad.
    fecha en formato 'AAAA-MM-DD'."""
    cursor.execute("""
        SELECT id_alumno
        FROM asistencia
        WHERE id_actividades = ? AND fecha_asistencia = ?
    """, (id_actividad, fecha))
    return {fila[0] for fila in cursor.fetchall()}

def listar_cuotas_del_mes(cursor, mes):
    """Devuelve [(id_cuota, alumno, tipo, importe, pagada, fecha_pago), ...] de las cuotas
    de un mes ('AAAA-MM-01'), con las pendientes primero."""
    cursor.execute("""
        SELECT cuotas.id, alumno.nombre || ' ' || alumno.apellidos, tipo_cuota.nombre,
        cuotas.importe, cuotas.pago_realizado, cuotas.fecha_pago
        FROM cuotas
        JOIN alumno ON cuotas.id_alumno = alumno.id
        JOIN tipo_cuota ON cuotas.id_tipo_cuota = tipo_cuota.id
        WHERE cuotas.mes_cuota = ?
        ORDER BY cuotas.pago_realizado, alumno.nombre, alumno.apellidos
    """, (mes,))
    return cursor.fetchall()

def obtener_profesor(cursor, id_profesor):
    """Devuelve (nombre, apellidos, fecha_cumpleaños, email, teléfono) del profesor o None si no existe."""
    cursor.execute("""
        SELECT nombre, apellidos, fecha_cumpleaños, email, telefono
        FROM profesor
        WHERE id = ?
    """, (id_profesor,))
    return cursor.fetchone()

def obtener_gasto(cursor, id_gasto):
    """Devuelve (fecha, concepto, categoria, importe) del gasto o None si no existe."""
    cursor.execute("""
        SELECT fecha, concepto, categoria, importe
        FROM gastos
        WHERE id = ?
    """, (id_gasto,))
    return cursor.fetchone()

def datos_ficha_alumno(cursor, id_alumno):
    """Devuelve (nombre, apellidos, fecha_cumpleaños, email, teléfono, contacto_emergencia,
    fecha_alta) del alumno, o None si no existe."""
    cursor.execute("""
        SELECT nombre, apellidos, fecha_cumpleaños, email, telefono, contacto_emergencia, fecha_alta
        FROM alumno
        WHERE id = ?
    """, (id_alumno,))
    return cursor.fetchone()

def actividades_de_alumno(cursor, id_alumno):
    """Devuelve [(id_actividad, 'Nombre (Profesor)'), ...] de las actividades en las que está
    inscrito el alumno, ordenadas por nombre."""
    cursor.execute("""
        SELECT actividades.id, actividades.nombre || ' (' || profesor.nombre || ')'
        FROM inscripciones
        JOIN actividades ON inscripciones.id_actividades = actividades.id
        JOIN profesor ON actividades.id_profesor = profesor.id
        WHERE inscripciones.id_alumno = ?
        ORDER BY actividades.nombre
    """, (id_alumno,))
    return cursor.fetchall()

def cuotas_de_alumno(cursor, id_alumno):
    """Devuelve [(mes_cuota, tipo, importe, pagada, fecha_pago), ...] de todas las cuotas del
    alumno, de la más reciente a la más antigua."""
    cursor.execute("""
        SELECT cuotas.mes_cuota, tipo_cuota.nombre, cuotas.importe, cuotas.pago_realizado,
               cuotas.fecha_pago
        FROM cuotas
        JOIN tipo_cuota ON cuotas.id_tipo_cuota = tipo_cuota.id
        WHERE cuotas.id_alumno = ?
        ORDER BY cuotas.mes_cuota DESC
    """, (id_alumno,))
    return cursor.fetchall()

def asistencias_de_alumno(cursor, id_alumno):
    """Devuelve [(fecha, actividad), ...] de todas las asistencias del alumno,
    de la más reciente a la más antigua."""
    cursor.execute("""
        SELECT asistencia.fecha_asistencia, actividades.nombre
        FROM asistencia
        JOIN actividades ON asistencia.id_actividades = actividades.id
        WHERE asistencia.id_alumno = ?
        ORDER BY asistencia.fecha_asistencia DESC, actividades.nombre
    """, (id_alumno,))
    return cursor.fetchall()

def listar_usuarios(cursor):
    """Devuelve [(id, nombre, email, rol, profesor), ...] de todos los usuarios, ordenados por
    nombre. profesor es 'Nombre Apellidos' o None si el usuario no es profesor."""
    cursor.execute("""
        SELECT usuarios.id, usuarios.nombre, usuarios.email, usuarios.rol,
               profesor.nombre || ' ' || profesor.apellidos
        FROM usuarios
        LEFT JOIN profesor ON usuarios.id_profesor = profesor.id
        ORDER BY usuarios.nombre
    """)
    return cursor.fetchall()

def datos_usuario(cursor, id_usuario):
    """Devuelve (nombre, email, rol, id_profesor, password_hash) del usuario o None si no existe."""
    cursor.execute("""
        SELECT nombre, email, rol, id_profesor, password
        FROM usuarios
        WHERE id = ?
    """, (id_usuario,))
    return cursor.fetchone()

def contar_admins(cursor):
    """Devuelve cuántos usuarios tienen el rol de administrador."""
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol = 'admin'")
    return cursor.fetchone()[0]

def id_admin_principal(cursor):
    """Devuelve el id del administrador principal: el primer usuario que se creó
    (el que crea la aplicación al arrancar por primera vez), o None si no hay usuarios."""
    cursor.execute("SELECT MIN(id) FROM usuarios")
    return cursor.fetchone()[0]
