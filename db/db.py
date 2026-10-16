from datetime import date
import sqlite3

def alta_alumno(cursor, nombre, apellidos, fecha_cumpleaños, email, telefono, contacto_emergencia):
    """
    Función para dar de alta a un alumno en la base de datos.

    Parámetros:
    cursor: Objeto cursor de la base de datos.
    nombre: Nombre del alumno.
    apellidos: Apellidos del alumno.
    fecha_cumpleaños: Fecha de cumpleaños del alumno (formato 'YYYY-MM-DD').
    email: Correo electrónico del alumno.
    telefono: Número de teléfono del alumno.
    contacto_emergencia: Información de contacto de emergencia.

    Retorna:
    True, False o 'duplicado'
    """
    fecha_alta = date.today().isoformat()
    try:
        cursor.execute("""
            INSERT INTO alumno (nombre, apellidos, fecha_cumpleaños, email, telefono, contacto_emergencia, fecha_alta)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nombre, apellidos, fecha_cumpleaños, email, telefono, contacto_emergencia, fecha_alta))
        cursor.connection.commit()
        return True
    except sqlite3.IntegrityError as e:
        cursor.connection.rollback()
        if "UNIQUE" in str(e):
            return "duplicado"
        return False  
    except Exception as e:
        print(f"Error al dar de alta al alumno: {e}")
        cursor.connection.rollback()
        return False

def alta_profesor(cursor, nombre, apellidos, fecha_cumpleaños, email, telefono,activo=True):
    """
    Función para dar de alta a un profesor en la base de datos.

    Parámetros:
    cursor: Objeto cursor de la base de datos.
    nombre: Nombre del profesor.
    apellidos: Apellidos del profesor.
    fecha_cumpleaños: Fecha de cumpleaños del profesor (formato 'YYYY-MM-DD').
    email: Correo electrónico del profesor.
    telefono: Número de teléfono del profesor.
    activo: Estado del profesor (True para activo, False para inactivo).
    La fecha de alta se pone automáticamente (hoy).

    Retorna:
    True, False o 'duplicado'
    """
    fecha_alta = date.today().isoformat()
    try:
        cursor.execute("""
            INSERT INTO profesor (nombre, apellidos, fecha_cumpleaños, email, telefono, activo, fecha_alta)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nombre, apellidos, fecha_cumpleaños, email, telefono, activo, fecha_alta))
        
        cursor.connection.commit()
        return True
    except sqlite3.IntegrityError as e:
        cursor.connection.rollback()
        if "UNIQUE" in str(e):
            return "duplicado"
        return False
    except Exception as e:
        print(f"Error al dar de alta al profesor: {e}")
        cursor.connection.rollback()
        return False


def baja_alumno(cursor, alumno_id):
    """
    Función para dar de baja a un alumno en la base de datos.

    Parámetros:
    cursor: Objeto cursor de la base de datos.
    alumno_id: ID del alumno a dar de baja.

    Retorna:
    True si la operación fue exitosa, False en caso contrario.
    """
    fecha_baja = date.today().isoformat()
    try:
        cursor.execute("""
            UPDATE alumno SET activo = 0, fecha_baja = ?  WHERE id = ?
        """, (fecha_baja, alumno_id,))
        
        cursor.connection.commit()
        return True
    
    except Exception as e:
        print(f"Error al dar de baja al alumno: {e}")
        cursor.connection.rollback()
        return False

def baja_profesor(cursor, profesor_id):
    """
    Función para dar de baja a un profesor en la base de datos.

    Parámetros:
    cursor: Objeto cursor de la base de datos.
    profesor_id: ID del profesor a dar de baja.

    Retorna:
    True si la operación fue exitosa, False en caso contrario
    """
    fecha_baja = date.today().isoformat()
    try:
        cursor.execute("""
            UPDATE profesor SET activo = 0, fecha_baja = ? WHERE id = ?
        """, (fecha_baja, profesor_id,))
        
        cursor.connection.commit()
        return True
    
    except Exception as e:
        print(f"Error al dar de baja al profesor: {e}")
        cursor.connection.rollback()
        return False

def alta_actividad(cursor, nombre, id_profesor):
    """
    Función para dar de alta una actividad impartida por un profesor.

    Parámetros:
    cursor: Objeto cursor de la base de datos.
    nombre: Nombre de la actividad.
    id_profesor: ID del profesor que la imparte.

    Retorna:
    True, False o 'duplicado'
    """
    try:
        cursor.execute("""
            INSERT INTO actividades (nombre, id_profesor)
            VALUES (?, ?)
        """, (nombre, id_profesor))
        cursor.connection.commit()
        return True
    except sqlite3.IntegrityError:
                cursor.connection.rollback()
                return "duplicado"  
    except Exception as e:
        print(f"Error al dar de alta la actividad: {e}")
        cursor.connection.rollback()
        return False

def inscribir_alumno_actividad(cursor, alumno_id, actividad_id):
    """
    Función para inscribir a un alumno en una actividad.

    Parámetros:
    cursor: Objeto cursor de la base de datos.
    alumno_id: ID del alumno a inscribir.
    actividad_id: ID de la actividad en la que se inscribirá el alumno.

    Retorna:
    True, False o 'duplicado' (si ya estaba inscrito)
    """
    try:
        cursor.execute("""
            INSERT INTO inscripciones (id_alumno, id_actividades)
            VALUES (?, ?)
        """, (alumno_id, actividad_id))
        
        cursor.connection.commit()
        return True
    except sqlite3.IntegrityError:
        cursor.connection.rollback()
        return "duplicado"   
    except Exception as e:
        print(f"Error al inscribir al alumno en la actividad: {e}")
        cursor.connection.rollback()
        return False

def desinscribir_alumno(cursor, id_alumno, id_actividad):
    """Quita a un alumno de una actividad. Sus asistencias pasadas se conservan.
    Devuelve True, "no inscrito" o False si hay un error."""
    try:
        cursor.execute("""
            DELETE FROM inscripciones
            WHERE id_alumno = ? AND id_actividades = ?
        """, (id_alumno, id_actividad))
        if cursor.rowcount == 0:
            return "no inscrito"
        cursor.connection.commit()
        return True
    except Exception as e:
        print(f"Error al desinscribir al alumno: {e}")
        cursor.connection.rollback()
        return False

def insertar_cuota(cursor, id_alumno, id_tipo_cuota, mes_cuota, importe):
    """
    Función para insertar una cuota mensual en la base de datos.

    Parámetros:
    cursor: Objeto cursor de la base de datos.
    id_alumno: ID del alumno para el cual se creará la cuota.
    id_tipo_cuota: ID del tipo de cuota.
    mes_cuota: Mes al que corresponde la cuota.
    importe: Importe de la cuota.

    Retorna:
    True, False, o 'duplicado'
    """
    try:
        cursor.execute("""
            INSERT INTO cuotas (id_alumno, id_tipo_cuota, pago_realizado, mes_cuota, importe)
            VALUES (?, ?, ?, ?, ?)
        """, (id_alumno, id_tipo_cuota, 0, mes_cuota, importe))
        
        cursor.connection.commit()
        return True
    except sqlite3.IntegrityError:
            cursor.connection.rollback()
            return "duplicado" 
    except Exception as e:
        print(f"Error al crear la cuota mensual: {e}")
        cursor.connection.rollback()
        return False

def guardar_pago(cursor, id_cuota, fecha_pago):
    """
    Marca una cuota como pagada en la base de datos con la fecha indicada.
    No comprueba nada: eso lo hace logica/cuotas.py.

    Retorna:
    True o False
    """
    try:
        cursor.execute("""
            UPDATE cuotas SET pago_realizado = 1, fecha_pago = ? WHERE id = ?
        """, (fecha_pago, id_cuota))
        cursor.connection.commit()
        return True
    except Exception as e:
        print(f"Error al guardar el pago: {e}")
        cursor.connection.rollback()
        return False


def registrar_asistencia(cursor, id_alumno, id_actividad, fecha_asistencia=None):
    """
    Función para registrar la asistencia de un alumno a una actividad.

    Parámetros:
    cursor: Objeto cursor de la base de datos.
    id_alumno: ID del alumno que asistió.
    id_actividad: ID de la actividad a la que asistió el alumno.
    fecha_asistencia: Fecha de la asistencia (opcional, por defecto es hoy).

    Retorna:
    True si se registra,
    "duplicado" si ya existía ese registro, False si hay otro error.
    """
    if fecha_asistencia is None:
        fecha_asistencia = date.today().isoformat()

    try:
        cursor.execute("""
            INSERT INTO asistencia (id_alumno, id_actividades, fecha_asistencia)
            VALUES (?, ?, ?)
        """, (id_alumno, id_actividad, fecha_asistencia))

        cursor.connection.commit()
        return True

    except sqlite3.IntegrityError:
        cursor.connection.rollback()
        print("Ya existe un registro de asistencia para ese alumno, esa actividad y esa fecha.")
        return "duplicado"
    except Exception as e:
        print(f"Error al registrar la asistencia: {e}")
        cursor.connection.rollback()
        return False

def insertar_factura(cursor, id_cuota, id_alumno, fecha_factura):
    """
    Función para insertar una factura en la base de datos.

    Parámetros:
    cursor: Objeto cursor de la base de datos.
    id_cuota: ID de la cuota para la cual se generarán las facturas.
    id_alumno: ID del alumno al que pertenece la cuota.
    fecha_factura: Fecha de la factura.

    Retorna:
    True, False, o 'duplicado'
    """
    try:
        cursor.execute("""
            INSERT INTO factura (id_alumno, id_cuota, fecha_factura)
            VALUES (?, ?, ?)
        """, (id_alumno, id_cuota, fecha_factura))
        cursor.connection.commit()
        return True
    except sqlite3.IntegrityError:
        cursor.connection.rollback()
        return "duplicado"

    except Exception as e:
        print(f"Error al generar la factura: {e}")
        cursor.connection.rollback()
        return False

def registrar_usuario(cursor, nombre, email, password_hash, rol, id_profesor=None):
    """
    Función para registrar un nuevo usuario en la base de datos.

    Parámetros:
    cursor: Objeto cursor de la base de datos.
    nombre: Nombre del usuario.
    email: Correo electrónico del usuario.
    password_hash: Contraseña del usuario (ya cifrada).
    rol: Rol del usuario ('admin' u 'operador').
    id_profesor: ID del profesor asociado al usuario (opcional).

    Retorna:
    True, False o 'duplicado' (si el email ya existe)
    """
    try:
        cursor.execute("""
            INSERT INTO usuarios (nombre, email, password, rol, id_profesor)
            VALUES (?, ?, ?, ?, ?)
        """, (nombre, email, password_hash, rol, id_profesor))
        
        cursor.connection.commit()
        return True

    except sqlite3.IntegrityError:
        print("El correo electrónico ya está registrado. No se puede crear el usuario.")
        cursor.connection.rollback()
        return "duplicado"

    except Exception as e:
        print(f"Error al registrar el usuario: {e}")
        cursor.connection.rollback()
        return False

def alta_tipo_cuota(cursor, nombre, precio):
    """
    Función para dar de alta un nuevo tipo de cuota en la base de datos.

    Parámetros:
    cursor: Objeto cursor de la base de datos.
    nombre: Nombre del tipo de cuota.
    precio: Precio del tipo de cuota.

    Retorna:
    True, False o 'duplicado'
    """
    try:
        cursor.execute("""
            INSERT INTO tipo_cuota (nombre, precio)
            VALUES (?, ?)
        """, (nombre, precio))
        
        cursor.connection.commit()
        return True
    except sqlite3.IntegrityError:
        cursor.connection.rollback()
        return "duplicado" 
    except Exception as e:
        print(f"Error al dar de alta el tipo de cuota: {e}")
        cursor.connection.rollback()
        return False

def actualizar_alumno(cursor, id_alumno, nombre, apellidos, fecha_cumpleaños, email, telefono, contacto_emergencia):
    """
    Función para actualizar la información de un alumno en la base de datos.

    Parámetros:
    cursor: Objeto cursor de la base de datos.
    id_alumno: ID del alumno a actualizar.
    nombre: Nuevo nombre del alumno (opcional).
    apellidos: Nuevos apellidos del alumno (opcional).
    fecha_cumpleaños: Nueva fecha de cumpleaños del alumno (opcional).
    email: Nuevo correo electrónico del alumno (opcional).
    telefono: Nuevo número de teléfono del alumno (opcional).
    contacto_emergencia: Nueva información de contacto de emergencia (opcional).

    Retorna:
    True si la operación fue exitosa, False en caso contrario o 'duplicado' si el email ya existe para otro alumno.
    """
    
    try:
        cursor.execute("""
            UPDATE alumno
            SET nombre = ?, apellidos = ?, fecha_cumpleaños = ?, email = ?, telefono = ?, contacto_emergencia = ?
            WHERE id = ?
        """, (nombre, apellidos, fecha_cumpleaños, email, telefono, contacto_emergencia, id_alumno))

    except sqlite3.IntegrityError as e:
            cursor.connection.rollback()
            if "UNIQUE" in str(e):
                return "duplicado"
            return False  
    except Exception as e:
        print(f"Error al dar de alta al alumno: {e}")
        cursor.connection.rollback()
        return False

    cursor.connection.commit()
    return True

def insertar_gastos(cursor, fecha, concepto, categoria, importe):
    """Función para insertar gastos
    Parámtros:
    fecha: Fecha del gasto.
    concepto: Concepto del gasto.
    categoría: Categoria, debe de estar dentro del seleccionable.
    importe: Importe del gasto.

    Retorna:
    True o False
    """
    try:
        cursor.execute("""
            INSERT INTO gastos (fecha, concepto, categoria, importe)
            VALUES (?, ?, ?, ?)
        """, (fecha, concepto, categoria, importe))
        cursor.connection.commit()
        return True
    except Exception as e:
        print(f"Error al crear el gasto: {e}")
        cursor.connection.rollback()
        return False

def borrar_cuota(cursor, id_cuota):
    """Borra una cuota.

    Retorna:
    True si se borra, "no existe" si no hay ninguna con ese id,
    "facturada" si tiene factura asociada (no se puede borrar), False si hay otro error.
    """
    try:
        cursor.execute("DELETE FROM cuotas WHERE id = ?", (id_cuota,))
        if cursor.rowcount == 0:
            return "no existe"
        cursor.connection.commit()
        return True
    except sqlite3.IntegrityError:
        cursor.connection.rollback()
        return "facturada"
    except Exception as e:
        print(f"Error al borrar la cuota: {e}")
        cursor.connection.rollback()
        return False

def actualizar_profesor(cursor, id_profesor, nombre, apellidos, fecha_cumpleaños, email, telefono):
    """
    Función para actualizar la información de un profesor en la base de datos.

    Parámetros:
    cursor: Objeto cursor de la base de datos.
    id_alumno: ID del alumno a actualizar.
    nombre: Nuevo nombre del alumno (opcional).
    apellidos: Nuevos apellidos del alumno (opcional).
    fecha_cumpleaños: Nueva fecha de cumpleaños del alumno (opcional).
    email: Nuevo correo electrónico del alumno (opcional).
    telefono: Nuevo número de teléfono del alumno (opcional).

    Retorna:
    True si la operación fue exitosa, False en caso contrario o 'duplicado' si el email ya existe para otro profesor.
    """
    
    try:
        cursor.execute("""
            UPDATE profesor
            SET nombre = ?, apellidos = ?, fecha_cumpleaños = ?, email = ?, telefono = ?
            WHERE id = ?
        """, (nombre, apellidos, fecha_cumpleaños, email, telefono, id_profesor))

    except sqlite3.IntegrityError as e:
            cursor.connection.rollback()
            if "UNIQUE" in str(e):
                return "duplicado"
            return False  
    except Exception as e:
        print(f"Error al dar de alta al profesor: {e}")
        cursor.connection.rollback()
        return False

    cursor.connection.commit()
    return True

def actualizar_gasto(cursor, id_gasto, fecha, concepto, categoria, importe):
    """Cambia los datos de un gasto. Devuelve True, "no existe" o False si hay un error."""
    try:
        cursor.execute("""
            UPDATE gastos
            SET fecha = ?, concepto = ?, categoria = ?, importe = ?
            WHERE id = ?
        """, (fecha, concepto, categoria, importe, id_gasto))
        if cursor.rowcount == 0:
            return "no existe"
        cursor.connection.commit()
        return True
    except Exception as e:
        print(f"Error al actualizar el gasto: {e}")
        cursor.connection.rollback()
        return False

def borrar_gasto(cursor, id_gasto):
    """Borra un gasto. Devuelve True, "no existe" o False si hay un error."""
    try:
        cursor.execute("DELETE FROM gastos WHERE id = ?", (id_gasto,))
        if cursor.rowcount == 0:
            return "no existe"
        cursor.connection.commit()
        return True
    except Exception as e:
        print(f"Error al borrar el gasto: {e}")
        cursor.connection.rollback()
        return False

def actualizar_usuario(cursor, id_usuario, nombre, email, rol, id_profesor):
    """Cambia los datos de un usuario (no la contraseña).
    Devuelve True, "duplicado" si el email es de otro usuario, "no existe" o False."""
    try:
        cursor.execute("""
            UPDATE usuarios
            SET nombre = ?, email = ?, rol = ?, id_profesor = ?
            WHERE id = ?
        """, (nombre, email, rol, id_profesor, id_usuario))
        if cursor.rowcount == 0:
            return "no existe"
        cursor.connection.commit()
        return True
    except sqlite3.IntegrityError:
        cursor.connection.rollback()
        return "duplicado"
    except Exception as e:
        print(f"Error al actualizar el usuario: {e}")
        cursor.connection.rollback()
        return False

def cambiar_password(cursor, id_usuario, password_hash):
    """Guarda una contraseña nueva (ya cifrada). Devuelve True o False."""
    try:
        cursor.execute("UPDATE usuarios SET password = ? WHERE id = ?", (password_hash, id_usuario))
        cursor.connection.commit()
        return True
    except Exception as e:
        print(f"Error al cambiar la contraseña: {e}")
        cursor.connection.rollback()
        return False

def borrar_usuario(cursor, id_usuario):
    """Borra un usuario. Devuelve True, "no existe" o False."""
    try:
        cursor.execute("DELETE FROM usuarios WHERE id = ?", (id_usuario,))
        if cursor.rowcount == 0:
            return "no existe"
        cursor.connection.commit()
        return True
    except Exception as e:
        print(f"Error al borrar el usuario: {e}")
        cursor.connection.rollback()
        return False
