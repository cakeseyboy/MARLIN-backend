import pathlib
from typing import Dict, List, Any

import yaml

SCHEDULE_FILE = pathlib.Path(__file__).parents[2] / "config" / "ingest_schedule.yml"


def load_station_times() -> Dict[str, List[str]]:
    """Load station-specific timing windows from YAML config."""
    with SCHEDULE_FILE.open() as fh:
        raw: Dict[str, Any] = yaml.safe_load(fh)
    return {code: list(slots.values()) for code, slots in raw.items()} 