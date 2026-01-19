from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Self


type Scalar = str | int | float | bool
type NestedArray = Scalar | list[NestedArray]
type Cases = list[tuple[NestedArray[Scalar], NestedArray[Scalar]]]


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
        # TODO: Populate this
        ...

    def initialize_modules(self) -> None:
        # TODO: Populate this
        ...

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


def write_cases_to_file(array: Cases, filename_with_ext: Path) -> None:
    # Write a single multi-dimensional array
    with open(filename_with_ext, "w") as f:
        # TODO: Populate this
        # NOTE: This function should write the Python `array` to a global variable in the given language
        ...


if __name__ == "__main__":
    test_files = [
        Project.File(path=Path("output_meta/folder/test")),
        Project.File(path=Path("output_meta/folder/inside/file")),
        Project.File(
            path=Path("output_meta/folder/inside/meta"),
            depends_on=[
                Project.File(path=Path("output_meta/folder/test")),
                Project.File(path=Path("output_meta/folder/inside/file")),
            ],
        ),
    ]
    test_project = Project(files=test_files)
    test_project.initialize_modules()

    test_array = [
        (
            [1, 7, 1, 1, 2],
            [16, 243],
        ),
        (
            [1, -1],
            [4, 9, 0, 0],
        ),
        (
            [6],
            [8, 24, 1],
        ),
    ]
    for file in test_project.files:
        write_cases_to_file(test_array, file.path.with_suffix(test_project.suffix))
