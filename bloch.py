"""Accessible Bloch sphere: an inline SVG (with title/description) plus a text description."""
import math
from html import escape

CX = CY = 120
R = 80
SKEW = 0.4  # oblique projection: the x axis points toward the viewer, lower-left
VECTOR_COLOR = "#D55E00"  # colour-blind-safe vermillion
VECTOR_COLOR_HC = "#FFD700"
PANEL = {False: ("#FFFFFF", "#1F2328"), True: ("#000000", "#FFFFFF")}  # (background, ink)


def _project(x: float, y: float, z: float) -> tuple:
    return CX + R * (y - SKEW * x), CY - R * (z - SKEW * x)


def _curve(points) -> str:
    return "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in points)


def describe(x: float, y: float, z: float, T: dict) -> str:
    """Plain-language description of the Bloch vector (used as alt text and caption)."""
    where = T["bloch_where"]
    if z >= 0.99:
        place = where["north"]
    elif z <= -0.99:
        place = where["south"]
    elif abs(z) < 0.01:
        place = where["equator"]
    else:
        place = where["upper"] if z > 0 else where["lower"]
    p0 = (1 + z) / 2 * 100
    return T["bloch_desc"].format(x=x, y=y, z=z, where=place, p0=p0, p1=100 - p0)


def bloch_svg(x: float, y: float, z: float, title: str, desc: str, high_contrast: bool = False) -> str:
    """SVG of the Bloch sphere on its own solid panel, so it reads in any theme.

    Meant for st.image: st.html strips <svg> entirely, and images cannot inherit the page's
    text colour, hence the fixed colours and the background rectangle.
    """
    bg, ink = PANEL[high_contrast]
    n = 72
    equator = [_project(math.cos(2 * math.pi * i / n),
                        math.sin(2 * math.pi * i / n), 0) for i in range(n + 1)]
    meridian = [_project(math.cos(2 * math.pi * i / n), 0,
                         math.sin(2 * math.pi * i / n)) for i in range(n + 1)]
    tx, ty = _project(x, y, z)
    color = VECTOR_COLOR_HC if high_contrast else VECTOR_COLOR
    axes = "".join(
        f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" '
        f'stroke="{ink}" stroke-width="1" opacity="0.6"/>'
        for a, b in (
            (_project(0, 0, -1), _project(0, 0, 1)),
            (_project(0, -1, 0), _project(0, 1, 0)),
            (_project(-1, 0, 0), _project(1, 0, 0)),
        )
    )
    px, py = _project(1.18, 0, 0)
    qx, qy = _project(0, 1.0, 0)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 250" width="240" height="250" '
        'role="img" aria-labelledby="bloch-title bloch-desc">'
        f'<title id="bloch-title">{escape(title)}</title>'
        f'<desc id="bloch-desc">{escape(desc)}</desc>'
        f'<rect width="240" height="250" rx="8" fill="{bg}"/>'
        f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="none" stroke="{ink}" stroke-width="2"/>'
        f'<path d="{_curve(equator)}" fill="none" stroke="{ink}" stroke-width="1" '
        'stroke-dasharray="4 3" opacity="0.6"/>'
        f'<path d="{_curve(meridian)}" fill="none" stroke="{ink}" stroke-width="1" '
        'stroke-dasharray="4 3" opacity="0.6"/>'
        f"{axes}"
        f'<line x1="{CX}" y1="{CY}" x2="{tx:.1f}" y2="{ty:.1f}" stroke="{color}" stroke-width="4" '
        'stroke-linecap="round"/>'
        f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="6" fill="{color}" stroke="{ink}" stroke-width="1"/>'
        f'<g font-size="15" font-family="sans-serif" fill="{ink}" text-anchor="middle">'
        f'<text x="{CX}" y="{CY - R - 8}">|0⟩</text>'
        f'<text x="{CX}" y="{CY + R + 20}">|1⟩</text>'
        f'<text x="{px - 6:.1f}" y="{py + 16:.1f}">x</text>'
        f'<text x="{qx + 14:.1f}" y="{qy + 5:.1f}">y</text>'
        "</g></svg>"
    )
