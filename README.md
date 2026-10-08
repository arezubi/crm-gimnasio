# CRM Gimnasio

Aplicación de escritorio para gestionar un gimnasio de deportes de contacto
(Boxeo, K1, MMA, BJJ, Fight-BOX y Clases Mixtas). Práctica final del curso de Python.

Tecnologías: Python 3, PySide6, SQLite, Pandas, Matplotlib y bcrypt.

## Funcionalidades
- Login con roles (admin y operador).
- Alta y baja de alumnos y profesores.
- Actividades, inscripciones y registro de asistencia.
- Tipos de cuota, cuotas mensuales, marcar cuotas pagadas y facturas.
- Dashboard con alumnos activos, pagos pendientes, ingresos del mes,
  alumnos nuevos y actividad más usada.
- Estadísticas: ingresos y alumnos nuevos por mes y por año, actividad más usada.

## Instalación
1. Instala Python 3 y abre una terminal en la carpeta del proyecto.
2. Instala las dependencias:

       pip install -r requirements.txt

## Puesta en marcha (ejecutar en este orden)
1. `python crear_bbdd.py` crea la base de datos `gimnasio.db`.
2. `python crear_usuario_inicial.py` crea el usuario administrador.
3. `python datos_prueba.py` carga datos de ejemplo (opcional).
4. `python main.py` arranca la aplicación.

Si cambias la estructura de las tablas, borra `gimnasio.db` y repite los pasos 1 a 3.

## Usuarios de prueba
| Rol | Email | Contraseña |
|-----|-------|------------|
| admin | admin@gimnasio.com | admin123 |
| operador | marcos.login@gimnasio.com | operador123 |

El operador no ve el menú "Usuario".

## Estructura
- `main.py`: punto de entrada.
- `db/`: acceso a la base de datos.
- `gui/`: ventanas de la aplicación.
- `informes/`: consultas y cálculos de estadísticas.
- `resources/`: estilos (QSS).
- `assets/`: logo.