import subprocess
import sys

import openai

from skill_class import Skill
from utils import extract_install_command


class InstallModuleSkill(Skill):
    def execute(self, missing_module: str):
        if missing_module is None:
            return "There is no missing module"
        prompt = (
            f"Give me the command line to install {missing_module}. "
            f"Pip is already installed. The command must be in bash and for the environment only"
        )

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
        )

        install_command = extract_install_command(
            response.choices[0].message["content"]
        )
        print(f"install_command={install_command}")
        if install_command:
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", install_command]
                )
                return f"Module {missing_module} installed successfully."
            except Exception as e:
                return f"Error installing {missing_module}. Reason: {str(e)}"
