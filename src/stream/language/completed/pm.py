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
        # Ensure each file's parent directory has an __init__.py
        for f in self.files:
            init_path = f.path.parent / "__init__.py"
            init_path.touch(exist_ok=True)

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


def write_jagged_array_to_file(
    array: list[tuple[list[int], list[int]]],
    filename_with_ext: Path,
) -> None:
    with open(filename_with_ext, "w") as f:
        var_name = filename_with_ext.stem + "_data"
        f.write(f"{var_name} = {repr(array)}\n")
