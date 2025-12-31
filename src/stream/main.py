import argparse
import os
import sys

from pathlib import Path
import dspy

from stream.adapter import FileAdapter
from stream.adapter import File, Project


def main(args):
    lm = dspy.LM(
        model="openrouter/nvidia/nemotron-3-nano-30b-a3b:free",
        api_key=os.environ["OPENROUTER_API_KEY"],
        temperature=1.0,
        cache=False,
    )
    adapter = FileAdapter() if args.files else dspy.ChatAdapter()
    dspy.configure(
        lm=lm,
        adapter=adapter,
    )

    # Define the project (e.g., for Python, package) structure
    project_name = args.proj_name
    # Create files without dependencies first
    files = {
        "cases": File(Path(f"{project_name}/cases.py")),
        "solution": File(Path(f"{project_name}/solution.py")),
        "test": File(Path(f"{project_name}/test.py")),
        "runtime": File(Path(f"{project_name}/measurements/runtime.py")),
        "memory": File(Path(f"{project_name}/measurements/memory.py")),
    }
    # Add dependencies to files
    # NOTE: This is currently built in topological order by hand
    # FIXME: Use a proper graph library to store this
    files["runtime"].add_deps(
        [
            files["cases"],
            files["solution"],
        ]
    )
    files["memory"].add_deps(
        [
            files["cases"],
            files["solution"],
        ]
    )
    files["test"].add_deps(
        [
            files["cases"],
            files["solution"],
            files["runtime"],
            files["memory"],
        ]
    )
    # Create the folder structure
    proj_structure: Project = Project(
        language=args.language,
        files=list(files.values()),
    )

    class ProblemSolving(dspy.Signature):
        """You are an expert in solving algorithmic problems using Python."""

        project: Project = dspy.InputField(desc=proj_structure)

        problem: str = dspy.InputField(
            desc="The description of the problem to be solved",
        )
        cases: list[tuple[list[int], list[int]]] = dspy.InputField(
            desc="A list of paired inputs and outputs for the problem",
        )

        solution: dspy.Code[args.language] = dspy.OutputField(
            desc="Code that when executed with the inputs, produces the expected outputs",
        )
        runtime: dspy.Code[args.language] = dspy.OutputField(
            desc="Code that profiles the execution time of `solution` when running on `cases`",
        )
        memory: dspy.Code[args.language] = dspy.OutputField(
            desc="Code that profiles the runtime memory usage of `solution` when running on `cases`",
        )
        test: dspy.Code[args.language] = dspy.OutputField(
            desc="Code that tests the `solution` on the provided `cases` and runs `runtime` and `memory` measurements",
        )

    # Define an AI module that is templated (prompted) to solve the task
    module = dspy.Predict(ProblemSolving)

    # Perform the task on some inputs
    inputs = {
        "project": None,
        "problem": """Given an integer array `nums` sorted in non-decreasing order, consider the number of unique elements in `nums` to be `k`.
    Return the number of unique elements `k`.""",
        "cases": [
            ([1, 1, 4, 6, 7, 9], [5]),
            ([4, 4, 4, 4, 4], [1]),
            ([26, 999, 1003], [3]),
        ],
    }
    pred = module(**inputs)

    # Save the original stdout to restore it later
    original_stdout = sys.stdout
    with open("./history.txt", "w") as f:
        # Redirect stdout to the file
        sys.stdout = f
        dspy.inspect_history(n=5)
    # Restore stdout to the original (usually the console)
    sys.stdout = original_stdout

    # Write the Python code to files
    proj_structure.initialize_modules()
    for key in ProblemSolving.output_fields.keys():
        with open(proj_structure.file_map[key], "w") as f:
            f.write(pred[key].code)

    # FIXME: Figure out how to annotate data structures to-be-converted to code
    written_inputs = ["cases"]
    for key in written_inputs:
        with open(proj_structure.file_map[key], "w") as f:
            f.write(f"{key} = {inputs[key]}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--files",
        action="store_true",
        help="Use file-system aware adapter and signature",
    )
    parser.add_argument(
        "--proj_name",
        type=str,
        default="./output",
        help="Location for the LLM to write code in",
    )
    parser.add_argument(
        "--language",
        type=str,
        default="Python",
        help="Language for the desired LLM output code",
    )
    args = parser.parse_args()

    main(args)
