import os

import openai

from skill_class import Skill
from utils import create_python_file, extract_python_code


class GenerateCodeSkill(Skill):
    def execute(self, general_goal: str, filename: str):
        if os.path.isfile(path=f"./{filename}"):
            return f"Code already generated"
        else:
            try:
                prompt = (
                    f"Write a Python code for: {general_goal}. "
                    f"Please provide the code enclosed within Python code blocks (```python ... ```)."
                )
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                )
                openai_response = response.choices[0].message["content"]
                generated_code = extract_python_code(openai_response)
                create_python_file(generated_code, filename)
                feedback = f"Code généré avec succès et sauvegardé dans {filename}."
                return feedback
            except Exception as e:
                return f"Error: {str(e)}"
