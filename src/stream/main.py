import argparse
import os
import sys
import random

from pathlib import Path
import datasets
import dspy

from stream.project import FileAdapter
from stream.feedback import ModuleWithCodeFeedback

from stream.language.completed.python import Project
from stream.language.completed.python import write_cases_to_file

from stream.dataset import get_dataset, get_problem_description


def get_project_structure(name: str, project_class: type) -> Project:
    # Create files without dependencies first
    files = {
        "cases": project_class.File(Path(f"{name}/cases")),
        "solution": project_class.File(Path(f"{name}/solution")),
        "test": project_class.File(Path(f"{name}/test")),
        "runtime": project_class.File(Path(f"{name}/measurements/runtime")),
        "memory": project_class.File(Path(f"{name}/measurements/memory")),
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

    project = project_class(files=list(files.values()))
    return project


def main(args):
    # RNG
    random.seed(args.seed)

    lm = dspy.LM(
        model="openrouter/nvidia/nemotron-3-nano-30b-a3b:free",
        api_key=os.environ["OPENROUTER_API_KEY"],
        temperature=1.0,
        cache=False,
    )
    dspy.configure(lm=lm)

    class ProblemSolvingGeneric(dspy.Signature):
        """You are an expert in solving algorithmic problems using {language}."""

        problem: str = dspy.InputField(
            desc="The description of the problem to be solved",
        )
        cases: dspy.Code[args.language] = dspy.InputField(
            desc="The paired inputs and outputs for the problem written as jagged arrays",
        )

        project: Project = dspy.InputField(
            desc=get_project_structure(args.proj_name, Project)
        )

        explanation: str = dspy.OutputField(
            desc="An explanation of the implementation of `solution`"
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

    # Inject the language in the signature instructions
    ProblemSolvingGeneric = ProblemSolvingGeneric.with_instructions(
        ProblemSolvingGeneric.__doc__.format(language=args.language)
    )

    # Load dataset
    ds: datasets.Dataset = get_dataset("newfacade/LeetCodeDataset")
    train_idx = list(range(len(ds["train"])))
    random.shuffle(train_idx)

    for i in train_idx:
        # Replace the project structure with a sample-specific one in the signature
        sample_dir = f"{args.proj_name}/sample{i}"
        sample_proj_structure = get_project_structure(sample_dir, Project)
        sample_proj_structure.initialize_modules()
        ProblemSolving = ProblemSolvingGeneric.with_updated_fields(
            "project", type_=Project, desc=sample_proj_structure
        )

        # Define an AI module that is templated (prompted) to solve the task
        module = dspy.Predict(ProblemSolving)
        module = ModuleWithCodeFeedback(
            base_module=module,
            project=sample_proj_structure,
        )

        sample = ds["train"][i]
        if "Constraints:" not in sample["problem_description"]:
            raise ValueError("Found a sample without 'Constraints:'!")

        desc, cases = get_problem_description(sample["problem_description"])

        if "Example:" in desc:
            raise ValueError("Examples should not be found in the problem description!")

        write_cases_to_file(cases, sample_proj_structure.file_map["cases"])

        # Form inputs
        inputs = {
            "project": None,
            "problem": desc,
            "cases": sample_proj_structure.file_map["cases"].read_text(),
        }

        with dspy.context(adapter=FileAdapter()):
            pred = module(**inputs)

        # Save the original stdout to restore it later
        original_stdout = sys.stdout
        with open(f"{sample_dir}/history.txt", "w") as f:
            # Redirect stdout to the file
            sys.stdout = f
            dspy.inspect_history(n=5)
        # Restore stdout to the original (usually the console)
        sys.stdout = original_stdout


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
    parser.add_argument(
        "--seed",
        type=int,
        default=2026,
        help="RNG seed",
    )
    args = parser.parse_args()

    main(args)
