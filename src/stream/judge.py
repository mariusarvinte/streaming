import os
import sys
import dspy

lm = dspy.LM(
    model="openrouter/nvidia/nemotron-3-nano-30b-a3b:free",
    api_key=os.environ["OPENROUTER_API_KEY"],
    temperature=1.0,
    cache=False,
)
dspy.configure(
    lm=lm,
)


class ProblemSolving(dspy.Signature):
    """You are an expert in solving algorithmic problems using Python"""

    problem: str = dspy.InputField(
        desc="The description of the problem to be solved",
    )
    cases: list[tuple[list[int], list[int]]] = dspy.InputField(
        desc="A list of paired inputs and outputs for the problem",
    )

    prev_solution: dspy.Code["Python"] = dspy.InputField(
        desc="The current solution to the `problem`"
    )

    suggestions: str = dspy.InputField(
        desc="Suggestions from an expert programmer on how to improve the code"
    )

    explanation: str = dspy.OutputField(
        desc="An explanation of the implementation of `solution`"
    )
    solution: dspy.Code["Python"] = dspy.OutputField(
        desc="Code that when executed with the inputs, produces the expected outputs",
    )
    runtime: dspy.Code["Python"] = dspy.OutputField(
        desc="Code that profiles the execution time of `solution` when running on `cases`",
    )
    memory: dspy.Code["Python"] = dspy.OutputField(
        desc="Code that profiles the runtime memory usage of `solution` when running on `cases`",
    )
    test: dspy.Code["Python"] = dspy.OutputField(
        desc="Code that tests the `solution` on the provided `cases` and runs `runtime` and `memory` measurements",
    )


class SolutionJudge(dspy.Signature):
    """You are an expert code evaluator, focused on optimal implementations."""

    candidate: dspy.Code["Python"] = dspy.InputField(
        desc="The code whose complexity will be evaluated"
    )
    suggestions: str = dspy.OutputField(
        desc="Suggestions to improve the performance of the code, without sacrificing correctness"
    )


coder = dspy.Predict(ProblemSolving)
judge = dspy.ChainOfThought(SolutionJudge)
steps = 3

# Perform the task on some inputs
inputs = {
    "problem": """Given an integer array `nums` sorted in non-decreasing order, consider the number of unique elements in `nums` to be `k`.
Return the number of unique elements `k`.""",
    "cases": [
        ([1, 1, 4, 6, 7, 9], [5]),
        ([4, 4, 4, 4, 4], [1]),
        ([26, 999, 1003], [3]),
    ],
}

local_inputs = inputs
for i in range(steps):
    if i == 0:
        local_inputs["prev_solution"] = ""
        local_inputs["suggestions"] = ""

    # Predict solution
    pred = coder(**local_inputs)

    # Judge solution
    judge_inputs = {"candidate": pred.solution.code}
    judgement = judge(**judge_inputs)

    # Pass feedback
    local_inputs["prev_solution"] = pred.solution.code
    local_inputs["suggestions"] = judgement.suggestions


# Save the original stdout to restore it later
original_stdout = sys.stdout
with open("./history.txt", "w") as f:
    # Redirect stdout to the file
    sys.stdout = f
    dspy.inspect_history(n=10)
# Restore stdout to the original (usually the console)
sys.stdout = original_stdout
