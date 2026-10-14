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
- ~100 alumnos generados con cuotas de todo 2026, asistencias y gastos, para el informe anual

Ejecútalo UNA VEZ desde la raíz del proyecto: python datos_prueba.py
Si ya tenías datos de antes y quieres partir de cero, borra gimnasio.db antes de ejecutarlo.
"""

import random
import sqlite3
import unicodedata
from datetime import date, timedelta
from config import RUTA_BD
from db.db import (
    alta_alumno,
    alta_profesor,
    alta_actividad,
    alta_tipo_cuota,
    inscribir_alumno_actividad,
    baja_alumno
)
from db.esquema import crear_tablas
from logica.autenticacion import crear_admin_si_no_hay_usuarios, crear_usuario
from logica.asistencia import registrar_asistencia
from logica.facturas import facturar_cuota
from logica.cuotas import crear_cuota_mensual, marcar_cuota_pagada
from logica.gastos import registrar_gasto

conexion = sqlite3.connect(RUTA_BD)
conexion.execute("PRAGMA foreign_keys = ON")
cursor = conexion.cursor()

crear_tablas(conexion)
crear_admin_si_no_hay_usuarios(cursor)

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
alta_tipo_cuota(cursor, "Infantil", 28)
id_infantil = id_ultima_fila("tipo_cuota")

alta_tipo_cuota(cursor, "Adulto", 49)
id_adulto = id_ultima_fila("tipo_cuota")

alta_tipo_cuota(cursor, "Adulto 2 actividades", 64)
id_adulto_2act = id_ultima_fila("tipo_cuota")


print("--- Actividades ---")
alta_actividad(cursor, "Boxeo", id_carlos)
id_boxeo = id_ultima_fila("actividades")

alta_actividad(cursor, "BJJ", id_marcos)
id_bjj = id_ultima_fila("actividades")

alta_actividad(cursor, "MMA", id_carlos)
id_mma = id_ultima_fila("actividades")

alta_actividad(cursor, "Fight-BOX", id_marcos)
id_fightbox = id_ultima_fila("actividades")

alta_actividad(cursor, "K1", id_carlos)
id_k1 = id_ultima_fila("actividades")

alta_actividad(cursor, "Clases Mixtas", id_marcos)
id_clases_mixtas = id_ultima_fila("actividades")


print("--- Alumnos ---")
# Alumnos activos, con fechas de alta en meses distintos para poder ver "alumnos nuevos por mes"
alta_alumno(cursor, "Ana", "García López", "2000-04-12", "ana@example.com", "600111000", "Madre: 600222000")
id_ana = id_ultima_fila("alumno")
cursor.execute("UPDATE alumno SET fecha_alta = ? WHERE id = ?", ("2026-03-10", id_ana,))

alta_alumno(cursor, "Luis", "Gómez Ruiz", "1995-08-23", "luis@example.com", "600333000", "Hermano: 600444000")
id_luis = id_ultima_fila("alumno")
cursor.execute("UPDATE alumno SET fecha_alta = ? WHERE id = ?", ("2025-06-01", id_luis,))

alta_alumno(cursor, "Sofía", "Reyes Martín", "2012-09-22", "sofia@example.com", "600555000", "Padre: 600666000")
id_sofia = id_ultima_fila("alumno")
cursor.execute("UPDATE alumno SET fecha_alta = ? WHERE id = ?", ("2026-01-07", id_sofia,))

alta_alumno(cursor, "Marta", "Ibáñez Cruz", "2010-03-05", "marta@example.com", "600777000", "Madre: 600888000")
id_marta = id_ultima_fila("alumno")
cursor.execute("UPDATE alumno SET fecha_alta = ? WHERE id = ?", ("2025-03-10", id_marta,))

alta_alumno(cursor, "Pablo", "Sánchez Vidal", "1998-01-17", "pablo@example.com", "600999000", "Pareja: 600000111")
id_pablo = id_ultima_fila("alumno")

# Alumno dado de baja, para probar que no aparece en listados de activos
alta_alumno(cursor, "Elena", "Molina Ortiz", "1992-07-30", "elena.m@example.com", "600222111", "Amigo: 600333111")
id_elena_baja = id_ultima_fila("alumno")
cursor.execute("UPDATE alumno SET fecha_alta = ? WHERE id = ?", ("2025-03-10", id_elena_baja,))
baja_alumno(cursor, id_elena_baja)
cursor.execute("UPDATE alumno SET fecha_baja = ? WHERE id = ?", ("2026-10-01", id_elena_baja,))
conexion.commit()

print("--- Inscripciones (algunos alumnos en más de una actividad) ---")
inscribir_alumno_actividad(cursor, id_ana, id_boxeo)
inscribir_alumno_actividad(cursor, id_luis, id_k1)
inscribir_alumno_actividad(cursor, id_luis, id_mma)       # Luis: 2 actividades
inscribir_alumno_actividad(cursor, id_sofia, id_fightbox)
inscribir_alumno_actividad(cursor, id_sofia, id_clases_mixtas)
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

# Octubre: algunas pagadas, otras pendientes (para "pagos pendientes" y "cuotas pendientes")
crear_cuota_mensual(cursor, id_ana, id_adulto, "2026-10-01")
marcar_cuota_pagada(cursor, id_ultima_fila("cuotas"))

crear_cuota_mensual(cursor, id_luis, id_adulto_2act, "2026-10-01")
# ↑ esta la dejamos SIN pagar a propósito

crear_cuota_mensual(cursor, id_sofia, id_infantil, "2026-10-01")
# ↑ esta también sin pagar

crear_cuota_mensual(cursor, id_marta, id_adulto_2act, "2026-10-01")
marcar_cuota_pagada(cursor, id_ultima_fila("cuotas"))

crear_cuota_mensual(cursor, id_pablo, id_adulto, "2026-10-01")
# ↑ sin pagar


print("--- Facturas: solo para algunas cuotas pagadas, para poder ver el listado de 'cuotas pagadas sin facturar' ---")
cursor.execute("SELECT id FROM cuotas WHERE id_alumno = ? AND mes_cuota = '2026-08-01'", (id_ana,))
facturar_cuota(cursor, cursor.fetchone()[0])

cursor.execute("SELECT id FROM cuotas WHERE id_alumno = ? AND mes_cuota = '2026-09-01'", (id_ana,))
facturar_cuota(cursor, cursor.fetchone()[0])
# La cuota de agosto de Luis se queda pagada pero SIN factura a propósito


print("--- Asistencias, repartidas en varios días ---")
registrar_asistencia(cursor, id_ana, id_boxeo, "2026-09-01")
registrar_asistencia(cursor, id_ana, id_boxeo, "2026-09-03")
registrar_asistencia(cursor, id_ana, id_boxeo, "2026-09-08")
registrar_asistencia(cursor, id_luis, id_k1, "2026-09-02")
registrar_asistencia(cursor, id_luis, id_mma, "2026-09-04")
registrar_asistencia(cursor, id_marta, id_boxeo, "2026-09-01")
registrar_asistencia(cursor, id_marta, id_bjj, "2026-09-05")
registrar_asistencia(cursor, id_sofia, id_fightbox, "2026-09-06")

print("--- Usuarios (para probar el login) ---")
# El admin lo crea crear_admin_si_no_hay_usuarios(); aquí solo añadimos un operador.
crear_usuario(cursor, "Marcos Login", "marcos.login@gimnasio.com", "operador123", "operador", id_marcos)


# =====================================================================================
# Alumnos generados: un gimnasio con ~100 alumnos para que el informe anual sea realista
# (con 5 alumnos no se cubren ni el alquiler ni las nóminas).
# random.seed fija el azar: cada vez que se ejecuta el script salen los mismos datos.
# =====================================================================================
random.seed(2026)
HOY = date.today()

NOMBRES = ["Lucía", "Hugo", "Martina", "Mateo", "Paula", "Leo", "Julia", "Daniel", "Valeria", "Álvaro",
           "Carmen", "Adrián", "Noa", "Diego", "Sara", "Mario", "Irene", "Javier", "Claudia", "Sergio",
           "Laura", "Pablo", "Elena", "Iván", "Alba", "Rubén", "Nerea", "Óscar", "Lola", "Marcos"]
APELLIDOS = ["García", "Martínez", "López", "Sánchez", "Pérez", "Gómez", "Martín", "Jiménez", "Ruiz",
             "Hernández", "Díaz", "Moreno", "Muñoz", "Álvarez", "Romero", "Navarro", "Torres", "Domínguez",
             "Vázquez", "Ramos", "Gil", "Serrano", "Molina", "Blanco", "Castro", "Ortega", "Rubio", "Medina"]
ACTIVIDADES = [id_boxeo, id_bjj, id_mma, id_fightbox, id_k1, id_clases_mixtas]

# Altas por mes: la mayoría ya estaban en 2025, con picos en enero y septiembre (vuelta al cole)
ALTAS_2026 = {1: 8, 2: 4, 3: 4, 4: 3, 5: 3, 6: 2, 7: 2, 8: 1, 9: 10, 10: 4}
ALUMNOS_PREVIOS = 85


def sin_tildes(texto):
    """'Álvaro' -> 'alvaro' (para construir emails)."""
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()


def fecha_al_azar(anio, mes, dia_maximo=28):
    return date(anio, mes, random.randint(1, dia_maximo)).isoformat()


def dar_de_alta_alumno_generado(numero, fecha_alta):
    """Crea un alumno con tipo de cuota e inscripciones coherentes. Devuelve (id, id_tipo_cuota)."""
    nombre = random.choice(NOMBRES)
    apellidos = f"{random.choice(APELLIDOS)} {random.choice(APELLIDOS)}"
    tipo = random.choices([id_infantil, id_adulto, id_adulto_2act], weights=[25, 45, 30])[0]
    nacimiento = (fecha_al_azar(random.randint(2012, 2019), random.randint(1, 12)) if tipo == id_infantil
                  else fecha_al_azar(random.randint(1975, 2005), random.randint(1, 12)))
    email = f"{sin_tildes(nombre)}.{sin_tildes(apellidos.split()[0])}{numero}@example.com"
    telefono = f"6{random.randint(10000000, 99999999)}"

    alta_alumno(cursor, nombre, apellidos, nacimiento, email, telefono, f"Familiar: 6{random.randint(10000000, 99999999)}")
    id_alumno = id_ultima_fila("alumno")
    cursor.execute("UPDATE alumno SET fecha_alta = ? WHERE id = ?", (fecha_alta, id_alumno))
    conexion.commit()

    # "Adulto 2 actividades" -> 2 inscripciones; el resto -> 1
    for id_actividad in random.sample(ACTIVIDADES, 2 if tipo == id_adulto_2act else 1):
        inscribir_alumno_actividad(cursor, id_alumno, id_actividad)
    return id_alumno, tipo


print("--- Alumnos generados ---")
generados = []          # (id_alumno, id_tipo_cuota, fecha_alta)
numero = 1
for _ in range(ALUMNOS_PREVIOS):
    fecha_alta = fecha_al_azar(2025, random.randint(1, 12))
    generados.append((*dar_de_alta_alumno_generado(numero, fecha_alta), fecha_alta))
    numero += 1
for mes, cantidad in ALTAS_2026.items():
    if mes > HOY.month:
        continue
    for _ in range(cantidad):
        dia_maximo = min(28, HOY.day) if mes == HOY.month else 28    # nada de altas en el futuro
        fecha_alta = fecha_al_azar(2026, mes, dia_maximo)
        generados.append((*dar_de_alta_alumno_generado(numero, fecha_alta), fecha_alta))
        numero += 1

# Algunas bajas a lo largo del año
bajas = {}              # id_alumno -> mes de la baja
for id_alumno, _, _ in random.sample(generados[:ALUMNOS_PREVIOS], 7):
    mes_baja = random.randint(3, HOY.month)
    baja_alumno(cursor, id_alumno)
    dia_maximo = min(20, HOY.day) if mes_baja == HOY.month else 20
    cursor.execute("UPDATE alumno SET fecha_baja = ? WHERE id = ?",
                   (fecha_al_azar(2026, mes_baja, dia_maximo), id_alumno))
    conexion.commit()
    bajas[id_alumno] = mes_baja


print("--- Cuotas de 2026 de los alumnos generados ---")
for id_alumno, tipo, fecha_alta in generados:
    mes_alta = int(fecha_alta[5:7]) if fecha_alta.startswith("2026") else 1
    ultimo_mes = bajas.get(id_alumno, HOY.month + 1) - 1     # la cuota del mes de la baja ya no se cobra
    for mes in range(mes_alta, ultimo_mes + 1):
        if crear_cuota_mensual(cursor, id_alumno, tipo, f"2026-{mes:02d}-01") is not True:
            continue
        # Los meses pasados están casi todos cobrados; el mes actual, solo una parte
        probabilidad_pago = 0.6 if mes == HOY.month else 0.97
        if random.random() < probabilidad_pago:
            marcar_cuota_pagada(cursor, id_ultima_fila("cuotas"))


print("--- Facturas de algunas cuotas de septiembre ---")
cursor.execute("""
    SELECT id FROM cuotas
    WHERE mes_cuota = '2026-09-01' AND pago_realizado = 1
    AND id NOT IN (SELECT id_cuota FROM factura)
    LIMIT 15
""")
for (id_cuota,) in cursor.fetchall():
    facturar_cuota(cursor, id_cuota)


print("--- Asistencias de septiembre y octubre ---")
cursor.execute("""
    SELECT alumno.id, inscripciones.id_actividades FROM alumno
    JOIN inscripciones ON inscripciones.id_alumno = alumno.id
    WHERE alumno.activo = 1
""")
inscripciones = cursor.fetchall()
dia = date(2026, 9, 1)
while dia <= HOY:
    if dia.weekday() < 5:                              # de lunes a viernes
        for id_alumno, id_actividad in inscripciones:
            if random.random() < 0.18:                 # cada alumno viene ~1 de cada 5 días a cada actividad
                registrar_asistencia(cursor, id_alumno, id_actividad, dia.isoformat())
    dia += timedelta(days=1)


print("--- Gastos de 2026 ---")
for mes in range(1, HOY.month + 1):
    registrar_gasto(cursor, f"2026-{mes:02d}-01", "Alquiler del local", "Alquiler", 1100)
    registrar_gasto(cursor, fecha_al_azar(2026, mes, 10), "Iberdrola (luz)", "Suministros",
                    round(random.uniform(140, 230), 2))
    registrar_gasto(cursor, fecha_al_azar(2026, mes, 10), "Canal de Isabel II (agua)", "Suministros",
                    round(random.uniform(35, 60), 2))
    registrar_gasto(cursor, f"2026-{mes:02d}-05", "Fibra e internet", "Suministros", 45.90)
    if mes < HOY.month:                                # las nóminas del mes actual aún no se han pagado
        registrar_gasto(cursor, f"2026-{mes:02d}-28", "Nómina Carlos Ruiz", "Sueldos", 1250)
        registrar_gasto(cursor, f"2026-{mes:02d}-28", "Nómina Marcos Díaz", "Sueldos", 1250)

registrar_gasto(cursor, "2026-02-12", "Guantes y vendas", "Material", 384.50)
registrar_gasto(cursor, "2026-03-03", "Seguro de responsabilidad civil", "Otros", 310)
registrar_gasto(cursor, "2026-04-20", "Reparación de la ducha", "Mantenimiento", 218.40)
registrar_gasto(cursor, "2026-07-15", "Revisión del aire acondicionado", "Mantenimiento", 175)
registrar_gasto(cursor, "2026-09-02", "Tatami nuevo", "Material", 1290)


conexion.close()

print("\n¡Listo! Datos de prueba insertados en gimnasio.db.")
print("Usuarios para entrar en la app:")
print("  admin@gimnasio.com / admin123")
print("  marcos.login@gimnasio.com / operador123  (rol operador, vinculado a Marcos Díaz)")

