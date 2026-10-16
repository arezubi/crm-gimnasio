from db.consultas import contar_admins, datos_usuario
from db.db import actualizar_usuario, borrar_usuario, cambiar_password
from logica.autenticacion import cifrar_password, password_correcta
from logica.validaciones import email_valido, password_valida


def es_ultimo_admin(cursor, id_usuario):
    """True si ese usuario es administrador y no hay ningún otro."""
    datos = datos_usuario(cursor, id_usuario)
    return datos is not None and datos[2] == "admin" and contar_admins(cursor) == 1


def modificar_usuario(cursor, id_usuario, id_actual, nombre, email, rol, id_profesor, password_nueva=""):
    """Un administrador cambia los datos de un usuario y, si escribe una, su contraseña.
    id_actual es el usuario que ha iniciado sesión.
    Devuelve True, False, 'no existe', 'duplicado', 'email no válido', 'contraseña corta',
    'propio rol' (quitarse a sí mismo el rol de admin) o 'ultimo admin'."""
    if datos_usuario(cursor, id_usuario) is None:
        return "no existe"
    if not email_valido(email):
        return "email no válido"
    if password_nueva and not password_valida(password_nueva):
        return "contraseña corta"
    if rol != "admin":
        if id_usuario == id_actual:
            return "propio rol"
        if es_ultimo_admin(cursor, id_usuario):
            return "ultimo admin"

    resultado = actualizar_usuario(cursor, id_usuario, nombre, email, rol, id_profesor)
    if resultado is True and password_nueva:
        resultado = cambiar_password(cursor, id_usuario, cifrar_password(password_nueva))
    return resultado


def eliminar_usuario(cursor, id_usuario, id_actual):
    """Borra un usuario. No se puede borrar uno mismo ni al último administrador.
    Devuelve True, False, 'no existe', 'propio' o 'ultimo admin'."""
    if id_usuario == id_actual:
        return "propio"
    if es_ultimo_admin(cursor, id_usuario):
        return "ultimo admin"
    return borrar_usuario(cursor, id_usuario)


def cambiar_mi_cuenta(cursor, id_usuario, nombre, password_actual="", password_nueva=""):
    """El propio usuario cambia su nombre y, si quiere, su contraseña (escribiendo la actual).
    Devuelve True, False, 'no existe', 'contraseña incorrecta' o 'contraseña corta'."""
    datos = datos_usuario(cursor, id_usuario)
    if datos is None:
        return "no existe"
    _, email, rol, id_profesor, password_hash = datos
    if password_nueva:
        if not password_correcta(password_actual, password_hash):
            return "contraseña incorrecta"
        if not password_valida(password_nueva):
            return "contraseña corta"

    resultado = actualizar_usuario(cursor, id_usuario, nombre, email, rol, id_profesor)
    if resultado is True and password_nueva:
        resultado = cambiar_password(cursor, id_usuario, cifrar_password(password_nueva))
    return resultado
