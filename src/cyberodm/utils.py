from __future__ import annotations
import pandas as pd

def norm_toward_target(value: float, target: float, direction: str) -> float:
    # returns 0..1 where 1 means meets/exceeds target in correct direction
    if target is None:
        return 0.0
    if direction == "up_is_good":
        return max(0.0, min(1.0, value / target if target != 0 else 1.0))
    # down_is_good: lower or equal is better; 1 if value <= target, else decays
    if target == 0:
        return 1.0 if value == 0 else max(0.0, min(1.0, 1.0 / (value)))
    return max(0.0, min(1.0, target / value if value != 0 else 1.0))

def rag(score: float, red: float, amber: float) -> str:
    if score < red: return "Red"
    if score < amber: return "Amber"
    return "Green"
