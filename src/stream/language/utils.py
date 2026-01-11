import difflib


def split_code(code: str, separator: str) -> tuple[str]:
    return code.partition(separator)


def validate_with_template(
    template: str | None, code: str, allowed_change: str
) -> tuple[bool, str | None]:
    feedback = None
    if template is None:
        return True, feedback

    # Escape special characters in strings
    template = template.replace("\\n", "\\\\n").replace("\\t", "\\\\t")
    code = code.replace("\\n", "\\\\n").replace("\\t", "\\\\t")

    d = difflib.Differ()
    lines_template = template.splitlines()
    lines_code = code.splitlines()
    diffs = list(d.compare(lines_template, lines_code))
    indents = [None for diff in diffs]
    allowed = [False for diff in diffs]
    valid = [False for diff in diffs]

    # Populate the indent and marker for each line
    indent_previous = 0
    for i, diff in enumerate(diffs):
        _, diff_code = diff[:2], diff[2:]
        # Treat newlines as part of the previous level set
        indent_current = (
            indent_previous
            if diff_code.strip() == ""
            else len(diff_code) - len(diff_code.lstrip())
        )
        indent_previous = indents[i] = indent_current

        if diff_code.strip().startswith(allowed_change):
            allowed[i] = True

    # For each changed line, determine if an allowed line is on its level set
    for i, diff in enumerate(diffs):
        diff_type, diff_code = diff[:2], diff[2:]
        indent_current = indents[i]

        # Marker lines should auto-pass
        if allowed[i] or diff_type == "  ":
            valid[i] = True

        if diff_type in ["- ", "+ "]:
            # Search for the marker below
            for j in range(i + 1, len(diffs)):
                if indent_current == indents[j] and allowed[j]:
                    valid[i] = True
                if indent_current > indents[j]:
                    break

            # Search for the marker above
            for j in range(i - 1, -1, -1):
                if indent_current == indents[j] and allowed[j]:
                    valid[i] = True
                if indent_current > indents[j]:
                    break

    if not all(valid):
        feedback = f"You must strictly follow the provided template and only modify the code where it is marked with {allowed_change}!"

    return all(valid), feedback
