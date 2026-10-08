import sqlite3

# 1. Conectar (si el archivo no existe, SQLite lo crea automáticamente)
conexion = sqlite3.connect("gimnasio.db")

# 2. Crear un cursor (es lo que usas para ejecutar sentencias SQL)
cursor = conexion.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

# 3. Ejecutar una sentencia SQL
cursor.execute("""
    CREATE TABLE IF NOT EXISTS alumno (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	nombre VARCHAR NOT NULL,
	apellidos VARCHAR NOT NULL,
	fecha_cumpleaños DATE NOT NULL,
	email VARCHAR UNIQUE NOT NULL,
	telefono varchar NOT NULL,
	contacto_emergencia varchar NOT NULL,
    fecha_alta DATE NOT NULL,
    fecha_baja DATE,
    activo BOOLEAN NOT NULL DEFAULT 1
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS profesor (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR NOT NULL,
    apellidos VARCHAR NOT NULL,
    fecha_cumpleaños DATE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    telefono VARCHAR NOT NULL,
    fecha_alta DATE NOT NULL,
    fecha_baja DATE,
    activo BOOLEAN NOT NULL DEFAULT 1
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS actividades (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	nombre VARCHAR NOT NULL,
	id_profesor INTEGER NOT NULL,
    FOREIGN KEY (id_profesor) REFERENCES PROFESOR(id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS inscripciones (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	id_alumno INTEGER NOT NULL,
	id_actividades INTEGER NOT NULL,
	FOREIGN KEY (id_alumno) REFERENCES ALUMNO(id),
	FOREIGN KEY (id_actividades) REFERENCES ACTIVIDADES(id),
    UNIQUE(id_alumno, id_actividades)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS asistencia (
	id_actividades INTEGER NOT NULL, 
	id_alumno INTEGER NOT NULL,
	fecha_asistencia DATE NOT NULL,
	PRIMARY KEY (id_actividades, id_alumno, fecha_asistencia),
	FOREIGN KEY (id_actividades) REFERENCES ACTIVIDADES(id),
	FOREIGN KEY (id_alumno) REFERENCES ALUMNO(id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS tipo_cuota (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	nombre VARCHAR NOT NULL,
	precio INTEGER NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS cuotas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_alumno INTEGER NOT NULL,
    id_tipo_cuota INTEGER NOT NULL,
    fecha_pago TIMESTAMP,
    pago_realizado BOOLEAN NOT NULL DEFAULT 0,
    mes_cuota DATE NOT NULL,
    importe INTEGER NOT NULL,
    FOREIGN KEY (id_alumno) REFERENCES ALUMNO(id),
    FOREIGN KEY (id_tipo_cuota) REFERENCES TIPO_CUOTA(id),
    UNIQUE(id_alumno, mes_cuota)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS factura (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	id_alumno INTEGER NOT NULL,
	id_cuota INTEGER NOT NULL, 
    fecha_factura DATE NOT NULL,
    FOREIGN KEY (id_alumno) REFERENCES ALUMNO(id),
    FOREIGN KEY (id_cuota) REFERENCES CUOTAS(id),
    UNIQUE(id_cuota)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	nombre VARCHAR NOT NULL,
	email VARCHAR UNIQUE NOT NULL,
	password VARCHAR NOT NULL,
	id_profesor INTEGER,
	rol VARCHAR NOT NULL,
	FOREIGN KEY (id_profesor) REFERENCES PROFESOR(id)
    )
""")

# 4. Confirmar los cambios (sin esto, ¡no se guarda nada en el archivo!)
conexion.commit()

# 5. Cerrar la conexión
conexion.close()