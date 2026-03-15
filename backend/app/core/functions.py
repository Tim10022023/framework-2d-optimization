from __future__ import annotations
import math
from dataclasses import dataclass


@dataclass
class FunctionSpec:
    id: str
    name: str
    allowed_goals: tuple[str, ...]
    target_z: float
    tolerance: float
    bounds: dict[str, float]
    reveal_title: str | None = None
    reveal_description: str | None = None
    reveal_image: str | None = None



FUNCTIONS = {
    "sphere_shifted": FunctionSpec(
        id="sphere_shifted",
        name="Sphere (verschoben)",
        allowed_goals=("min",),
        target_z=0.0,
        tolerance=0.01,
        bounds={"xmin": -5, "xmax": 5, "ymin": -5, "ymax": 5},
        reveal_title="Sphere (verschoben)",
        reveal_description="Einfache glatte Testfunktion mit globalem Minimum bei (3.7, -2.1).",
        reveal_image="/static/function_images/sphere_shifted.png",
    ),
    "booth": FunctionSpec(
        id="booth",
        name="Booth",
        allowed_goals=("min",),
        target_z=0.0,
        tolerance=0.01,
        bounds={"xmin": -10, "xmax": 10, "ymin": -10, "ymax": 10},
        reveal_title="Booth",
        reveal_description="Glatter quadratischer Benchmark mit globalem Minimum bei (1, 3).",
        reveal_image="/static/function_images/booth.png",
    ),
    "himmelblau": FunctionSpec(
        id="himmelblau",
        name="Himmelblau",
        allowed_goals=("min",),
        target_z=0.0,
        tolerance=0.01,
        bounds={"xmin": -5, "xmax": 5, "ymin": -5, "ymax": 5},
        reveal_title="Himmelblau",
        reveal_description="Benchmark-Funktion mit mehreren gleich guten globalen Minima.",
        reveal_image="/static/function_images/himmelblau.png",
    ),
    "rosenbrock": FunctionSpec(
        id="rosenbrock",
        name='Rosenbrock ("Bananenfunktion")',
        allowed_goals=("min",),
        target_z=0.0,
        tolerance=0.01,
        bounds={"xmin": -2, "xmax": 2, "ymin": -1, "ymax": 3},
        reveal_title='Rosenbrock-Funktion ("Bananenfunktion")',
        reveal_description="Klassische Tal-Funktion mit globalem Minimum bei (1, 1).",
        reveal_image="/static/function_images/rosenbrock.png",
    ),
    "eggholder": FunctionSpec(
        id="eggholder",
        name="Eggholder",
        allowed_goals=("min",),
        target_z=-959.6407,
        tolerance=5.0,
        bounds={"xmin": -512, "xmax": 512, "ymin": -512, "ymax": 512},
        reveal_title="Eggholder",
        reveal_description="Stark multimodale Benchmark-Funktion mit sehr unruhiger Landschaft.",
        reveal_image="/static/function_images/eggholder.png",
    ),
    "rastrigin_shifted": FunctionSpec(
        id="rastrigin_shifted",
        name="Rastrigin (verschoben)",
        allowed_goals=("min",),
        target_z=0.0,
        tolerance=0.01,
        bounds={"xmin": -5.12, "xmax": 5.12, "ymin": -5.12, "ymax": 5.12},
        reveal_title="Rastrigin (verschoben)",
        reveal_description="Stark multimodale Benchmark-Funktion mit vielen lokalen Minima.",
        reveal_image="/static/function_images/rastrigin_shifted.png",
    ),
    "schwefel": FunctionSpec(
        id="schwefel",
        name="Schwefel",
        allowed_goals=("min",),
        target_z=0.0,
        tolerance=1.0,
        bounds={"xmin": -500, "xmax": 500, "ymin": -500, "ymax": 500},
        reveal_title="Schwefel",
        reveal_description="Benchmark-Funktion mit schwierigem Suchraum und globalem Minimum nahe 420.9687 pro Dimension.",
        reveal_image="/static/function_images/schwefel.png",
    ),
    "levy": FunctionSpec(
        id="levy",
        name="Levy",
        allowed_goals=("min",),
        target_z=0.0,
        tolerance=0.01,
        bounds={"xmin": -10, "xmax": 10, "ymin": -10, "ymax": 10},
        reveal_title="Levy",
        reveal_description="Benchmark-Funktion mit welliger Struktur und globalem Minimum bei (1, 1).",
        reveal_image="/static/function_images/levy.png",
    ),
    "griewank_negated_shifted": FunctionSpec(
        id="griewank_negated_shifted",
        name="Griewank (negiert, verschoben)",
        allowed_goals=("max",),
        target_z=0.0,
        tolerance=0.01,
        bounds={"xmin": -10, "xmax": 10, "ymin": -10, "ymax": 10},
        reveal_title="Griewank (negiert, verschoben)",
        reveal_description="Negierte und verschobene Griewank-Funktion, daher hier als Maximierungsproblem.",
        reveal_image="/static/function_images/griewank_negated_shifted.png",
    ),
    "easom": FunctionSpec(
        id="easom",
        name="Easom",
        allowed_goals=("min",),
        target_z=-1.0,
        tolerance=0.01,
        bounds={"xmin": -5, "xmax": 20, "ymin": -5, "ymax": 20},
        reveal_title="Easom",
        reveal_description="Sehr spitze Benchmark-Funktion mit globalem Minimum bei (π, π).",
        reveal_image="/static/function_images/easom.png",
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
            "reveal_title": f.reveal_title,
            "reveal_description": f.reveal_description,
            "reveal_image": f.reveal_image,
        }
        for f in FUNCTIONS.values()
    ]



def get_spec(function_id: str) -> FunctionSpec:
    spec = FUNCTIONS.get(function_id)
    if not spec:
        raise ValueError(f"unknown function_id: {function_id}")
    return spec


def evaluate_function(function_id: str, x: float, y: float) -> float:
    if function_id == "sphere_shifted":
        return (x - 3.7) ** 2 + (y + 2.1) ** 2

    if function_id == "booth":
        return (x + 2 * y - 7) ** 2 + (2 * x + y - 5) ** 2

    if function_id == "himmelblau":
        return (x * x + y - 11) ** 2 + (x + y * y - 7) ** 2

    if function_id == "rosenbrock":
        return (1 - x) ** 2 + 100 * (y - x * x) ** 2

    if function_id == "eggholder":
        return -(
            (y + 47) * math.sin(math.sqrt(abs(y + x / 2 + 47)))
            + x * math.sin(math.sqrt(abs(x - (y + 47))))
        )

    if function_id == "rastrigin_shifted":
        xs = x - 2.5
        ys = y + 1.7
        return 20 + xs**2 - 10 * math.cos(2 * math.pi * xs) + ys**2 - 10 * math.cos(2 * math.pi * ys)

    if function_id == "schwefel":
        return 837.97 - x * math.sin(math.sqrt(abs(x))) - y * math.sin(math.sqrt(abs(y)))

    if function_id == "levy":
        w1 = 1 + (x - 1) / 4
        w2 = 1 + (y - 1) / 4
        return (
            math.sin(math.pi * w1) ** 2
            + (w1 - 1) ** 2 * (1 + 10 * math.sin(math.pi * w1 + 1) ** 2)
            + (w2 - 1) ** 2 * (1 + math.sin(2 * math.pi * w2) ** 2)
        )

    if function_id == "griewank_negated_shifted":
        xs = x + 2.6
        ys = y - 3.1
        return -(
            1
            + (xs**2) / 4000
            + (ys**2) / 4000
            - math.cos(xs) * math.cos(ys / math.sqrt(2))
        )

    if function_id == "easom":
        return -math.cos(x) * math.cos(y) * math.exp(-((x - math.pi) ** 2 + (y - math.pi) ** 2))

    raise ValueError(f"unknown function_id: {function_id}")

