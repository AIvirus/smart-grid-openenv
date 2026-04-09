from typing import Any, Dict, List

def easy_grader(trajectory: List[Dict[str, Any]]) -> float:
    """Grader for the Easy task (Surplus Storage)."""
    if not trajectory:
        return 0.0
    rewards = [step.get("reward", 0.0) for step in trajectory]
    score = sum(rewards) / len(rewards) if rewards else 0.0
    return min(max(score, 0.0), 1.0)

def medium_grader(trajectory: List[Dict[str, Any]]) -> float:
    """Grader for the Medium task (Peak Shaving)."""
    if not trajectory:
        return 0.0
    rewards = [step.get("reward", 0.0) for step in trajectory]
    score = sum(rewards) / len(rewards) if rewards else 0.0
    return min(max(score, 0.0), 1.0)

def hard_grader(trajectory: List[Dict[str, Any]]) -> float:
    """Grader for the Hard task (Survive the Storm)."""
    if not trajectory:
        return 0.0
    rewards = [step.get("reward", 0.0) for step in trajectory]
    score = sum(rewards) / len(rewards) if rewards else 0.0
    return min(max(score, 0.0), 1.0)