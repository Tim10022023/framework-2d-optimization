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
        tolerance=0.01,
        bounds={"xmin": -5, "xmax": 5, "ymin": -5, "ymax": 5},
    ),
    "himmelblau": FunctionSpec(
        id="himmelblau",
        name="Himmelblau",
        allowed_goals=("min",),
        target_z=0.0,
        tolerance=0.01,
        bounds={"xmin": -6, "xmax": 6, "ymin": -6, "ymax": 6},
    ),
    "rastrigin": FunctionSpec(
        id="rastrigin",
        name="Rastrigin",
        allowed_goals=("min",),
        target_z=0.0,
        tolerance=0.1,
        bounds={"xmin": -5.12, "xmax": 5.12, "ymin": -5.12, "ymax": 5.12},
    ),
    "ackley": FunctionSpec(
        id="ackley",
        name="Ackley",
        allowed_goals=("min",),
        target_z=0.0,
        tolerance=0.1,
        bounds={"xmin": -5, "xmax": 5, "ymin": -5, "ymax": 5},
    ),
    "rosenbrock": FunctionSpec(
    id="rosenbrock",
    name="Rosenbrock",
    allowed_goals=("min",),
    target_z=0.0,
    tolerance=0.1,
    bounds={"xmin": -2, "xmax": 2, "ymin": -1, "ymax": 3},
),
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

    if function_id == "himmelblau":
        return (x * x + y - 11) ** 2 + (x + y * y - 7) ** 2

    if function_id == "rastrigin":
        import math
        return 20 + (x * x - 10 * math.cos(2 * math.pi * x)) + (y * y - 10 * math.cos(2 * math.pi * y))

    if function_id == "ackley":
        import math
        return (
            -20 * math.exp(-0.2 * math.sqrt(0.5 * (x * x + y * y)))
            - math.exp(0.5 * (math.cos(2 * math.pi * x) + math.cos(2 * math.pi * y)))
            + math.e
            + 20
        )
    if function_id == "rosenbrock":
        return (1 - x) ** 2 + 100 * (y - x * x) ** 2

    raise ValueError(f"unknown function_id: {function_id}")


