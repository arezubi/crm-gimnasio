# CRM Gimnasio

Aplicación de escritorio para gestionar un gimnasio de deportes de contacto
(Boxeo, K1, MMA, BJJ, Fight-BOX y Clases Mixtas). Práctica final del curso de Python.

Tecnologías: Python 3, PySide6, SQLite, Pandas, Matplotlib y bcrypt.

## Funcionalidades
- Login con roles (admin y operador).
- Alta y baja de alumnos y profesores.
- Actividades, inscripciones y registro de asistencia.
- Tipos de cuota, cuotas mensuales y marcar cuotas pagadas.
- Facturas en PDF (carpeta `facturas/`) y listado de facturas emitidas para volver a abrirlas.
- Calendario mensual de asistencia, filtrable por alumno y actividad, con resumen por alumno.
- Listado de alumnos con buscador y estado de la cuota del mes (pagada / pendiente / sin cuota).
- Dashboard con alumnos activos, altas del mes, ingresos del mes, cuotas pendientes,
  actividad más popular, gráfico de los últimos 6 meses y cuotas pendientes más antiguas.
- Estadísticas: ingresos y altas por mes (eligiendo el año) y por año, actividades más populares.

## Criterios
- **Ingresos de un mes** = suma del importe de las cuotas *de ese mes* que están pagadas
  (columna `mes_cuota`), aunque se cobraran otro día.
- El importe se copia en la cuota al crearla. Si después cambia el precio de un tipo de cuota,
  los ingresos de meses anteriores no cambian.
- Las bajas son lógicas (`activo = 0` y `fecha_baja`): se conserva el historial.

## Instalación
1. Instala Python 3 y abre una terminal en la carpeta del proyecto.
2. Instala las dependencias:

       pip install -r requirements.txt

## Puesta en marcha (ejecutar en este orden)
1. `python crear_bbdd.py` crea la base de datos `gimnasio.db`.
2. `python crear_usuario_inicial.py` crea el usuario administrador.
3. `python datos_prueba.py` carga datos de ejemplo y un usuario operador (opcional).
4. `python main.py` arranca la aplicación.

Si cambias la estructura de las tablas, borra `gimnasio.db` y repite los pasos 1 a 3.

## Usuarios de prueba
| Rol | Email | Contraseña |
|-----|-------|------------|
| admin | admin@gimnasio.com | admin123 |
| operador | marcos.login@gimnasio.com | operador123 |

El operador no ve la sección "Usuarios".

## Estructura
- `main.py`: punto de entrada.
- `config.py`: rutas y datos del gimnasio que salen en las facturas (cámbialos por los reales).
- `db/`: acceso a la base de datos.
- `gui/`: pantallas de la aplicación.
  - `ventana_principal.py`: barra lateral y secciones.
  - `componentes.py`: clases base (`Pagina`, `FormularioBase`) y formatos (euros, fechas).
  - `estilo_graficos.py`: tema oscuro de los gráficos y clase base `PaginaGrafico`.
- `informes/`: consultas, estadísticas y generación del PDF de las facturas (`factura_pdf.py`).
- `resources/`: estilos (QSS).
- `assets/`: logo.