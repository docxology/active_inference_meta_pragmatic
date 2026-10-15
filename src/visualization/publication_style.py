"""Typography and export contracts shared by every retained publication figure."""

from pathlib import Path
from typing import Final

from matplotlib.figure import Figure
from matplotlib.text import Text

MINIMUM_FONT: Final = 12.0
PUBLICATION_STYLE: Final = {
    "font.family": "DejaVu Sans",
    "font.size": 14,
    "axes.labelsize": 14,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.labelcolor": "#23333D",
    "axes.edgecolor": "#64717A",
    "axes.linewidth": 0.8,
    "xtick.color": "#23333D",
    "ytick.color": "#23333D",
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "legend.fontsize": 12,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "lines.linewidth": 2.2,
    "grid.color": "#BCC5CB",
    "grid.linewidth": 0.65,
    "legend.frameon": False,
    "pdf.fonttype": 42,
    "svg.fonttype": "none",
    "savefig.dpi": 300,
}


def save_publication_figure(fig: Figure, path: Path) -> None:
    """Enforce source font sizes before export; preserve larger intentional type."""
    for label in fig.findobj(match=Text):
        label.set_fontsize(max(MINIMUM_FONT, label.get_fontsize()))
    fig.savefig(path, dpi=300, bbox_inches="tight")
    if path.suffix == ".svg":
        path.write_text(
            "\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n"
        )
