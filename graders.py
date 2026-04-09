from typing import Any

def safe_extract(args: tuple, kwargs: dict, key: str, default: float) -> float:
    """Bulletproof extraction that handles trajectories, Pydantic models, and dicts without crashing."""
    try:
        # 1. Check kwargs for state
        if 'state' in kwargs and isinstance(kwargs['state'], dict):
            return float(kwargs['state'].get(key, default))
        
        # 2. Check args (could be a single state dict, or a trajectory list of steps)
        if args:
            data = args[0]
            if isinstance(data, list) and len(data) > 0:
                data = data[-1]  # Get the final step in the trajectory
                
            if hasattr(data, 'observation'):
                data = data.observation  # Extract observation from StepResult
                
            if hasattr(data, 'model_dump'):
                data = data.model_dump()
            elif hasattr(data, '__dict__'):
                data = vars(data)
                
            if isinstance(data, dict):
                return float(data.get(key, default))
    except Exception:
        pass
    return float(default)

def easy_grader(*args, **kwargs) -> float:
    val = safe_extract(args, kwargs, 'battery_charge_mwh', 0.0)
    return 1.0 if val >= 40.0 else 0.0

def medium_grader(*args, **kwargs) -> float:
    budget = safe_extract(args, kwargs, 'budget_remaining', 0.0)
    return max(0.0, min(budget / 1000.0, 1.0))

def hard_grader(*args, **kwargs) -> float:
    blackout = safe_extract(args, kwargs, 'blackout_occurred', 0.0)
    if blackout:
        return 0.0
    budget = safe_extract(args, kwargs, 'budget_remaining', 0.0)
    return max(0.0, min(budget / 1000.0, 1.0))
