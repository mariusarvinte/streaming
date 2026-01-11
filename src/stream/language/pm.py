import argparse
import os
import sys

from pathlib import Path

import dspy

from stream.feedback import ModuleWithCodeFeedback
from stream.language.utils import split_code
from stream.language.completed.python import Project


def main(args):
    lm = dspy.LM(
        model="openrouter/nvidia/nemotron-3-nano-30b-a3b:free",
        api_key=os.environ["OPENROUTER_API_KEY"],
        temperature=1.0,
        cache=False,
    )
    dspy.configure(lm=lm)

    # Create the Python meta-project which will encompass the project management code
    files = [Project.File(path=Path("src/stream/language/completed/pm"))]
    proj_structure = Project(files=files)
    proj_structure.initialize_modules()

    class ProjectManager(dspy.Signature):
        """
        You are an expert in using Python to manage multi-file projects in arbitrary languages.
        Using the Python `template`, populate its missing code.
        The way the project is structured should be coherent, idiomatic, and ensure that execution is possible.
        Only populate methods, classes, or functions marked with 'TODO' and nothing else.
        Do not add new code outside of the 'TODO' scope, nor remove existing code.
        Your solution will be strictly checked and graded against these requirements.
        """

        language: str = dspy.InputField(
            desc="The programming language of the code files that are instrumented"
        )
        template: dspy.Code["Python"] = dspy.InputField(
            desc="The template to be populated"
        )

        pm: dspy.Code["Python"] = dspy.OutputField(desc="The populated `template`")

    # Form the inputs
    template = Path(args.template_path).read_text()
    template, statement, test = split_code(
        template, separator='if __name__ == "__main__":'
    )

    # Instantiate the dspy.Module
    project_manager = dspy.Predict(ProjectManager)
    if args.feedback:
        project_manager = ModuleWithCodeFeedback(
            base_module=project_manager,
            project=proj_structure,
            test_code=dict(pm="\n".join((statement, test))),
        )

    inputs = {
        "language": args.language,
        "template": template,
    }
    # Predict and write the code to disk (with execution feedback)
    pred = project_manager(**inputs)

    # Save the original stdout to restore it later
    original_stdout = sys.stdout
    with open("./history_pm.txt", "w") as f:
        # Redirect stdout to the file
        sys.stdout = f
        dspy.inspect_history(n=5)
    # Restore stdout to the original (usually the console)
    sys.stdout = original_stdout


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--language",
        type=str,
        default="Python",
        help="Language for the desired LLM output code",
    )
    parser.add_argument(
        "--template_path",
        type=str,
        default="src/stream/language/template/pm.py",
        help="Path to the template file",
    )
    parser.add_argument(
        "--feedback",
        action="store_true",
        help="Use execution feedback",
    )
    args = parser.parse_args()

    main(args)
