# CRM Gimnasio

Aplicación de escritorio para gestionar un gimnasio de deportes de contacto
(Boxeo, K1, MMA, BJJ, Fight-BOX y Clases Mixtas). Práctica final del curso de Python.

Tecnologías: Python 3, PySide6, SQLite, Pandas, Matplotlib, Plotly y bcrypt.

## Funcionalidades
- Login con roles (admin y operador).
- **Inicio (dashboard)**: alumnos activos, altas del mes, ingresos del mes, cuotas pendientes y
  asistencias del mes. Cada tarjeta lleva a su pantalla con un clic. Además, ingresos de los
  últimos 6 meses, ingresos por tipo de cuota, actividades más populares y cuotas pendientes
  más antiguas. El logo de la barra lateral vuelve siempre al inicio.
- **Alumnos**: listado con buscador y estado de la cuota del mes (pagada / pendiente / sin cuota).
  Desde el mismo listado se da de alta, se edita y se da de baja.
- **Profesores**: listado con las actividades que da cada uno. Alta, edición y baja desde el
  listado; al dar de baja a un profesor con actividades, la aplicación lo avisa.
- **Actividades**: alta de actividades, inscripciones, **pasar lista** (se marca de una vez a todos
  los alumnos de una clase) y calendario mensual de asistencia, filtrable por alumno y actividad.
- **Cuotas**: cuotas de cada mes con su estado; desde la lista se cobran o se eliminan las
  pendientes. Generación de las cuotas del mes de todos los alumnos activos con un botón: a
  cada uno se le asigna el mismo tipo que su última cuota (los que no tienen ninguna se indican
  para crearla a mano). Tipos de cuota con su precio.
- **Facturas** en PDF (carpeta `facturas/`) y listado de facturas emitidas para volver a abrirlas.
- **Estadísticas**: ingresos y altas por mes (eligiendo el año) y por año, actividades más
  populares.
- **Informes HTML interactivos**, mensual y anual: altas, facturación, gastos y beneficio bruto,
  con gráficos en los que se puede pasar el ratón, hacer zoom y ocultar series. Se abren en el
  navegador y funcionan sin internet.
- **Gastos** (solo administradores): listado por año con alta, edición y eliminación.
- Cifras en formato español (1.234,50 €) en tablas, gráficos y campos.

## Criterios
- **Ingresos de un mes** = suma del importe de las cuotas *de ese mes* que están pagadas
  (columna `mes_cuota`), aunque se cobraran otro día.
- El importe se copia en la cuota al crearla. Si después cambia el precio de un tipo de cuota,
  los ingresos de meses anteriores no cambian.
- Solo se pueden eliminar cuotas pendientes: una cuota cobrada es un ingreso y puede tener factura.
- Las bajas de alumnos y profesores son lógicas (`activo = 0` y `fecha_baja`): se conserva el
  historial.
- **Beneficio bruto** = facturación − gastos del mismo periodo.

## Instalación
1. Instala Python 3 y abre una terminal en la carpeta del proyecto.
2. Instala las dependencias:

       pip install -r requirements.txt

## Puesta en marcha
1. `python main.py` arranca la aplicación. La primera vez crea automáticamente
   la base de datos `gimnasio.db` y el usuario administrador.
2. (Opcional) `python datos_prueba.py` carga un gimnasio de ejemplo: unos 130 alumnos,
   profesores, actividades, cuotas, facturas, asistencias y gastos de todo 2026, y un usuario
   operador. **Borra la base de datos que haya y la crea de nuevo**, así que no lo ejecutes
   sobre datos reales.

Para empezar desde cero, borra `gimnasio.db` y vuelve a arrancar la aplicación.

## Ejecutable para Windows
    python -m PyInstaller --noconfirm --windowed --icon assets/icono.ico --name CRMGimnasio --add-data "resources;resources" --add-data "assets;assets" --collect-data plotly main.py

El programa queda en `dist/CRMGimnasio/`. La base de datos, las facturas (`facturas/`) y los
informes (`informes_generados/`) se guardan junto a `CRMGimnasio.exe`, así que no se pierden
al instalar una versión nueva. **Copia de seguridad**: basta con copiar esos tres elementos.

La versión entregada incluye una base de datos con datos de prueba. Para empezar con el
gimnasio vacío, borra `gimnasio.db` y la aplicación creará una nueva al abrirse.

## Usuarios de prueba
| Rol | Email | Contraseña |
|-----|-------|------------|
| admin | admin@gimnasio.com | admin123 |
| operador | marcos.login@gimnasio.com | operador123 |

El operador no ve las secciones "Usuarios" ni "Gastos".

## Arquitectura
La aplicación está dividida en capas. Cada capa solo llama a la de debajo:

```
gui  →  logica  →  db
```
  - `gui/` no contiene SQL: pide los datos a db/ y las decisiones a logica/.
  - `logica/` no usa PySide6 ni escribe SQL.
  - `db/` no importa nada de logica/ ni de gui/.

Las operaciones que no tienen ninguna regla (por ejemplo, dar de alta una actividad o borrar
un gasto) se llaman directamente desde `gui` a `db`. Las que tienen reglas pasan siempre por
`logica`.

- `main.py`: punto de entrada.
- `config.py`: rutas y datos del gimnasio que salen en las facturas y los informes.
- `datos_prueba.py`: genera la base de datos de ejemplo.
- `db/`: acceso a la base de datos.
  - `db.py`: escribe (INSERT, UPDATE, DELETE).
  - `consultas.py`: lee (SELECT), sin cambiar nada.
  - `esquema.py`: creación de las tablas.
- `gui/`: pantallas de la aplicación.
  - `ventana_principal.py`: barra lateral, secciones y navegación desde el dashboard.
  - `componentes.py`: piezas comunes: clases base (`Pagina`, `FormularioBase`), formatos
    (euros, fechas), botones dentro de las filas de una tabla (`poner_botones_fila`) y
    formularios en ventana emergente (`abrir_en_dialogo`).
  - `estilo_graficos.py`: tema oscuro de los gráficos y clase base `PaginaGrafico`.
  - `listado_*.py`: las pantallas de listado con sus botones; usan los formularios
    `alta_*`, `editar_*` y `nuevo_gasto.py` en ventanas emergentes.
- `informes/`: solo lectura de la base de datos.
  - `estadisticas.py`: consultas para el dashboard, los gráficos y los informes.
  - `factura_pdf.py`: PDF de las facturas.
  - `informe_html.py`: informes HTML interactivos (Plotly), mensual y anual.
- `logica/`: reglas del negocio.
  - `autenticacion.py`: contraseñas cifradas con bcrypt, login sin revelar qué dato falla.
  - `validaciones.py`: formato de email y longitud mínima de contraseña.
  - `asistencia.py`: solo asisten los alumnos inscritos.
  - `cuotas.py`: el importe se congela al crear la cuota; no se cobra dos veces; solo se
    eliminan las pendientes.
  - `facturas.py`: solo se facturan cuotas pagadas; numeración F-AAAA-NNNN.
  - `gastos.py`: importe mayor que 0 y categoría de la lista, tanto al crear como al editar.
- `resources/`: estilos (QSS) e iconos de los campos.
- `assets/`: logo e icono del ejecutable.

## Mejoras futuras
- Listado de usuarios con edición y borrado, y pantalla "Mi cuenta" para cambiar el nombre y
  la contraseña.
- Estadísticas unificadas: meses y total del año en el mismo gráfico (los informes HTML ya lo
  muestran así).
- Ficha del alumno con su historial de cuotas y asistencias.
- Desinscribir a un alumno de una actividad.
