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


def test_valid_with_template(valid: str, template: str, allowed_change: str):
    valid, feedback = validate_with_template(template, valid, allowed_change)
    assert valid == True
    assert feedback is None


def test_invalid_with_template(invalid: str, template: str, allowed_change: str):
    valid, feedback = validate_with_template(template, invalid, allowed_change)
    assert valid == False
    assert feedback == "You did something wrong!"
