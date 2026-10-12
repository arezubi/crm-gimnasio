import db.db as db
from db.consultas import esta_inscrito

def registrar_asistencia(cursor, id_alumno, id_actividad, fecha):
    """Registra la asistencia de un alumno en la base de datos. Devuelve True, False, 'duplicado' o 'no inscrito'."""
    if not esta_inscrito(cursor, id_alumno, id_actividad):
        return "no inscrito"
    return db.registrar_asistencia(cursor, id_alumno, id_actividad, fecha)