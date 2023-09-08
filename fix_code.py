import openai

from skill_class import Skill
from utils import extract_python_code


class FixCodeSkill(Skill):
    def execute(self, filename: str, error_message: str):
        with open(filename, "r") as file:
            code_content = file.read()

        prompt = (
            f"Given the following Python code:\n\n"
            f"{code_content}\n\nAnd the error message:\n\n"
            f"{error_message}\n\nPlease suggest a correction."
            f"I only want a correction in python, I don't want any explanation"
        )

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
        )

        suggested_fix = response.choices[0].message["content"]
        modified_code = extract_python_code(suggested_fix)

        if modified_code.strip() != code_content.strip():
            with open(filename, "w") as file:
                file.write(modified_code)
            return f"Correction applied to {filename}."
        else:
            return "No correction needed."
