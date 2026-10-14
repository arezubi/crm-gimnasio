import html
from datetime import date
import plotly.graph_objects as go
from plotly.offline import get_plotlyjs
from config import CARPETA_INFORMES, DATOS_GIMNASIO
from informes.estadisticas import (
    alumnos_nuevos_por_mes,
    asistencias_por_actividad,
    calcular_ingresos_por_mes,
    gastos_del_mes,
    gastos_por_categoria,
    gastos_por_mes,
    ingresos_por_tipo_cuota,
    ingresos_por_tipo_cuota_anual,
)

# informes no importa nada de gui, así que tiene sus propios nombres de mes
MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
         "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# Colores de la marca (los mismos que en estilo.qss)
NARANJA = "#ff6a00"
GRIS = "#6b7280"
VERDE = "#22c55e"
ROJO = "#ef4444"
COLORES_CIRCULAR = [NARANJA, "#ffa45c", "#ffd0a8", GRIS, "#9ca3af", "#d1d5db"]


# ---------- Piezas reutilizables ----------

def euros(valor):
    """1234.5 -> '1.234,50 €' (formato español)."""
    texto = f"{valor:,.2f}"                      # '1,234.50'
    return texto.replace(",", "X").replace(".", ",").replace("X", ".") + " €"


def estilo_grafico(fig, titulo):
    """Aplica el tema oscuro de la app a una figura de Plotly."""
    fig.update_layout(
        title=titulo,
        template="plotly_dark",
        paper_bgcolor="#1a1a1a",
        plot_bgcolor="#1a1a1a",
        font=dict(family="Segoe UI, sans-serif", color="#e5e5e5"),
        separators=",.",                         # decimales con coma, miles con punto
        margin=dict(l=40, r=20, t=60, b=40),
        legend=dict(orientation="h", y=-0.15),
        hoverlabel=dict(bgcolor="#262626"),
    )
    return fig


def grafico(fig):
    """Convierte la figura en un trozo de HTML. La librería de Plotly no va aquí:
    se mete una sola vez en la cabecera de la página (ver pagina_html)."""
    html_fig = fig.to_html(full_html=False, include_plotlyjs=False,
                           config={"displaylogo": False})
    return f'<div class="grafico">{html_fig}</div>'


def grafico_circular(titulo, etiquetas, valores):
    if not any(valores):
        return f'<div class="grafico sin-datos"><h3>{titulo}</h3><p>Sin datos en este periodo.</p></div>'

    fig = go.Figure(go.Pie(
        labels=etiquetas, values=valores, hole=0.5, sort=False,
        marker=dict(colors=COLORES_CIRCULAR),
        hovertemplate="%{label}: %{value:,.2f} € (%{percent})<extra></extra>",
    ))
    return grafico(estilo_grafico(fig, titulo))


def tarjeta(titulo, valor, detalle="", clase=""):
    return f"""
    <div class="tarjeta {clase}">
        <div class="tarjeta-titulo">{titulo}</div>
        <div class="tarjeta-valor">{valor}</div>
        <div class="tarjeta-detalle">{detalle}</div>
    </div>"""


def tabla(cabeceras, filas, fila_total=None):
    """Tabla HTML. html.escape evita que un texto con < o & rompa la página."""
    cabecera = "".join(f"<th>{html.escape(str(c))}</th>" for c in cabeceras)
    cuerpo = ""
    for fila in filas:
        cuerpo += "<tr>" + "".join(f"<td>{html.escape(str(c))}</td>" for c in fila) + "</tr>"
    if fila_total:
        cuerpo += '<tr class="total">' + "".join(f"<td>{html.escape(str(c))}</td>" for c in fila_total) + "</tr>"
    return f"<table><thead><tr>{cabecera}</tr></thead><tbody>{cuerpo}</tbody></table>"


def pagina_html(titulo, contenido):
    """Monta la página completa. La librería de Plotly va dentro del propio archivo:
    así el informe funciona sin internet y se puede enviar por correo tal cual."""
    generado = date.today().strftime("%d/%m/%Y")
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo} · {DATOS_GIMNASIO['nombre']}</title>
<script>{get_plotlyjs()}</script>
<style>
    body {{ margin: 0; background: #111; color: #e5e5e5; font-family: "Segoe UI", sans-serif; }}
    .contenido {{ max-width: 1200px; margin: 0 auto; padding: 24px 16px 48px; }}
    header {{ border-bottom: 3px solid {NARANJA}; padding-bottom: 12px; margin-bottom: 24px; }}
    header .marca {{ color: {NARANJA}; font-weight: 700; letter-spacing: 2px; font-size: 14px; }}
    header h1 {{ margin: 4px 0; font-size: 28px; }}
    header .fecha {{ color: #9ca3af; font-size: 13px; }}
    h2 {{ font-size: 18px; margin: 32px 0 12px; }}
    .tarjetas {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }}
    .tarjeta {{ background: #1a1a1a; border-radius: 10px; padding: 16px; border-left: 4px solid {NARANJA}; }}
    .tarjeta.positivo {{ border-left-color: {VERDE}; }}
    .tarjeta.negativo {{ border-left-color: {ROJO}; }}
    .tarjeta-titulo {{ color: #9ca3af; font-size: 13px; text-transform: uppercase; }}
    .tarjeta-valor {{ font-size: 28px; font-weight: 700; margin: 6px 0; }}
    .tarjeta-detalle {{ color: #9ca3af; font-size: 13px; }}
    .rejilla {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 16px; }}
    .grafico {{ background: #1a1a1a; border-radius: 10px; padding: 8px; margin-top: 16px; min-width: 0; }}
    .sin-datos {{ padding: 16px; color: #9ca3af; }}
    table {{ width: 100%; border-collapse: collapse; background: #1a1a1a; border-radius: 10px; overflow: hidden; }}
    th, td {{ padding: 10px 12px; text-align: right; border-bottom: 1px solid #262626; }}
    th:first-child, td:first-child {{ text-align: left; }}
    th {{ background: #262626; color: {NARANJA}; font-weight: 600; }}
    tr.total td {{ font-weight: 700; border-top: 2px solid {NARANJA}; }}
    .tabla-scroll {{ overflow-x: auto; }}
    footer {{ margin-top: 40px; color: #6b7280; font-size: 12px; text-align: center; }}
    @media (max-width: 500px) {{ .rejilla {{ grid-template-columns: 1fr; }} }}

</style>
</head>
<body>
<div class="contenido">
    <header>
        <div class="marca">{DATOS_GIMNASIO['nombre'].upper()}</div>
        <h1>{titulo}</h1>
        <div class="fecha">Generado el {generado}</div>
    </header>
    {contenido}
    <footer>{DATOS_GIMNASIO['nombre']} · {DATOS_GIMNASIO['direccion']} · CIF {DATOS_GIMNASIO['cif']}</footer>
</div>
<script>
    // Cada gráfico se dibuja según se lee la página, antes de que la rejilla tenga su tamaño
    // final. Al terminar de cargar, se ajustan todos a la caja que les ha tocado.
    window.addEventListener("load", function () {{
        document.querySelectorAll(".plotly-graph-div").forEach(function (g) {{ Plotly.Plots.resize(g); }});
    }});
</script>
</body>
</html>"""


def tarjetas_resumen(altas, facturacion, gastos):
    """Las 4 cifras principales. Sirven igual para el informe anual y el mensual."""
    beneficio = facturacion - gastos
    margen = beneficio / facturacion * 100 if facturacion else 0
    clase = "positivo" if beneficio >= 0 else "negativo"
    return f"""
    <div class="tarjetas">
        {tarjeta("Altas", altas, "alumnos nuevos")}
        {tarjeta("Facturación", euros(facturacion), "cuotas cobradas")}
        {tarjeta("Gastos", euros(gastos))}
        {tarjeta("Beneficio bruto", euros(beneficio), f"margen del {margen:.1f} %".replace(".", ","), clase)}
    </div>"""


# ---------- Informe anual ----------

def informe_anual(cursor, anio):
    hoy = date.today()
    ultimo_mes = hoy.month if anio == hoy.year else 12   # el año en curso, solo hasta hoy

    # Pasar todo a diccionarios {mes: valor} para recorrerlos igual
    ingresos = {int(mes_cuota[5:7]): total
                for mes_cuota, total in calcular_ingresos_por_mes(cursor, anio).items()}
    altas = {periodo.month: n for periodo, n in alumnos_nuevos_por_mes(cursor, anio).items()}
    gastos = gastos_por_mes(cursor, anio)

    meses = list(range(1, ultimo_mes + 1))
    nombres = [MESES[m - 1] for m in meses]
    lista_ingresos = [ingresos.get(m, 0) for m in meses]
    lista_gastos = [gastos.get(m, 0) for m in meses]
    lista_beneficio = [i - g for i, g in zip(lista_ingresos, lista_gastos)]
    lista_altas = [altas.get(m, 0) for m in meses]

    # 1. Ingresos frente a gastos, con la línea del beneficio
    fig = go.Figure()
    fig.add_bar(name="Ingresos", x=nombres, y=lista_ingresos, marker_color=NARANJA,
                hovertemplate="%{y:,.2f} €")
    fig.add_bar(name="Gastos", x=nombres, y=lista_gastos, marker_color=GRIS,
                hovertemplate="%{y:,.2f} €")
    fig.add_scatter(name="Beneficio", x=nombres, y=lista_beneficio, mode="lines+markers",
                    line=dict(color=VERDE, width=3), hovertemplate="%{y:,.2f} €")
    fig.update_layout(barmode="group", hovermode="x unified")
    grafico_balance = grafico(estilo_grafico(fig, "Ingresos, gastos y beneficio por mes"))

    # 2. Altas por mes
    fig = go.Figure(go.Bar(x=nombres, y=lista_altas, marker_color=NARANJA,
                        text=lista_altas, textposition="outside",
                        hovertemplate="%{x}: %{y} altas<extra></extra>"))
    grafico_altas = grafico(estilo_grafico(fig, "Altas por mes"))

    # 3 y 4. Circulares: gastos por categoría e ingresos por tipo de cuota
    categorias = gastos_por_categoria(cursor, anio)
    grafico_categorias = grafico_circular("Gastos por categoría",
                                        [c for c, _ in categorias], [t for _, t in categorias])
    tipos = ingresos_por_tipo_cuota_anual(cursor, anio)
    grafico_tipos = grafico_circular("Ingresos por tipo de cuota",
                                    [t for t, _, _ in tipos], [imp for _, _, imp in tipos])

    # 5. Tabla mes a mes
    filas = [(MESES[m - 1], a, euros(i), euros(g), euros(i - g))
            for m, a, i, g in zip(meses, lista_altas, lista_ingresos, lista_gastos)]
    total = ("Total", sum(lista_altas), euros(sum(lista_ingresos)),
            euros(sum(lista_gastos)), euros(sum(lista_beneficio)))
    tabla_meses = tabla(["Mes", "Altas", "Ingresos", "Gastos", "Beneficio"], filas, total)

    contenido = f"""
    {tarjetas_resumen(sum(lista_altas), sum(lista_ingresos), sum(lista_gastos))}
    {grafico_balance}
    <div class="rejilla">
        {grafico_altas}
        {grafico_categorias}
    </div>
    <div class="rejilla">
        {grafico_tipos}
    </div>
    <h2>Resumen mes a mes</h2>
    <div class="tabla-scroll">{tabla_meses}</div>"""
    return pagina_html(f"Informe anual {anio}", contenido)


# ---------- Informe mensual (te toca a ti) ----------

def informe_mensual(cursor, anio, mes):
    # 1. Cifras del mes
    altas_por_mes = {periodo.month: n
                    for periodo, n in alumnos_nuevos_por_mes(cursor, anio).items()}
    altas = int(altas_por_mes.get(mes, 0))

    tipos = ingresos_por_tipo_cuota(cursor, f"{anio}-{mes:02d}-01")
    facturacion = sum(importe for _, _, importe in tipos)

    gastos = gastos_por_mes(cursor, anio).get(mes, 0)

    # 2. Circular: gastos por categoría
    categorias = gastos_por_categoria(cursor, anio, mes)
    grafico_categorias = grafico_circular("Gastos por categoría",
                                        [c for c, _ in categorias],
                                        [t for _, t in categorias])

    # 3. Circular: ingresos por tipo de cuota
    grafico_tipos = grafico_circular("Ingresos por tipo de cuota",
                                        [t for t, _, _ in tipos],
                                        [imp for _, _, imp in tipos])

    # 4. Barras horizontales: asistencias por actividad
    asistencias = asistencias_por_actividad(cursor, anio, mes)
    nombres_actividades = [a for a, _ in asistencias]
    totales = [n for _, n in asistencias]
    fig = go.Figure(go.Bar(
        x=totales, y=nombres_actividades, orientation="h", marker_color=NARANJA,
        text=totales, textposition="outside",
        hovertemplate="%{y}: %{x} asistencias<extra></extra>",
    ))
    fig.update_yaxes(autorange="reversed")      # la actividad con más asistencias, arriba
    grafico_asistencias = grafico(estilo_grafico(fig, "Asistencias por actividad"))

    # 5. Tabla con los gastos del mes
    gastos_mes = gastos_del_mes(cursor, anio, mes)
    filas = [(f"{fecha[8:10]}/{fecha[5:7]}/{fecha[:4]}", concepto, categoria, euros(importe))
             for fecha, concepto, categoria, importe in gastos_mes]
    total = ("Total", "", "", euros(sum(importe for _, _, _, importe in gastos_mes)))
    tabla_gastos = tabla(["Fecha", "Concepto", "Categoría", "Importe"], filas, total)

    contenido = f"""
    {tarjetas_resumen(altas, facturacion, gastos)}
    <div class="rejilla">
        {grafico_categorias}
        {grafico_tipos}
    </div>
    {grafico_asistencias}
    <h2>Gastos del mes</h2>
    <div class="tabla-scroll">{tabla_gastos}</div>"""
    return pagina_html(f"Informe de {MESES[mes - 1].lower()} {anio}", contenido)


# ---------- Punto de entrada ----------

def generar_informe(cursor, anio, mes=None):
    """Crea el informe (anual si mes es None, mensual si no) y devuelve la ruta del archivo."""
    if mes is None:
        contenido = informe_anual(cursor, anio)
        nombre = f"informe_{anio}.html"
    else:
        contenido = informe_mensual(cursor, anio, mes)
        nombre = f"informe_{anio}-{mes:02d}.html"

    CARPETA_INFORMES.mkdir(exist_ok=True)
    ruta = CARPETA_INFORMES / nombre
    ruta.write_text(contenido, encoding="utf-8")
    return ruta
