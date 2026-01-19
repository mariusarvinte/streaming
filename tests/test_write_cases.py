import pytest
import subprocess

from stream.language.completed.python import write_cases_to_file


TEST_CASES = [
    (
        [
            ("blabla", 6),
            (["abcdef", "another"], "some"),
            ([[1, 2, 5], "some", [2.5, 1.5]], [9, 8, 1]),
            ([[True, False], [1, 2]], False),
        ],
        "chaos",
    )
]


@pytest.mark.parametrize("array, label", TEST_CASES)
def test_write_cases_to_file(array, label, tmp_path):
    tmp_path.mkdir(exist_ok=True)
    test_file = tmp_path / f"{label}.py"

    write_cases_to_file(array, test_file)

    # Assert file was written
    assert test_file.exists()
    # Check successful execution
    result = subprocess.run(f"uv run {str(test_file)}")
    assert result.returncode == 0
