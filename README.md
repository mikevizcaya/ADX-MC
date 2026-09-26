# Trading Analitic — Versión 3

Esta versión incorpora las gráficas interactivas del evento JAPY2.

## Novedades

Al seleccionar una señal en la tabla, la app muestra una gráfica con cuatro modos:

- **Todo**: 15 velas previas + vela seleccionada + 15 posteriores.
- **Antes**: 14 velas previas + la vela inmediatamente anterior como última visible.
- **Inicio**: 15 velas previas + la vela seleccionada reducida a su OPEN.
- **Fin**: 15 velas previas + la vela seleccionada completa hasta CLOSE.

La gráfica incluye:

- Velas.
- LSMA OPEN 7.
- LSMA CLOSE 7.
- WMA OPEN 7.
- Triángulos amarillos JAPY2.
- ADX 14.
- DI+ y DI-.
- Zoom con rueda del mouse.

## Actualizar GitHub

Reemplaza:
- `app.py`
- `requirements.txt`

Añade:
- `charts.py`

Mantén:
- `iqoption_service.py`
- `japy2.py`

Después del commit, Streamlit Community Cloud debería redeplegar automáticamente.
