"""
Script para poblar gimnasio.db con datos de prueba.

Cubre varias casuísticas para poder probar la app de verdad:
- Alumnos activos e inactivos
- Profesores activos e inactivos
- Varios tipos de cuota (infantil, adulto, adulto 2 actividades)
- Actividades repartidas entre profesores
- Alumnos inscritos en 1 o 2 actividades
- Cuotas pagadas y pendientes, en dos meses distintos (para ver "ingresos por mes")
- Alumnos dados de alta en meses distintos (para ver "alumnos nuevos por mes")
- Facturas generadas solo para algunas cuotas pagadas (para ver "cuotas pendientes de facturar")
- Asistencias repartidas en varios días
- Un usuario admin y un usuario operador vinculado a un profesor (para probar el login)

Ejecútalo UNA VEZ desde la raíz del proyecto: python datos_prueba.py
Si ya tenías datos de antes y quieres partir de cero, borra gimnasio.db y
vuelve a ejecutar crear_bbdd.py antes de este script.
"""

import sqlite3
from config import RUTA_BD
from db.db import (
    alta_alumno,
    alta_profesor,
    alta_actividad,
    alta_tipo_cuota,
    inscribir_alumno_actividad,
    crear_cuota_mensual,
    marcar_cuota_pagada,
    registrar_asistencia,
    generar_facturas,
    registrar_usuario,
)

conexion = sqlite3.connect(RUTA_BD)
conexion.execute("PRAGMA foreign_keys = ON")
cursor = conexion.cursor()


def id_ultima_fila(tabla):
    """Pequeño ayudante: devuelve el id autoincremental de la última fila insertada en una tabla."""
    cursor.execute(f"SELECT id FROM {tabla} ORDER BY id DESC LIMIT 1")
    return cursor.fetchone()[0]


print("--- Profesores ---")
alta_profesor(cursor, "Carlos", "Ruiz Peña", "1985-02-20", "carlos@gimnasio.com", "600111222")
id_carlos = id_ultima_fila("profesor")

alta_profesor(cursor, "Elena", "Torres Gil", "1990-06-15", "elena@gimnasio.com", "600333444", activo=False)
id_elena = id_ultima_fila("profesor")  # profesor inactivo, para probar que no sale en los desplegables

alta_profesor(cursor, "Marcos", "Díaz Soto", "1988-11-03", "marcos@gimnasio.com", "600555666")
id_marcos = id_ultima_fila("profesor")


print("--- Tipos de cuota ---")
alta_tipo_cuota(cursor, "infantil", 28)
id_infantil = id_ultima_fila("tipo_cuota")

alta_tipo_cuota(cursor, "adulto", 49)
id_adulto = id_ultima_fila("tipo_cuota")

alta_tipo_cuota(cursor, "adulto_2_actividades", 64)
id_adulto_2act = id_ultima_fila("tipo_cuota")


print("--- Actividades ---")
alta_actividad(cursor, "Boxeo", id_carlos)
id_boxeo = id_ultima_fila("actividades")

alta_actividad(cursor, "BJJ", id_marcos)
id_bjj = id_ultima_fila("actividades")

alta_actividad(cursor, "MMA", id_carlos)
id_mma = id_ultima_fila("actividades")

alta_actividad(cursor, "Kickboxing", id_marcos)
id_kickboxing = id_ultima_fila("actividades")


print("--- Alumnos ---")
# Alumnos activos, con fechas de alta en meses distintos para poder ver "alumnos nuevos por mes"
alta_alumno(cursor, "Ana", "García López", "2000-04-12", "ana@example.com", "600111000", "Madre: 600222000")
id_ana = id_ultima_fila("alumno")

alta_alumno(cursor, "Luis", "Gómez Ruiz", "1995-08-23", "luis@example.com", "600333000", "Hermano: 600444000")
id_luis = id_ultima_fila("alumno")

alta_alumno(cursor, "Sofía", "Reyes Martín", "2012-09-22", "sofia@example.com", "600555000", "Padre: 600666000")
id_sofia = id_ultima_fila("alumno")

alta_alumno(cursor, "Marta", "Ibáñez Cruz", "2010-03-05", "marta@example.com", "600777000", "Madre: 600888000")
id_marta = id_ultima_fila("alumno")

alta_alumno(cursor, "Pablo", "Sánchez Vidal", "1998-01-17", "pablo@example.com", "600999000", "Pareja: 600000111")
id_pablo = id_ultima_fila("alumno")

# Alumno dado de baja, para probar que no aparece en listados de activos
alta_alumno(cursor, "Elena", "Molina Ortiz", "1992-07-30", "elena.m@example.com", "600222111", "Amigo: 600333111")
id_elena_baja = id_ultima_fila("alumno")
cursor.execute("UPDATE alumno SET activo = 0 WHERE id = ?", (id_elena_baja,))
conexion.commit()


print("--- Inscripciones (algunos alumnos en más de una actividad) ---")
inscribir_alumno_actividad(cursor, id_ana, id_boxeo)
inscribir_alumno_actividad(cursor, id_luis, id_bjj)
inscribir_alumno_actividad(cursor, id_luis, id_mma)       # Luis: 2 actividades
inscribir_alumno_actividad(cursor, id_sofia, id_kickboxing)
inscribir_alumno_actividad(cursor, id_marta, id_boxeo)
inscribir_alumno_actividad(cursor, id_marta, id_bjj)       # Marta: 2 actividades
inscribir_alumno_actividad(cursor, id_pablo, id_mma)


print("--- Cuotas: dos meses, mezcla de pagadas y pendientes ---")
# Agosto: todas pagadas
crear_cuota_mensual(cursor, id_ana, id_adulto, "2026-08-01")
marcar_cuota_pagada(cursor, id_ultima_fila("cuotas"))

crear_cuota_mensual(cursor, id_luis, id_adulto_2act, "2026-08-01")
marcar_cuota_pagada(cursor, id_ultima_fila("cuotas"))

crear_cuota_mensual(cursor, id_sofia, id_infantil, "2026-08-01")
marcar_cuota_pagada(cursor, id_ultima_fila("cuotas"))

# Septiembre: algunas pagadas, otras pendientes (para "pagos pendientes" y "cuotas pendientes")
crear_cuota_mensual(cursor, id_ana, id_adulto, "2026-09-01")
marcar_cuota_pagada(cursor, id_ultima_fila("cuotas"))

crear_cuota_mensual(cursor, id_luis, id_adulto_2act, "2026-09-01")
# ↑ esta la dejamos SIN pagar a propósito

crear_cuota_mensual(cursor, id_sofia, id_infantil, "2026-09-01")
# ↑ esta también sin pagar

crear_cuota_mensual(cursor, id_marta, id_adulto_2act, "2026-09-01")
marcar_cuota_pagada(cursor, id_ultima_fila("cuotas"))

crear_cuota_mensual(cursor, id_pablo, id_adulto, "2026-09-01")
# ↑ sin pagar


print("--- Facturas: solo para algunas cuotas pagadas, para poder ver el listado de 'cuotas pagadas sin facturar' ---")
cursor.execute("SELECT id FROM cuotas WHERE id_alumno = ? AND mes_cuota = '2026-08-01'", (id_ana,))
generar_facturas(cursor, cursor.fetchone()[0])

cursor.execute("SELECT id FROM cuotas WHERE id_alumno = ? AND mes_cuota = '2026-09-01'", (id_ana,))
generar_facturas(cursor, cursor.fetchone()[0])
# La cuota de agosto de Luis se queda pagada pero SIN factura a propósito


print("--- Asistencias, repartidas en varios días ---")
registrar_asistencia(cursor, id_ana, id_boxeo, "2026-09-01")
registrar_asistencia(cursor, id_ana, id_boxeo, "2026-09-03")
registrar_asistencia(cursor, id_ana, id_boxeo, "2026-09-08")
registrar_asistencia(cursor, id_luis, id_bjj, "2026-09-02")
registrar_asistencia(cursor, id_luis, id_mma, "2026-09-04")
registrar_asistencia(cursor, id_marta, id_boxeo, "2026-09-01")
registrar_asistencia(cursor, id_marta, id_bjj, "2026-09-05")
registrar_asistencia(cursor, id_sofia, id_kickboxing, "2026-09-06")


print("--- Usuarios (para probar el login) ---")
# El admin lo crea crear_usuario_inicial.py; aquí solo añadimos un operador.
registrar_usuario(cursor, "Marcos Login", "marcos.login@gimnasio.com", "operador123", "operador", id_marcos)

conexion.close()

print("\n¡Listo! Datos de prueba insertados en gimnasio.db.")
print("Usuarios para entrar en la app:")
print("  admin@gimnasio.com / admin123  (creado por crear_usuario_inicial.py)")
print("  marcos.login@gimnasio.com / operador123  (rol operador, vinculado a Marcos Díaz)")
