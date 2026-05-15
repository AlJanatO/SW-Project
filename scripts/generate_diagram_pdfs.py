#!/usr/bin/env python3
"""Render PlantUML diagram source files into PDF files for submission."""

from pathlib import Path
import shutil
import subprocess
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DIAGRAM_DIR = PROJECT_ROOT / "diagrams"
OUTPUT_DIR = DIAGRAM_DIR / "rendered"
PLANTUML_JAR = PROJECT_ROOT / "tools" / "plantuml.jar"

DIAGRAMS = [
    "class-diagram.puml",
    "request-statechart.puml",
    "security-analysis-flow.puml",
]


def plantuml_command(source_file: Path) -> list[str]:
    installed = shutil.which("plantuml")
    if installed:
        return [installed, "-tpdf", "-o", str(OUTPUT_DIR), str(source_file)]
    if PLANTUML_JAR.exists():
        return ["java", "-jar", str(PLANTUML_JAR), "-tpdf", "-o", str(OUTPUT_DIR), str(source_file)]
    raise RuntimeError(
        "PlantUML was not found. Install plantuml or place plantuml.jar at tools/plantuml.jar."
    )


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    missing = [name for name in DIAGRAMS if not (DIAGRAM_DIR / name).exists()]
    if missing:
        print(f"Missing diagram source files: {', '.join(missing)}", file=sys.stderr)
        return 1

    for name in DIAGRAMS:
        source_file = DIAGRAM_DIR / name
        command = plantuml_command(source_file)
        print(f"Rendering {source_file.name}...")
        subprocess.run(command, check=True)

    print(f"PDF diagrams generated in: {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
