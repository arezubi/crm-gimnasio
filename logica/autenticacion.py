from db.consultas import obtener_usuario
import bcrypt

def iniciar_sesion(cursor, email, password):
    """Devuelve el rol y nombre si el email y la contraseña son correctos, o None si no lo son."""
    usuario = obtener_usuario(cursor, email)
    if usuario is None:
        return None
    password_hash, rol, nombre = usuario
    if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
        return rol, nombre
    else:
        return None