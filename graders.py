from typing import Any, Dict

def easy_grader(state: Dict[str, Any]) -> float:
    """Grader for the Easy task."""
    if state.get('battery_charge_mwh', 0.0) >= 40.0:
        return 1.0
    return 0.0

def medium_grader(state: Dict[str, Any]) -> float:
    """Grader for the Medium task."""
    budget = state.get('budget_remaining', 0.0)
    return max(0.0, min(budget / 1000.0, 1.0))

def hard_grader(state: Dict[str, Any]) -> float:
    """Grader for the Hard task."""
    if state.get('blackout_occurred', False):
        return 0.0
    budget = state.get('budget_remaining', 0.0)
    return max(0.0, min(budget / 1000.0, 1.0))
