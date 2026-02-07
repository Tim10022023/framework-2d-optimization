from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FunctionSpec:
    id: str
    name: str
    allowed_goals: tuple[str, ...]
    target_z: float           # globales Optimum (für allowed_goals)
    tolerance: float          # wann gilt "found"
    bounds: dict  # {"xmin": -5, "xmax": 5, "ymin": -5, "ymax": 5}



FUNCTIONS: dict[str, FunctionSpec] = {
    "sphere": FunctionSpec(
        id="sphere",
        name="Sphere (x^2 + y^2)",
        allowed_goals=("min",),
        target_z=0.0,
        tolerance=0.01,   # <= 0.01 gilt als gefunden
        bounds={"xmin": -5, "xmax": 5, "ymin": -5, "ymax": 5}
    )
}


def list_function_specs() -> list[dict]:
    return [
        {
            "id": f.id,
            "name": f.name,
            "allowed_goals": list(f.allowed_goals),
            "target_z": f.target_z,
            "tolerance": f.tolerance,
            "bounds": f.bounds,  # <-- NEU
        }
        for f in FUNCTIONS.values()
    ]



def get_spec(function_id: str) -> FunctionSpec:
    if function_id not in FUNCTIONS:
        raise ValueError(f"unknown function_id: {function_id}")
    return FUNCTIONS[function_id]


def evaluate_function(function_id: str, x: float, y: float) -> float:
    if function_id == "sphere":
        return x * x + y * y
    raise ValueError(f"unknown function_id: {function_id}")
