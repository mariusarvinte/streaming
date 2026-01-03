from pathlib import Path


def write_array_to_file(
    array: list[tuple[list[int], list[int]]],
    filename: Path,
) -> None:
    # Write a single multi-dimensional array
    with open(filename, "w") as f:
        f.write(f"{filename.stem} = {array}")
