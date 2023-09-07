import pytest

from utils import extract_python_code


@pytest.mark.parametrize(
    "input_text, expected_output",
    [
        (
            "Here's a Python code:\n```python\ndef add(a, b):\n    return a + b\n```",
            "def add(a, b):\n    return a + b",
        ),
        ("Here's a code:\n```\ndef subtract(a, b):\n    return a - b\n```", ""),
        (
            "Here's some Python code:\n```python\ndef multiply(a, b):\n    return a * b\n```\nAnd another one:\n```python\ndef divide(a, b):\n    return a / b\n```",
            "def multiply(a, b):\n    return a * b\ndef divide(a, b):\n    return a / b",
        ),
    ],
)
def test_extract_python_code(input_text, expected_output):
    actual_output = extract_python_code(input_text).strip()
    assert (
        actual_output == expected_output.strip()
    ), f"Expected: {expected_output.strip()}, Got: {actual_output}"
