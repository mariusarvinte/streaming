from collections import defaultdict
from copy import deepcopy
from typing import Any, Type

import dspy

from stream.project import write_code

from stream.language.completed.python import Project
from stream.language.completed.python import execute_code


class ModuleWithCodeFeedback(dspy.Module):
    def __init__(
        self,
        base_module: dspy.Module,
        project: Project,
        steps: int = 3,
        test_code: dict[str, str] | None = None,
        success_message: str = "Code executed successfully!",
        trajectory_len: int = 0,
    ):
        super().__init__()

        self.base_module = base_module
        self.base_signatures: dict[str, Type[dspy.Signature]] = {
            name: module.signature
            for name, module in self.base_module.named_predictors()
        }
        self.base_names: dict[Type[dspy.Signature], str] = {
            value: key for key, value in self.base_signatures.items()
        }

        self.project = project
        self.steps = steps
        self.test_code = test_code
        self.success_message = success_message
        self.trajectory_len = trajectory_len

        # Modify all signatures to include trajectories and code execution feedback
        self.mod_signatures: dict[str, Type[dspy.Signature]] = {}
        for name, signature in self.base_signatures.items():
            mod_signature: Type[dspy.Signature] = deepcopy(signature)

            for field_name, field in mod_signature.output_fields.items():
                # Only for dspy.Code outputs
                if getattr(field.annotation, "__bases__", None) != (dspy.Code,):
                    continue

                # Insert the trajectory field containing all (possibly truncated) previous attempts
                mod_signature = mod_signature.append(
                    f"{field_name}_attempts",
                    dspy.InputField(desc=f"The previous attempts for `{field_name}`"),
                    type_=list[dspy.Code[f"{field.annotation.language.lower()}"]],
                )

                # Insert the code execution outcome from the latest attempt
                mod_signature = mod_signature.append(
                    f"{field_name}_outcome",
                    dspy.InputField(
                        desc=f"Outcome of attempting to execute the latest of `{field_name}_attempts`"
                    ),
                    type_=str,
                )

            self.mod_signatures[name] = mod_signature

    def forward(self, **kwargs):
        adapter = dspy.settings.adapter or dspy.ChatAdapter()
        mod_signatures = self.mod_signatures
        base_names = self.base_names

        # TODO: dataclass this
        advice: dict[str, str] | None = None
        attempts: dict[str, list[str]] | None = None

        # For each attempt
        for i in range(self.steps):
            all_success = True

            class FeedbackWrapperAdapter(adapter.__class__):
                def __call__(
                    self, lm, lm_kwargs, signature, demos, inputs
                ) -> list[dict[str, Any]]:
                    if advice is None:
                        return adapter(lm, lm_kwargs, signature, demos, inputs)

                    # Retrieve the modified signature based on the runtime module name
                    mod_signature = mod_signatures[base_names[signature]]
                    # Pass in trajectory and execution feedback
                    for key, value in advice.items():
                        inputs[f"{key}_attempts"] = attempts[key]
                        inputs[f"{key}_outcome"] = value

                    return adapter(lm, lm_kwargs, mod_signature, demos, inputs)

            with dspy.context(adapter=FeedbackWrapperAdapter()):
                outputs = self.base_module(**kwargs)

            write_code(outputs, self.project, extra=self.test_code)

            advice = dict()
            if attempts is None:
                attempts = defaultdict(list)

            for name, field in outputs.items():
                # For code outputs only
                if type(field).__base__ != dspy.Code:
                    continue

                # Execute the code
                artifact_path = self.project.file_map[name]
                message = execute_code(
                    artifact_path,
                    project=self.project,
                    success_message=self.success_message,
                )
                if message != self.success_message:
                    all_success = False
                # Pass successful message in case of partial success
                advice[name] = message

                # Store attempt and truncate trajectory
                attempts[name].append(field.code)
                if self.trajectory_len > 0 and i >= self.trajectory_len:
                    attempts[name].pop(0)

            # Early exit on all success
            if all_success:
                return outputs

        # If we reach this, the LLM failed to generate code that executes for all outputs
        return outputs
