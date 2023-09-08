import openai

from skill_class import Skill
from utils import extract_python_code


class FixTestCodeSkill(Skill):
    def execute(self, test_filename: str, error_message: str):
        if test_filename is None:
            return "Test file has not been generated yet"
        with open(test_filename, "r") as file:
            test_code_content = file.read()

        prompt = (
            f"Given the following Python test function:\n\n"
            f"{test_code_content}\n\nAnd the error message:\n\n"
            f"{error_message}\n\nPlease suggest a correction."
            f"I only want a correction in python, I don't want any explanation"
        )

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
        )

        suggested_fix = response.choices[0].message["content"]
        modified_test_code = extract_python_code(suggested_fix)
        with open(test_filename, "w") as file:
            file.write(modified_test_code)

        return f"Correction applied to {test_filename}."
