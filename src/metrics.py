import time
from typing import Dict

# Simple in-memory metrics tracker
_metrics: Dict[str, float | int] = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "avg_response_time_ms": 0.0,
    "avg_translation_length": 0.0,
}

def record(success: bool, start_time: float, translated_text: str = ""):
    """Record each translation event with latency and result stats."""
    duration_ms = (time.time() - start_time) * 1000
    _metrics["total_requests"] += 1
    if success:
        _metrics["successful_requests"] += 1
    else:
        _metrics["failed_requests"] += 1

    # Update rolling average for latency
    n = _metrics["total_requests"]
    _metrics["avg_response_time_ms"] = (
        (_metrics["avg_response_time_ms"] * (n - 1)) + duration_ms
    ) / n

    # Track average translation length
    length = len(translated_text)
    _metrics["avg_translation_length"] = (
        (_metrics["avg_translation_length"] * (n - 1)) + length
    ) / n


def get_metrics() -> Dict[str, float | int]:
    """Return a snapshot of current metrics."""
    return dict(_metrics)
