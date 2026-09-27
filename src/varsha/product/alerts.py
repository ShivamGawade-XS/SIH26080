"""
Indicative Alert Level Classification Engine (Deliverable D4).
Evaluates district-level risk from probability distributions and spatial fractions.
"""

from dataclasses import dataclass

from varsha.config import VarshaConfig


@dataclass
class AlertStatus:
    level: str  # green, yellow, orange, red
    label: str  # No Warning, Watch, Alert, Warning
    action: str  # Normal Conditions, Be Updated, Be Prepared, Take Action
    glyph: str  # circle, square, triangle, diamond
    color_light: str
    color_dark: str


ALERT_METADATA = {
    "red": {
        "label": "Warning",
        "action": "Take Action",
        "glyph": "diamond",
        "color_light": "#B71C1C",
        "color_dark": "#EF5350",
    },
    "orange": {
        "label": "Alert",
        "action": "Be Prepared",
        "glyph": "triangle",
        "color_light": "#C75100",
        "color_dark": "#FF9800",
    },
    "yellow": {
        "label": "Watch",
        "action": "Be Updated",
        "glyph": "square",
        "color_light": "#9A6A00",
        "color_dark": "#FBC02D",
    },
    "green": {
        "label": "No Warning",
        "action": "Normal Conditions",
        "glyph": "circle",
        "color_light": "#2E7D32",
        "color_dark": "#4CAF50",
    },
}


def evaluate_district_alert(
    p50_mm: float,
    max_cell_prob_64: float,
    max_cell_prob_115: float,
    expected_area_fraction_64: float,
    expected_area_fraction_15: float,
    config: VarshaConfig | None = None,
) -> AlertStatus:
    """
    Classify district alert level based on configurable trigger conditions.
    Enforces that all labels indicate 'Indicative; not an official IMD warning'.
    """
    # Red Warning Condition
    if (
        max_cell_prob_115 >= 0.40
        or expected_area_fraction_64 >= 0.50
        or max_cell_prob_64 >= 0.75
        or p50_mm >= 115.6
    ):
        meta = ALERT_METADATA["red"]
        return AlertStatus(level="red", **meta)

    # Orange Alert Condition
    if (
        max_cell_prob_64 >= 0.45
        or expected_area_fraction_64 >= 0.25
        or max_cell_prob_115 >= 0.20
        or p50_mm >= 64.5
    ):
        meta = ALERT_METADATA["orange"]
        return AlertStatus(level="orange", **meta)

    # Yellow Watch Condition
    if max_cell_prob_64 >= 0.20 or expected_area_fraction_15 >= 0.40 or p50_mm >= 35.5:
        meta = ALERT_METADATA["yellow"]
        return AlertStatus(level="yellow", **meta)

    # Green Default
    meta = ALERT_METADATA["green"]
    return AlertStatus(level="green", **meta)
