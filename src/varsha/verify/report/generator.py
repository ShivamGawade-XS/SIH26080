"""
Verification Report Generator (Deliverable D5).
Renders the standalone scientific verification report as clean HTML using Jinja2
with data dynamically computed from run artifacts.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Template

TEMPLATE_PATH = Path(__file__).parent / "template.html"


def generate_html_report(
    run_id: str,
    data_mode: str,
    profile: str,
    n_days: int,
    model_ladder: list[dict[str, Any]],
    paired_comparisons: list[dict[str, Any]],
    controls: list[dict[str, Any]],
    fss_table: list[dict[str, Any]],
    output_path: Path | str,
) -> Path:
    """Render and save the standalone verification HTML report."""
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        template_str = f.read()

    template = Template(template_str)

    provenance_statement = (
        "SYNTHETIC EXPERIMENT MODE: Demonstrates pipeline recovery of known physical structures under controlled ground-truth conditions."
        if data_mode == "synthetic"
        else "REAL DATA MODE: Ingested GFS forecasts and IMD gridded observations."
    )

    rendered_html = template.render(
        run_id=run_id,
        data_mode=data_mode,
        profile=profile,
        n_days=n_days,
        model_ladder=model_ladder,
        paired_comparisons=paired_comparisons,
        controls=controls,
        fss_table=fss_table,
        provenance_statement=provenance_statement,
    )

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(rendered_html)

    return out_file
