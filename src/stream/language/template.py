import subprocess

from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Self


@dataclass
class Project:
    language: str
    files: list[File] = field(default_factory=list)

    @dataclass
    class File:
        path: Path
        depends_on: list[Self] = field(default_factory=list)

        def add_deps(self, deps: list[Self]):
            self.depends_on.extend(deps)

    @cached_property
    def suffix(self) -> str:
        # TODO: Populate this
        # NOTE: For example, in Python this would be ".py"
        pass

    def initialize_modules(self) -> None:
        # TODO: Populate this
        # NOTE: For example, in Python this would be writing __init__.py files in the parent folder of each file
        pass

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
    # TODO: Populate this
    # NOTE: Avoid using "all" / "star" imports, rather use generic function names as a template e.g., `some_fn_or_variable`
    # NOTE: For example, in Python this would be an import statement built from `location.parts` and their stems
    pass


def execute_code(
    artifact_path: Path,
    project: Project,
    success_message: str,
) -> str:
    # TODO: Populate this
    # NOTE: Generate a string `command` which executes the code in `artifact_path`
    # NOTE: If needed, use `project` to infer cross-file information and generate a `pre_command`
    # NOTE: If there is no `pre_command`, it should be None
    pre_command: str = ...
    command: str = ...

    # NOTE: The code below cannot be modified in any way
    # Execute the pre-command
    if pre_command:
        result = subprocess.run(pre_command, capture_output=True)
        if result.returncode:
            return f"Pre-command execution: {pre_command} failed with error {result.stderr}!"

    # Execute the command
    result = subprocess.run(command, capture_output=True)
    if result.returncode == 0:
        return success_message

    return result.stderr


def write_jagged_array_to_file(
    array: list[tuple[list[int], list[int]]],
    filename_with_ext: Path,
) -> None:
    with open(filename_with_ext, "w") as f:
        # TODO: Populate this
        # NOTE: This function should write the Python `array` to a global variable in the given language
        pass
