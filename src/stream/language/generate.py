from typing import Type

import dspy

from stream.main import get_project_structure


def get_signature() -> Type[dspy.Signature]:
    proj_structure = get_project_structure()

    class CodeInstrumenting(dspy.Signature):
        """You are an expert in using Python to instrument code written in arbitrary languages."""

        project: Project = dspy.InputField(desc=proj_structure)

        language: str = dspy.InputField(
            desc="The language of the code to be instrumented using Python"
        )
        template: dspy.Code["Python"] = dspy.InputField(
            desc="An instrumentation template, with TODOs and NOTEs left in"
        )

        code: dspy.Code["Python"] = dspy.OutputField(
            desc="The `template` with all completed code, and no other changes"
        )

    return CodeInstrumenting
