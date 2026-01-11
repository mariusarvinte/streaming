import os
import subprocess

from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Self


@dataclass
class Project:
    files: list[File] = field(default_factory=list)

    @dataclass
    class File:
        path: Path
        depends_on: list[Self] = field(default_factory=list)

        def add_deps(self, deps: list[Self]):
            self.depends_on.extend(deps)

    @cached_property
    def suffix(self) -> str:
        return ".py"

    def initialize_modules(self) -> None:
        for file in self.files:
            os.makedirs(file.path.parent, exist_ok=True)
            (file.path.parent / "__init__.py").touch()

    @cached_property
    def dependency_map(self) -> dict[str, list[Path]]:
        mapping = {
            f.path.stem: [g.path.with_suffix(self.suffix) for g in f.depends_on]
            for f in self.files
        }
        return mapping

    @cached_property
    def file_map(self) -> dict[str, Path]:
        mapping = {f.path.stem: f.path.with_suffix(self.suffix) for f in self.files}
        return mapping


def generate_use_statement(location: Path):
    parts = list(location.parts)
    parts[-1] = location.stem
    return f"from {'.'.join(parts)} import <function-or-variable-name>"


def execute_code(
    artifact_path: Path,
    project: Project,
    success_message: str,
) -> str:
    # The artifact is a module
    parts = list(artifact_path.parts)
    parts[-1] = artifact_path.stem
    module_name = f"{'.'.join(parts)}"
    command = f"uv run -m {module_name}"

    # Execute the command
    result = subprocess.run(command, capture_output=True)
    if result.returncode == 0:
        return success_message

    return result.stderr


def write_jagged_array_to_file(
    array: list[tuple[list[int], list[int]]],
    filename_with_ext: Path,
) -> None:
    # Write a single multi-dimensional array
    with open(filename_with_ext, "w") as f:
        f.write(f"{filename_with_ext.stem} = {array}")
