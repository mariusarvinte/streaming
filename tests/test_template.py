import pytest

from stream.language.utils import validate_with_template


@pytest.fixture
def allowed_change() -> str:
    return "# TODO:"


@pytest.fixture
def template() -> str:
    return """
def other_fn(args):
    return False

def some_fn(args):
    # TODO: Populate this
    ...

    # TODO: Use what you populated
    ...

class Stuff:
    def __init__():
        self.a = 1

    def method(self):
        # TODO: Populate this
    
    def do_not_touch(self):
        return False
""".strip()


@pytest.fixture
def valid() -> str:
    return """
def other_fn(args):
    return False

def some_fn(args):
    # TODO: Populate this
    a = 12
    return a

class Stuff:
    def __init__():
        self.a = 1

    def method(self):
        self.b = 1
    
    def do_not_touch(self):
        return False
""".strip()


@pytest.fixture
def invalid() -> str:
    return """
def other_fn(args):
    return False

def some_fn(args):
    # TODO: Populate this
    a = 12
    return a

class Stuff:
    def __init__():
        self.a = 1

    def method(self):
        self.b = 1
    
    def do_not_touch(self):
        return False

def added_fn(self):
    pass
""".strip()


@pytest.fixture
def valid_newline() -> str:
    return """
def other_fn(args):
    return False

def some_fn(args):
    print("Newline!\\n")

class Stuff:
    def __init__():
        self.a = 1

    def method(self):
        # TODO: Populate this
    
    def do_not_touch(self):
        return False
""".strip()


@pytest.fixture
def template_py() -> str:
    return """from dataclasses import dataclass, field
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


def write_jagged_array_to_file(
    array: list[tuple[list[int], list[int]]],
    filename_with_ext: Path,
) -> None:
    with open(filename_with_ext, "w") as f:
        # TODO: Populate this
        # NOTE: This function should write the Python `array` to a global variable in the given language
        ...
""".strip()


@pytest.fixture
def valid_py() -> str:
    return """from dataclasses import dataclass, field
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


def write_jagged_array_to_file(
    array: list[tuple[list[int], list[int]]],
    filename_with_ext: Path,
) -> None:
    with open(filename_with_ext, "w") as f:
        # TODO: Populate this
        # NOTE: This function should write the Python `array` to a global variable in the given language
        ...
""".strip()


def test_valid_with_template(template: str, valid: str, allowed_change: str):
    valid, feedback = validate_with_template(template, valid, allowed_change)
    assert valid == True
    assert feedback is None


def test_valid_newline_with_template(
    template: str, valid_newline: str, allowed_change: str
):
    valid, feedback = validate_with_template(template, valid_newline, allowed_change)
    assert valid == True
    assert feedback is None


def test_valid_py_with_template(template_py: str, valid_py: str, allowed_change: str):
    valid, feedback = validate_with_template(template_py, valid_py, allowed_change)
    assert valid == True
    assert feedback is None


def test_invalid_with_template(template: str, invalid: str, allowed_change: str):
    valid, feedback = validate_with_template(template, invalid, allowed_change)
    assert valid == False
    assert (
        feedback
        == "You must strictly follow the provided template and only modify the code where it is marked with # TODO:!"
    )
