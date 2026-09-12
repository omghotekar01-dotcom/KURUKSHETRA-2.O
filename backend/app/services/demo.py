from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.schemas.incident import DemoScenario


_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "demo_scenarios.json"


@lru_cache(maxsize=1)
def load_demo_scenarios() -> tuple[DemoScenario, ...]:
    """Load deterministic, version-controlled demo incidents.

    The fixtures are intentionally local so the judging flow remains available
    even when external APIs or internet connectivity are unavailable.
    """
    raw = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
    return tuple(DemoScenario.model_validate(item) for item in raw)


def list_demo_scenarios() -> list[DemoScenario]:
    return list(load_demo_scenarios())


def get_demo_scenario(scenario_id: str) -> DemoScenario | None:
    normalized = scenario_id.strip().upper()
    return next((item for item in load_demo_scenarios() if item.id.upper() == normalized), None)
