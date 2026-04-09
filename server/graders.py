# graders.py

def safe_extract(args, kwargs, key: str, default: float) -> float:
    """Bulletproof extraction that handles any data structure the bot throws at it."""
    try:
        data = args[0] if args else kwargs.get('trajectory', kwargs.get('state'))
        last_step = data[-1] if isinstance(data, list) else data
        
        # Dig down to the observation dictionary
        obs = getattr(last_step, 'observation', last_step)
        if hasattr(obs, 'model_dump'):
            obs = obs.model_dump()
        elif hasattr(obs, '__dict__'):
            obs = vars(obs)
            
        if isinstance(obs, dict):
            return float(obs.get(key, default))
        return float(getattr(obs, key, default))
    except Exception:
        return float(default)

def easy_grader(*args, **kwargs) -> float:
    val = safe_extract(args, kwargs, 'battery_charge_mwh', 0.0)
    return 1.0 if val >= 40.0 else 0.0

def medium_grader(*args, **kwargs) -> float:
    val = safe_extract(args, kwargs, 'budget_remaining', 0.0)
    return max(0.0, min(val / 1000.0, 1.0))

def hard_grader(*args, **kwargs) -> float:
    blackout = safe_extract(args, kwargs, 'blackout_occurred', 0.0)
    if blackout:
        return 0.0
    val = safe_extract(args, kwargs, 'budget_remaining', 0.0)
    return max(0.0, min(val / 1000.0, 1.0))
