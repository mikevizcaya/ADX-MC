from io import BytesIO

import plotly.io as pio
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from charts import build_chart


def _figure_png(fig, width=1200, height=650):
    fig.update_layout(
        width=width,
        height=height,
        margin=dict(l=45, r=25, t=65, b=35),
    )
    return pio.to_image(
        fig,
        format="png",
        width=width,
        height=height,
        scale=1.35,
        engine="kaleido",
    )


def _draw_chart(c, png_bytes, x, y, max_w, max_h):
    image = ImageReader(BytesIO(png_bytes))
    iw, ih = image.getSize()
    scale = min(max_w / iw, max_h / ih)
    w = iw * scale
    h = ih * scale
    c.drawImage(
        image,
        x + (max_w - w) / 2,
        y + (max_h - h) / 2,
        width=w,
        height=h,
        preserveAspectRatio=True,
        mask="auto",
    )


def create_event_pdf(
    analyzed,
    source_index: int,
    asset_label: str,
    timeframe_seconds: int,
    theme: str = "Blanco",
):
    """
    Crea PDF carta vertical de 3 páginas:
    página 1: Estándar (Todo) + Antes
    página 2: Inicio + Fin con ADX estándar
    página 3: Inicio + Fin con ADX-MC, reemplazando el ADX estándar
    """
    images = {}

    # Páginas 1 y 2: ADX estándar.
    for mode in ["Todo", "Antes", "Inicio", "Fin"]:
        fig = build_chart(
            analyzed=analyzed,
            source_index=source_index,
            mode=mode,
            asset_label=asset_label,
            theme=theme,
            adx_variant="standard",
        )
        try:
            images[mode] = _figure_png(fig)
        except Exception as exc:
            raise RuntimeError(
                "No fue posible convertir las gráficas estándar a imagen. "
                "Verifica que Kaleido se haya instalado correctamente."
            ) from exc

    # Página 3: ADX-MC sustituye al estándar; no se superponen.
    for mode in ["Inicio", "Fin"]:
        fig_mc = build_chart(
            analyzed=analyzed,
            source_index=source_index,
            mode=mode,
            asset_label=asset_label,
            theme=theme,
            adx_variant="mc",
        )
        try:
            images[f"{mode}_MC"] = _figure_png(fig_mc)
        except Exception as exc:
            raise RuntimeError(
                "No fue posible convertir las gráficas ADX-MC a imagen. "
                "Verifica que Kaleido se haya instalado correctamente."
            ) from exc

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    page_w, page_h = letter

    margin_x = 24
    top = 24
    bottom = 22
    header_h = 34
    gap = 8
    usable_w = page_w - (2 * margin_x)
    usable_h = page_h - top - bottom - header_h
    chart_h = (usable_h - gap) / 2

    selected = analyzed.loc[source_index]
    event_time = str(selected.get("datetime_mexico", ""))
    frame_min = max(1, int(timeframe_seconds // 60))

    pages = [
        ("Página 1 - Estándar / Antes", "Todo", "Antes"),
        ("Página 2 - Inicio / Fin - ADX estándar", "Inicio", "Fin"),
        ("Página 3 - Inicio / Fin - ADX-MC", "Inicio_MC", "Fin_MC"),
    ]

    for page_title, upper_mode, lower_mode in pages:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin_x, page_h - top, f"Trading Analitic - {asset_label}")

        c.setFont("Helvetica", 8)
        c.drawRightString(
            page_w - margin_x,
            page_h - top,
            f"{event_time} | {frame_min} min | Fondo {theme}",
        )

        c.setFont("Helvetica-Bold", 9)
        c.drawString(margin_x, page_h - top - 14, page_title)

        _draw_chart(
            c,
            images[upper_mode],
            margin_x,
            bottom + chart_h + gap,
            usable_w,
            chart_h,
        )
        _draw_chart(
            c,
            images[lower_mode],
            margin_x,
            bottom,
            usable_w,
            chart_h,
        )
        c.showPage()

    c.save()
    buffer.seek(0)
    return buffer.getvalue()
