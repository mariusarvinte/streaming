import subprocess
from pathlib import Path

from stream.language.completed.pm import Project


def generate_use_statement(location: Path):
    # TODO: Populate this
    # NOTE: Avoid using "all" / "star" imports, rather use generic function names as a template e.g., `some_fn_or_variable`
    # NOTE: For example, in Python this would be an import statement built from `location.parts` and their stems
    ...


def execute_code(
    artifact_path: Path,
    project: Project,
    success_message: str,
) -> str:
    # TODO: Populate this
    # NOTE: Generate a string `command` which executes the code in `artifact_path`
    # NOTE: If needed, use `project` to infer cross-file information and generate a `pre_command`
    # NOTE: If there is no `pre_command`, it should be None
    pre_command: str = ...
    command: str = ...

    # NOTE: The code below cannot be modified in any way
    # Execute the pre-command
    if pre_command:
        result = subprocess.run(pre_command, capture_output=True)
        if result.returncode:
            return f"Pre-command execution: {pre_command} failed with error {result.stderr}!"

    # Execute the command
    result = subprocess.run(command, capture_output=True)
    if result.returncode == 0:
        return success_message

    return result.stderr
