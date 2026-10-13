# CRM Gimnasio

Aplicación de escritorio para gestionar un gimnasio de deportes de contacto
(Boxeo, K1, MMA, BJJ, Fight-BOX y Clases Mixtas). Práctica final del curso de Python.

Tecnologías: Python 3, PySide6, SQLite, Pandas, Matplotlib y bcrypt.

## Funcionalidades
- Login con roles (admin y operador).
- Alta, edición y baja de alumnos; alta y baja de profesores.
- Actividades, inscripciones y registro de asistencia.
- Tipos de cuota, cuotas mensuales y marcar cuotas pagadas. Generación de las cuotas del mes de todos los alumnos activos con un botón: a cada uno se le asigna el mismo tipo que su última cuota. Los alumnos sin ninguna cuota anterior se indican para crearla a mano.
- Facturas en PDF (carpeta `facturas/`) y listado de facturas emitidas para volver a abrirlas.
- Calendario mensual de asistencia, filtrable por alumno y actividad, con resumen por alumno.
- Listado de alumnos con buscador y estado de la cuota del mes (pagada / pendiente / sin cuota).
- Dashboard con alumnos activos, altas del mes, ingresos mensuales (total y desglose por tipo de cuota: infantil, adulto y adulto 2 actividades), cuotas pendientes, asistencias del mes, actividades más utilizadas, gráfico de los últimos 6 meses y cuotas pendientes más antiguas.
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

## Puesta en marcha
1. `python main.py` arranca la aplicación. La primera vez crea automáticamente
   la base de datos `gimnasio.db` y el usuario administrador.
2. (Opcional) `python datos_prueba.py` carga alumnos, profesores, cuotas y un
   usuario operador de ejemplo para probar la aplicación.

Para empezar desde cero, borra `gimnasio.db` y vuelve a arrancar la aplicación.

## Ejecutable para Windows
    python -m PyInstaller --noconfirm --name CRMGimnasio --add-data "resources;resources" --add-data "assets;assets" main.py

El programa queda en `dist/CRMGimnasio/`. La base de datos y las facturas se guardan
junto a `CRMGimnasio.exe`, así que no se pierden al instalar una versión nueva.

## Usuarios de prueba
| Rol | Email | Contraseña |
|-----|-------|------------|
| admin | admin@gimnasio.com | admin123 |
| operador | marcos.login@gimnasio.com | operador123 |

El operador no ve la sección "Usuarios".

## Arquitectura
La aplicación está dividida en capas. Cada capa solo llama a la de debajo:

```
gui  →  logica  →  db
```
  - `gui/` no contiene SQL: pide los datos a db/ y las decisiones a logica/.
  - `logica/` no usa PySide6 ni escribe SQL.
  - `db/` no importa nada de logica/ ni de gui/.

Las operaciones que no tienen ninguna regla (por ejemplo, dar de alta una actividad)
se llaman directamente desde `gui` a `db`. Las que tienen reglas pasan siempre por `logica`.

- `main.py`: punto de entrada.
- `config.py`: rutas y datos del gimnasio que salen en las facturas (cámbialos por los reales).
- `db/`: acceso a la base de datos.
  - `db.py`: escribe (altas, bajas, INSERT, UPDATE).
  - `consultas.py`: lee (SELECT), sin cambiar nada.
  - `esquema.py`: creación de las tablas.
- `gui/`: pantallas de la aplicación.
  - `ventana_principal.py`: barra lateral y secciones.
  - `componentes.py`: clases base (`Pagina`, `FormularioBase`) y formatos (euros, fechas).
  - `estilo_graficos.py`: tema oscuro de los gráficos y clase base `PaginaGrafico`.
- `informes/`: estadísticas (leen la base de datos directamente, solo lectura) y generación del PDF de las facturas (`factura_pdf.py`).
- `logica/`: reglas del negocio.
  - `autenticacion.py`: contraseñas cifradas con bcrypt, login sin revelar qué dato falla.
  - `validaciones.py`: formato de email y longitud mínima de contraseña.
  - `asistencia.py`: solo asisten los alumnos inscritos.
  - `facturas.py`: solo se facturan cuotas pagadas; numeración F-AAAA-NNNN.
  - `cuotas.py`: el importe se congela al crear la cuota; no se cobra dos veces.
- `resources/`: estilos (QSS).
- `assets/`: logo.