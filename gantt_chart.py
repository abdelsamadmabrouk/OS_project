"""
gantt_chart.py
──────────────
Gantt Chart widget for the CPU Scheduler project.

Contract
────────
Input  : segments — list of [pid, start_time, end_time]
         e.g. [["P1", 0, 24], ["P2", 24, 27], ["P3", 27, 30]]

Public API
──────────
    widget = GanttWidget(parent=None)
    widget.update_segments(segments)   # call on every tick or at completion
    widget.reset()                     # call when starting a new run
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker
import hashlib


# ── Colour mapping ────────────────────────────────────────────────────────────
# Uses the HSV colormap sampled via an MD5 hash of the pid.
# Deterministic — same pid always yields the same colour across app restarts.

from matplotlib import colormaps

def _pid_color(pid: str) -> tuple:
    """Return a consistent RGBA colour for a given pid using HSV colormap."""
    # hashlib ensures true determinism across different Python sessions
    hash_int = int(hashlib.md5(str(pid).encode()).hexdigest(), 16)
    t = (hash_int % 1000) / 1000.0
    return colormaps["hsv"](t)


# ── Widget ────────────────────────────────────────────────────────────────────

class GanttWidget(QWidget):
    """
    A PyQt6 widget that renders a live single-row Gantt chart using matplotlib.

    Usage
    ─────
        gantt = GanttWidget()
        layout.addWidget(gantt)

        # On each scheduler tick (or after batch completion):
        gantt.update_segments([["P1", 0, 5], ["P2", 5, 9], ...])
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self._segments: list = []              # current segment list

        # ── Matplotlib figure setup ──────────────────────────────────────────
        self._fig = Figure(figsize=(10, 1.8), dpi=100, facecolor="#1E1E2E")
        self._ax  = self._fig.add_subplot(111)
        self._fig.subplots_adjust(left=0.02, right=0.98, top=0.72, bottom=0.38)

        self._canvas = FigureCanvas(self._fig)
        self._canvas.setSizePolicy(QSizePolicy.Policy.Expanding,
                                   QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._canvas)

        self._init_axes()

    # ── Private helpers ───────────────────────────────────────────────────────

    def _init_axes(self):
        ax = self._ax
        ax.set_facecolor("#1E1E2E")

        ax.set_yticks([])
        ax.set_ylim(0, 1)

        ax.tick_params(axis="x", colors="#CDD6F4", labelsize=8)
        ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())

        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.set_xlim(0, 1)

    def _redraw(self):
        ax = self._ax
        
        # Clear axes AND figure legends to prevent memory leaks over multiple ticks
        ax.clear()
        self._fig.legends.clear()
        
        self._init_axes()

        if not self._segments:
            self._canvas.draw()
            return

        max_time   = max(seg[2] for seg in self._segments)
        legend_map: dict[str, mpatches.Patch] = {}

        for pid, start, end in self._segments:
            color    = _pid_color(str(pid))
            duration = end - start

            # Main bar
            ax.broken_barh(
                [(start, duration)],
                (0.08, 0.84),
                facecolors=color,
                edgecolors="#1E1E2E",
                linewidth=1.2,
            )

            # Process label inside bar (only if wide enough)
            if duration >= max(1, max_time * 0.04):
                ax.text(
                    start + duration / 2, 0.5,
                    str(pid),
                    ha="center", va="center",
                    fontsize=8, fontweight="bold",
                    color="#1E1E2E",
                )

            if str(pid) not in legend_map:
                legend_map[str(pid)] = mpatches.Patch(
                    facecolor=color, label=str(pid), edgecolor="#1E1E2E"
                )

        # X-axis: mark every boundary
        boundaries = sorted({seg[1] for seg in self._segments} |
                             {seg[2] for seg in self._segments})
        ax.set_xticks(boundaries)
        ax.set_xlim(0, max_time + max_time * 0.01)
        ax.tick_params(axis="x", colors="#CDD6F4", labelsize=7.5)

        # Legend
        self._fig.legend(
            handles=list(legend_map.values()),
            loc="upper center",
            ncol=min(len(legend_map), 8),
            bbox_to_anchor=(0.5, 1.0),
            frameon=False,
            fontsize=8,
            labelcolor="#CDD6F4",
        )

        self._canvas.draw()

    # ── Public API ────────────────────────────────────────────────────────────

    def update_segments(self, segments: list):
        """
        Refresh the Gantt chart with the latest segment list.

        Parameters
        ──────────
        segments : list of [pid, start_time, end_time]
            The complete segment history up to the current tick.
            Consecutive entries for the same pid are merged visually
            only if contiguous — pass raw tick-by-tick data freely,
            the widget will consolidate automatically.
        """
        self._segments = self._consolidate(segments)
        self._redraw()

    def reset(self):
        """Clear the chart for a new run."""
        self._segments = []
        self._redraw()

    # ── Segment consolidation ─────────────────────────────────────────────────

    @staticmethod
    def _consolidate(segments: list) -> list:
        """
        Merge adjacent segments of the same pid into a single bar.

        [P1,0,1],[P1,1,2],[P2,2,3]  →  [P1,0,2],[P2,2,3]
        """
        if not segments:
            return []

        merged = [list(segments[0])]
        for pid, start, end in segments[1:]:
            if str(pid) == str(merged[-1][0]) and start == merged[-1][2]:
                merged[-1][2] = end          # extend last bar
            else:
                merged.append([pid, start, end])
        return merged
