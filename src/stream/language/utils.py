import difflib


def split_code(code: str, separator: str) -> tuple[str]:
    return code.partition(separator)


def validate_with_template(
    template: str | None, code: str, allowed_change: str
) -> tuple[bool, str]:
    if template is None:
        return True, ""

    d = difflib.Differ()
    lines_template = template.splitlines()
    lines_code = code.splitlines()
    diffs = list(d.compare(lines_template, lines_code))

    streak: bool = False
    indent_allowed: int | None = None
    valid: bool = True
    feedback: str | None = None

    for diff in diffs:
        diff_type, diff_code = diff[:2], diff[2:]
        if (
            diff_type in ["  ", "- "]
            and diff_code.strip().startswith(allowed_change)
            and not streak
        ):
            # We start a streak and capture the indentation level
            streak = True
            indent_allowed = len(diff_code) - len(diff_code.lstrip())

        elif (
            diff_type == "  "
            and not diff_code.strip().startswith(allowed_change)
            and not streak
        ):
            # Nothing
            pass

        elif diff_type in ["- ", "+ "] and not streak:
            # Something somewhere else was modified
            valid = False
            feedback = "You did something wrong!"
            break

        elif (
            diff_type == "  "
            and not diff_code.strip().startswith(allowed_change)
            and streak
        ):
            streak = False

        elif diff_type in ["- ", "+ "] and streak:
            if indent_allowed is None:
                raise ValueError("The indent level should always be set in a streak!")

            # Newlines are always valid inside a streak
            indent_current = (
                indent_allowed
                if diff_code.strip() == ""
                else len(diff_code) - len(diff_code.lstrip())
            )

            # Check for correct Python indenting
            if indent_current < indent_allowed:
                valid = False
                feedback = "You did something wrong!"
                break

    return valid, feedback
