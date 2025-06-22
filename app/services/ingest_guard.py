from datetime import datetime, timedelta, timezone
from typing import Dict

MIN_GAP = timedelta(minutes=30)
_last: Dict[str, datetime] = {}


def should_run(key: str) -> bool:
    """Check if enough time has passed since the last run for this key."""
    now = datetime.now(timezone.utc)
    if key not in _last or now - _last[key] > MIN_GAP:
        _last[key] = now
        return True
    return False 