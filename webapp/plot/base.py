import io
import base64
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.dates import date2num
from matplotlib.colors import ListedColormap


def plot_to_base64(fig, dpi=300):
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def gradient_line(ax, x, y, cmap="RdYlGn_r", alpha=0.7):
    """
    Disegna una linea con gradiente cromatico in base alla variazione tra i punti.
    Rosso = salita (delta y > 0), Verde = discesa (delta y < 0).
    """


    x = np.array(date2num(x))
    y = np.array(y)

    if len(x) < 2 or len(y) < 2 or np.all(np.isnan(y)) or np.all(y == y[0]):
        ax.plot(x, y, color="lightcoral" if y[-1] > y[0] else "lightgreen", linewidth=2)
        return

    # Segmenti
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # Delta y
    slope = np.diff(y)
    slope = np.clip(slope, -1, 1)

    # Colormap
    pastel_cmap = ListedColormap([
        "#1f811f",  # verde chiaro
        "#3cb371",  # verde medio
        "#90ee90",  # verde chiaro
        "#f0c68c",  # arancione chiaro
        "#f0a68c",  # arancione
        "#f08080",  # rosso chiaro
        "#f05050",  # rosso
        "#f02020",  # rosso scuro
        "#f00000"   # rosso intenso
    ])

    norm = plt.Normalize(-1, 1)
    lc = LineCollection(segments, cmap=pastel_cmap, norm=norm, alpha=alpha)
    lc.set_array(slope)
    lc.set_linewidth(2.2)
    ax.add_collection(lc)

    ax.set_xlim(np.nanmin(x), np.nanmax(x))
    ax.set_ylim(np.nanmin(y), np.nanmax(y))

