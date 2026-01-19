import ast
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
        example.replace("null", "None")

        # Extract inputs
        start_str = "Input:"
        end_str = "Output:"
        pattern = rf"{start_str}(.*?){end_str}"
        substrings = re.findall(pattern, example, re.DOTALL)
        if len(substrings) != 1:
            raise RuntimeError("Input extraction failed!")
        case_inputs = substrings[0].strip()

        # Delete all named assignments from inputs
        case_inputs = list(case_inputs)
        to_pop = []
        for i, letter in enumerate(case_inputs):
            # Pop from the left
            if letter == "=":
                to_pop.append(i)
                for j in range(i - 1, -1, -1):
                    if case_inputs[j] == ",":
                        break
                    to_pop.append(j)
        for i in reversed(sorted(to_pop)):
            case_inputs.pop(i)
        case_inputs = f"[{''.join(case_inputs).strip()}]"
        try:
            case_inputs = ast.literal_eval(case_inputs)
        except (ValueError, SyntaxError) as e:
            print(e)
            raise RuntimeError("Input evaluation failed!")

        # Some examples may not have explanations
        start_str = "Output:"
        end_str = "Explanation:"
        if end_str not in example:
            substrings = re.split(start_str, example)[1:]
        else:
            pattern = rf"{start_str}(.*?){end_str}"
            substrings = re.findall(pattern, example, re.DOTALL)

        if len(substrings) != 1:
            raise RuntimeError("Output extraction failed!")

        try:
            case_outputs = ast.literal_eval(substrings[0].strip())
        except (ValueError, SyntaxError) as e:
            print(e)
            raise RuntimeError("Output evaluation failed!")

        cases.append((case_inputs, case_outputs))

    return desc, cases
