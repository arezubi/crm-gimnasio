from datetime import date
import sqlite3
import bcrypt

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
        print("Alumno dado de alta exitosamente.")
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
        # Insertar el nuevo profesor en la tabla correspondiente
        cursor.execute("""
            INSERT INTO profesor (nombre, apellidos, fecha_cumpleaños, email, telefono, activo, fecha_alta)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nombre, apellidos, fecha_cumpleaños, email, telefono, activo, fecha_alta))
        
        # Confirmar los cambios en la base de datos
        cursor.connection.commit()
        print("Profesor dado de alta exitosamente.")
        return True
    except sqlite3.IntegrityError as e:
        cursor.connection.rollback()
        if "UNIQUE" in str(e):
            return "duplicado"
        return False
    except Exception as e:
        # Manejar cualquier error que ocurra durante la inserción
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
        # Baja al alumno de la tabla correspondiente
        cursor.execute("""
            UPDATE alumno SET activo = 0, fecha_baja = ?  WHERE id = ?
        """, (fecha_baja, alumno_id,))
        
        # Confirmar los cambios en la base de datos
        cursor.connection.commit()
        print("Alumno dado de baja exitosamente.")
        return True
    
    except Exception as e:
        # Manejar cualquier error que ocurra durante la eliminación
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
        # Baja al profesor de la tabla correspondiente
        cursor.execute("""
            UPDATE profesor SET activo = 0, fecha_baja = ? WHERE id = ?
        """, (fecha_baja, profesor_id,))
        
        # Confirmar los cambios en la base de datos
        cursor.connection.commit()
        print("Profesor dado de baja exitosamente.")
        return True
    
    except Exception as e:
        # Manejar cualquier error que ocurra durante la eliminación
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
        # Insertar la inscripción del alumno en la tabla correspondiente
        cursor.execute("""
            INSERT INTO inscripciones (id_alumno, id_actividades)
            VALUES (?, ?)
        """, (alumno_id, actividad_id))
        
        # Confirmar los cambios en la base de datos
        cursor.connection.commit()
        return True
    except sqlite3.IntegrityError:
        cursor.connection.rollback()
        return "duplicado"   
    except Exception as e:
        # Manejar cualquier error que ocurra durante la inscripción
        print(f"Error al inscribir al alumno en la actividad: {e}")
        cursor.connection.rollback()
        return False

def crear_cuota_mensual(cursor, id_alumno, id_tipo_cuota, mes_cuota):
    """
    Función para crear una cuota mensual para un alumno.

    Parámetros:
    cursor: Objeto cursor de la base de datos.
    id_alumno: ID del alumno para el cual se creará la cuota.
    id_tipo_cuota: ID del tipo de cuota.
    mes_cuota: Mes al que corresponde la cuota.

    Retorna:
    True, False, 'duplicado' o 'no existe'
    """
    try:
        cursor.execute("SELECT precio FROM tipo_cuota WHERE id = ?", (id_tipo_cuota,))
        resultado = cursor.fetchone()
        if resultado is None:
            return "no existe"
        precio = resultado[0]
        # Insertar la cuota mensual en la tabla correspondiente
        cursor.execute("""
            INSERT INTO cuotas (id_alumno, id_tipo_cuota, pago_realizado, mes_cuota, importe)
            VALUES (?, ?, ?, ?, ?)
        """, (id_alumno, id_tipo_cuota, 0, mes_cuota, precio))
        
        # Confirmar los cambios en la base de datos
        cursor.connection.commit()
        return True
    except sqlite3.IntegrityError:
            cursor.connection.rollback()
            return "duplicado" 
    except Exception as e:
        # Manejar cualquier error que ocurra durante la creación de la cuota
        print(f"Error al crear la cuota mensual: {e}")
        cursor.connection.rollback()
        return False

def marcar_cuota_pagada(cursor, id_cuota):
    """
    Función para marcar una cuota como pagada.

    Parámetros:
    cursor: Objeto cursor de la base de datos.
    id_cuota: ID de la cuota a marcar como pagada.

    Retorna:
    True, False, 'ya pagada' o 'no existe'
    """

    try:
        cursor.execute("SELECT pago_realizado FROM cuotas WHERE id = ?", (id_cuota,))
        resultado = cursor.fetchone()
        if resultado is None:
            return "no existe"
        if resultado[0] == 1:
            return "ya pagada"
        
        # Actualizar el estado de la cuota a pagada
        hoy = date.today().isoformat()  
        cursor.execute("""
            UPDATE cuotas SET pago_realizado = 1, fecha_pago = ? WHERE id = ?
        """, (hoy, id_cuota))
        
        # Confirmar los cambios en la base de datos
        cursor.connection.commit()
        print("Cuota marcada como pagada exitosamente.")
        return True
    
    except Exception as e:
        # Manejar cualquier error que ocurra durante la actualización
        print(f"Error al marcar la cuota como pagada: {e}")
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
    True si se registra, "no inscrito" si el alumno no está en esa actividad,
    "duplicado" si ya existía ese registro, False si hay otro error.
    """
    if fecha_asistencia is None:
        fecha_asistencia = date.today().isoformat()

    try:
        cursor.execute("""
            SELECT 1 FROM inscripciones
            WHERE id_alumno = ? AND id_actividades = ?
        """, (id_alumno, id_actividad))
        if cursor.fetchone() is None:
            return "no inscrito"

        cursor.execute("""
            INSERT INTO asistencia (id_alumno, id_actividades, fecha_asistencia)
            VALUES (?, ?, ?)
        """, (id_alumno, id_actividad, fecha_asistencia))

        cursor.connection.commit()
        print("Asistencia registrada exitosamente.")
        return True

    except sqlite3.IntegrityError:
        cursor.connection.rollback()
        print("Ya existe un registro de asistencia para ese alumno, esa actividad y esa fecha.")
        return "duplicado"
    except Exception as e:
        print(f"Error al registrar la asistencia: {e}")
        cursor.connection.rollback()
        return False

def generar_facturas(cursor, id_cuota, fecha_factura=None):
    """
    Función para generar facturas para una cuota específica.

    Parámetros:
    cursor: Objeto cursor de la base de datos.
    id_cuota: ID de la cuota para la cual se generarán las facturas.
    fecha_factura: Fecha de la factura (opcional, por defecto es hoy).

    Retorna:
    True, False, 'duplicado', 'no pagada' o 'no existe'
    """
    if fecha_factura is None:
        fecha_factura = date.today().isoformat()
    
    try:
        cursor.execute("SELECT id_alumno, pago_realizado FROM cuotas WHERE id = ?", (id_cuota,))
        resultado = cursor.fetchone()
        if resultado is None:
            print("No se encontró la cuota especificada.")
            return "no existe"
        if resultado[1] == 0:
            print("La cuota no ha sido pagada. No se puede generar la factura.")
            return "no pagada"
        if resultado[1] == 1:
            print("La cuota ya ha sido pagada. Se puede generar la factura.")

        id_alumno = resultado[0]
        # Insertar la factura en la tabla correspondiente
        cursor.execute("""
            INSERT INTO factura (id_alumno, id_cuota, fecha_factura)
            VALUES (?, ?, ?)
        """, (id_alumno, id_cuota, fecha_factura))
        
        # Confirmar los cambios en la base de datos
        cursor.connection.commit()
        print("Factura generada exitosamente.")
        return True
    except sqlite3.IntegrityError:
        print("Ya existe una factura para esta cuota.")
        cursor.connection.rollback()
        return "duplicado"
    except Exception as e:
        # Manejar cualquier error que ocurra durante la generación de la factura
        print(f"Error al generar la factura: {e}")
        cursor.connection.rollback()
        return False

def registrar_usuario(cursor, nombre, email, password, rol, id_profesor=None):
    """
    Función para registrar un nuevo usuario en la base de datos.

    Parámetros:
    cursor: Objeto cursor de la base de datos.
    nombre: Nombre del usuario.
    email: Correo electrónico del usuario.
    password: Contraseña del usuario (en texto plano).
    rol: Rol del usuario ('admin' u 'operador').
    id_profesor: ID del profesor asociado al usuario (opcional).

    Retorna:
    True, False o 'duplicado' (si el email ya existe)
    """
    try:
        # Hashear la contraseña antes de almacenarla
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Insertar el nuevo usuario en la tabla correspondiente
        cursor.execute("""
            INSERT INTO usuarios (nombre, email, password, rol, id_profesor)
            VALUES (?, ?, ?, ?, ?)
        """, (nombre, email, hashed_password.decode('utf-8'), rol, id_profesor))
        
        # Confirmar los cambios en la base de datos
        cursor.connection.commit()
        print("Usuario registrado exitosamente.")
        return True

    except sqlite3.IntegrityError:
        print("El correo electrónico ya está registrado. No se puede crear el usuario.")
        cursor.connection.rollback()
        return "duplicado"

    except Exception as e:
        # Manejar cualquier error que ocurra durante el registro
        print(f"Error al registrar el usuario: {e}")
        cursor.connection.rollback()
        return False

def verificar_login(cursor, email, password):
    """
    Función para comprobar el email y la contraseña de un usuario.

    Retorna el rol ('admin' u 'operador') si las credenciales son válidas,
    None en caso contrario.
    """
    try:
        cursor.execute("SELECT password, rol FROM usuarios WHERE email = ?", (email,))
        resultado = cursor.fetchone()

        if resultado is None:
            print("Usuario no encontrado.")
            return None

        hashed_password, rol = resultado

        if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            print("Inicio de sesión exitoso.")
            return rol
        else:
            print("Contraseña incorrecta.")
            return None

    except Exception as e:
        print(f"Error al verificar el inicio de sesión: {e}")
        return None

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
        # Insertar el nuevo tipo de cuota en la tabla correspondiente
        cursor.execute("""
            INSERT INTO tipo_cuota (nombre, precio)
            VALUES (?, ?)
        """, (nombre, precio))
        
        # Confirmar los cambios en la base de datos
        cursor.connection.commit()
        print("Tipo de cuota dado de alta exitosamente.")
        return True
    except sqlite3.IntegrityError:
        cursor.connection.rollback()
        return "duplicado" 
    except Exception as e:
        # Manejar cualquier error que ocurra durante la inserción
        print(f"Error al dar de alta el tipo de cuota: {e}")
        cursor.connection.rollback()
        return False