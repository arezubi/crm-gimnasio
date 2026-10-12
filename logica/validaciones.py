LONGITUD_MINIMA_PASSWORD = 6

def email_valido(email):
    """Devuelve True si el email tiene un formato válido, False en caso contrario."""

    if " "  in email:
        return False
    partes = email.split("@")
    if len(partes) != 2:
        return False
    usuario, dominio = partes
    if not usuario or not dominio:
        return False
    if "." not in dominio:
        return False
    if dominio.startswith(".") or dominio.endswith("."):
        return False
    return True


def password_valida(password):
    """Devuelve True si la contraseña cumple con los requisitos de longitud, False en caso contrario."""
    return len(password) >= LONGITUD_MINIMA_PASSWORD