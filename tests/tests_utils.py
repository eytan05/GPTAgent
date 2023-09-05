import pytest

from utils import extract_python_code


@pytest.mark.parametrize(
    "text,expected_string",
    [
        (
            "Here is the Python code to calculate the sum of two numbers:"
            "```python"
            "def calculate_sum(a, b):"
            "    return a + b"
            "```"
            "Example Output:"
            "```"
            "The sum of 5 and 7 is: 12"
            "```",
            "def calculate_sum(a, b):" "    return a + b",
        )
    ],
)
def test_extract_python_code(text, expected_string):
    result_string = extract_python_code(text)
    assert result_string[0] == expected_string
