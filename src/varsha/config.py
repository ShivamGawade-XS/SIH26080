"""
Configuration and Profile Management for Varsha.
"""

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

DEFAULT_CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "configs"


class DomainConfig(BaseModel):
    name: str = "india_monsoon"
    lat_min: float = 6.0
    lat_max: float = 38.0
    lon_min: float = 68.0
    lon_max: float = 98.0


class ProfileConfig(BaseModel):
    profile_name: str = "demo-fast"
    grid_resolution: float = 1.0
    train_seasons: list[str] = Field(default_factory=lambda: ["S01", "S02", "S03", "S04"])
    cal_seasons: list[str] = Field(default_factory=lambda: ["S05"])
    test_seasons: list[str] = Field(default_factory=lambda: ["S06"])
    pseudo_prospective_seasons: list[str] = Field(default_factory=lambda: ["S07"])
    bootstrap_resamples: int = 50
    regime_dependent_bias: bool = True
    seed: int = 42


class VarshaConfig(BaseModel):
    data_mode: str = "synthetic"
    domain: DomainConfig = Field(default_factory=DomainConfig)
    profile: ProfileConfig = Field(default_factory=ProfileConfig)
    leads: list[int] = Field(default_factory=lambda: [1, 2, 3, 4, 5])
    raw_configs: dict[str, Any] = Field(default_factory=dict)


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}


def get_config(
    profile_name: str = "demo-fast",
    config_dir: Path | None = None,
    data_mode: str | None = None,
) -> VarshaConfig:
    cdir = config_dir or DEFAULT_CONFIG_DIR

    data_yaml = load_yaml(cdir / "data.yaml")
    regimes_yaml = load_yaml(cdir / "regimes.yaml")
    models_yaml = load_yaml(cdir / "models.yaml")
    alerts_yaml = load_yaml(cdir / "alerts.yaml")

    profile_path = cdir / "profiles" / f"{profile_name}.yaml"
    profile_yaml = load_yaml(profile_path)

    mode = str(data_mode or os.getenv("DATA_MODE", "synthetic") or "synthetic")

    domain_dict = data_yaml.get("domain", {})
    domain = DomainConfig(**domain_dict) if domain_dict else DomainConfig()

    profile = (
        ProfileConfig(**profile_yaml) if profile_yaml else ProfileConfig(profile_name=profile_name)
    )
    leads = data_yaml.get("leads", [1, 2, 3, 4, 5])

    return VarshaConfig(
        data_mode=mode,
        domain=domain,
        profile=profile,
        leads=leads,
        raw_configs={
            "data": data_yaml,
            "regimes": regimes_yaml,
            "models": models_yaml,
            "alerts": alerts_yaml,
            "profile": profile_yaml,
        },
    )
