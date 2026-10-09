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