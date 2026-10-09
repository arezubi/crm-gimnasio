"""Genera el PDF de una factura a partir de su id.

Se usa QTextDocument (un documento HTML sencillo) y QPdfWriter, que vienen con PySide6:
no hace falta instalar ninguna librería más.
"""
from PySide6.QtCore import QMarginsF, QSizeF
from PySide6.QtGui import QPageLayout, QPageSize, QPdfWriter, QTextDocument

from config import CARPETA_FACTURAS, DATOS_GIMNASIO
from gui.componentes import MESES, formatear_euros, formatear_fecha


def numero_factura(id_factura, fecha_factura):
    """id 3 del año 2026 -> 'F-2026-0003'"""
    return f"F-{fecha_factura[:4]}-{id_factura:04d}"


def datos_factura(cursor, id_factura):
    cursor.execute("""
        SELECT factura.id, factura.fecha_factura,
               alumno.nombre || ' ' || alumno.apellidos, alumno.email, alumno.telefono,
               tipo_cuota.nombre, cuotas.mes_cuota, cuotas.importe, cuotas.fecha_pago
        FROM factura
        JOIN cuotas ON factura.id_cuota = cuotas.id
        JOIN alumno ON factura.id_alumno = alumno.id
        JOIN tipo_cuota ON cuotas.id_tipo_cuota = tipo_cuota.id
        WHERE factura.id = ?
    """, (id_factura,))
    fila = cursor.fetchone()
    if fila is None:
        return None
    claves = ["id", "fecha", "alumno", "email", "telefono", "tipo_cuota", "mes_cuota", "importe", "fecha_pago"]
    return dict(zip(claves, fila))


def ruta_pdf(datos):
    return CARPETA_FACTURAS / f"{numero_factura(datos['id'], datos['fecha'])}.pdf"


def html_factura(datos):
    g = DATOS_GIMNASIO
    mes = int(datos["mes_cuota"][5:7])
    periodo = f"{MESES[mes - 1].capitalize()} {datos['mes_cuota'][:4]}"
    importe = formatear_euros(datos["importe"])
    pagada = f"Pagada el {formatear_fecha(datos['fecha_pago'])}. " if datos["fecha_pago"] else ""

    return f"""
    <html><body style="font-family: 'Segoe UI', Arial; font-size: 10pt; color: #222222;">

    <table width="100%" cellspacing="0" cellpadding="0">
      <tr>
        <td valign="top">
          <span style="font-size: 20pt; font-weight: bold; color: #ff6a00;">{g['nombre'].upper()}</span><br>
          <span style="color: #666666;">
            {g['direccion']}<br>CIF: {g['cif']}<br>{g['email']} · {g['telefono']}
          </span>
        </td>
        <td valign="top" align="right">
          <span style="font-size: 22pt; font-weight: bold;">FACTURA</span><br>
          Nº <b>{numero_factura(datos['id'], datos['fecha'])}</b><br>
          Fecha: {formatear_fecha(datos['fecha'])}
        </td>
      </tr>
    </table>

    <p style="margin-top: 28px; color: #666666; font-size: 9pt;">FACTURAR A</p>
    <p style="margin-top: 0px;">
      <b style="font-size: 12pt;">{datos['alumno']}</b><br>
      {datos['email']}<br>{datos['telefono']}
    </p>

    <table width="100%" cellspacing="0" cellpadding="8" style="margin-top: 20px;">
      <tr>
        <th align="left" bgcolor="#1f1f1f" style="color: #ffffff;">Concepto</th>
        <th align="left" bgcolor="#1f1f1f" style="color: #ffffff;">Periodo</th>
        <th align="right" bgcolor="#1f1f1f" style="color: #ffffff;">Importe</th>
      </tr>
      <tr>
        <td>Cuota mensual · {datos['tipo_cuota']}</td>
        <td>{periodo}</td>
        <td align="right">{importe}</td>
      </tr>
    </table>

    <table width="100%" cellspacing="0" cellpadding="8" style="margin-top: 12px;">
      <tr>
        <td align="right" bgcolor="#f3f3f3">
          <span style="font-size: 13pt;">TOTAL&nbsp;&nbsp;<b>{importe}</b></span>
        </td>
      </tr>
    </table>

    <p style="margin-top: 36px; color: #666666; font-size: 9pt;">
      {pagada}Precio con impuestos incluidos.<br>
      Gracias por entrenar con nosotros.
    </p>
    </body></html>
    """


def crear_pdf_factura(cursor, id_factura):
    """Crea (o vuelve a crear) el PDF de la factura y devuelve su ruta."""
    datos = datos_factura(cursor, id_factura)
    if datos is None:
        raise ValueError(f"No existe la factura {id_factura}")

    CARPETA_FACTURAS.mkdir(exist_ok=True)
    ruta = ruta_pdf(datos)

    escritor = QPdfWriter(str(ruta))
    escritor.setPageSize(QPageSize(QPageSize.A4))
    escritor.setPageMargins(QMarginsF(18, 18, 18, 18), QPageLayout.Millimeter)
    escritor.setTitle(f"Factura {numero_factura(datos['id'], datos['fecha'])}")

    documento = QTextDocument()
    documento.setHtml(html_factura(datos))
    # Maquetamos el documento directamente sobre la página del PDF. Si no se le da un
    # tamaño de página, Qt añade un número de página al pie.
    documento.documentLayout().setPaintDevice(escritor)
    documento.setPageSize(QSizeF(escritor.width(), escritor.height()))
    documento.print_(escritor)
    return ruta


def ruta_pdf_existente(cursor, id_factura):
    """Devuelve la ruta del PDF, creándolo solo si todavía no existe."""
    datos = datos_factura(cursor, id_factura)
    ruta = ruta_pdf(datos)
    if not ruta.exists():
        ruta = crear_pdf_factura(cursor, id_factura)
    return ruta
