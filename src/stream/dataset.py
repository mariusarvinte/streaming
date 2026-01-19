import re

from datasets import load_dataset, Dataset

from stream.language.completed.python import Cases


def get_dataset(name: str = "newfacade/LeetCodeDataset") -> Dataset:
    ds = load_dataset(name)
    return ds


def get_problem_description(
    full_text: str,
) -> tuple[str, Cases]:
    # Extract all text from beginning up to first occurence of 'Example'
    delimiter_pattern = r"Example \d{1}:|Constraints:"
    parts = re.split(delimiter_pattern, full_text)
    desc = parts[0].strip()

    # Extract input-output from all examples
    cases: Cases = []
    for i in range(1, len(parts) - 1):
        example = parts[i].strip()

        # Extract inputs
        start_str = "Input:"
        end_str = "Output:"
        pattern = rf"{start_str}(.*?){end_str}"
        substrings = re.findall(pattern, example)
        breakpoint()
        if len(substrings) > 1:
            raise RuntimeError("Input extraction failed!")
        case_inputs = substrings[0].strip()

        # Delete all named assignments

        case_output = ...

        cases.append((case_inputs, case_output))

    return desc, cases
