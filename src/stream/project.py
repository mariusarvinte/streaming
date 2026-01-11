from pathlib import Path
from typing import Any

import dspy
from dspy import Signature
from dspy.clients.lm import LM
from dspy.adapters.types.base_type import split_message_content_for_custom_types

from stream.language.completed.python import Project
from stream.language.completed.python import generate_use_statement


def write_code(code: dspy.Prediction, path: Path, extra: str | None = None):
    # Write the code to file
    code = "\n\n".join([code, extra]) if extra else code
    with open(path, "w") as f:
        f.write(code)


# Custom adapter that injects instructions about cross-output dependencies
class FileAdapter(dspy.ChatAdapter):
    def __call__(
        self,
        lm: "LM",
        lm_kwargs: dict[str, Any],
        signature: type[Signature],
        demos: list[dict[str, Any]],
        inputs: dict[str, Any],
    ) -> list[dict[str, Any]]:
        self.project = signature.input_fields["project"]
        signature = signature.delete("project")

        # TODO: Re-order the output fields in topological order
        processed_signature = self._call_preprocess(lm, lm_kwargs, signature, inputs)
        inputs = self.format(processed_signature, demos, inputs)

        outputs = lm(messages=inputs, **lm_kwargs)
        return self._call_postprocess(
            processed_signature, signature, outputs, lm, lm_kwargs
        )

    def format_output_interactions(
        self,
        signature: type[Signature],
    ) -> str:
        output = f""

        # Cache use statements for each pair of locations
        use_statements = dict()
        info: Project = self.project.json_schema_extra["desc"]

        for name, field in signature.output_fields.items():
            # Early exit for non-code fields
            if getattr(field.annotation, "__bases__", None) != (dspy.Code,):
                continue

            depends_on: list[Path] = [f.stem for f in info.dependency_map[name]]
            # Early exit
            if not depends_on:
                continue

            # Generate use statements and instructions for each dependency
            all_fields = signature.input_fields | signature.output_fields
            output += f"When generating code for `{name}`, use the following code to re-use other outputs:\n"
            output += f"```{all_fields[name].annotation.language.lower()}\n"

            for dep in depends_on:
                location: Path = info.file_map[dep]
                if getattr(all_fields[dep].annotation, "__bases__", None) == (
                    dspy.Code,
                ) and (
                    all_fields[dep].annotation.language
                    != all_fields[name].annotation.language
                ):
                    raise ValueError("Cannot generate cross-language use statements!")

                if (name, dep) in use_statements:
                    use_statement = use_statements[(name, dep)]
                else:
                    use_statement: str = generate_use_statement(location)
                    use_statements[(name, dep)] = use_statement

                # Add to instructions
                output += f"{use_statement}\n"
            # Add closing fences
            output += "```\n\n"

        return output

    def format(
        self,
        signature: type[Signature],
        demos: list[dict[str, Any]],
        inputs: dict[str, Any],
    ) -> list[dict[str, Any]]:
        inputs_copy = dict(inputs)

        # If the signature and inputs have conversation history, we need to format the conversation history and
        # remove the history field from the signature.
        history_field_name = self._get_history_field_name(signature)
        if history_field_name:
            # In order to format the conversation history, we need to remove the history field from the signature.
            signature_without_history = signature.delete(history_field_name)
            conversation_history = self.format_conversation_history(
                signature_without_history,
                history_field_name,
                inputs_copy,
            )

        messages = []
        system_message = (
            f"{self.format_field_description(signature)}\n"
            f"{self.format_field_structure(signature)}\n"
            f"{self.format_output_interactions(signature)}\n"
            f"{self.format_task_description(signature)}"
        )
        messages.append({"role": "system", "content": system_message})
        messages.extend(self.format_demos(signature, demos))
        if history_field_name:
            # Conversation history and current input
            content = self.format_user_message_content(
                signature_without_history, inputs_copy, main_request=True
            )
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": content})
        else:
            # Only current input
            content = self.format_user_message_content(
                signature, inputs_copy, main_request=True
            )
            messages.append({"role": "user", "content": content})

        messages = split_message_content_for_custom_types(messages)
        return messages
