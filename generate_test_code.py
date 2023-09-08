import openai

from skill_class import Skill
from utils import extract_python_code


class GenerateTestCodeSkill(Skill):
    def execute(self, filename: str):
        if filename is None:
            return None
        with open(filename, "r") as file:
            code = file.read()
        prompt = (
            f"Given the following Python function:\n\n{code}\n\nPlease generate a unittest test case for this function. "
            f"the function is imported from {filename}. "
            f"The test file must be complete with concrete test. "
            f"Please provide the code enclosed within Python code blocks (```python ... ```)."
        )
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
        )
        openai_response = response.choices[0].message["content"]
        test_code = extract_python_code(openai_response)
        test_filename = f"test_{filename}"
        with open(test_filename, "w") as test_file:
            test_file.write(test_code)

        return (
            f"Test file {test_filename} created with content:\n{test_code}",
            test_filename,
        )
