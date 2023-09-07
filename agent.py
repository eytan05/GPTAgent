import os
import subprocess
import time

import openai
from dotenv import load_dotenv

from utils import (
    create_python_file,
    extract_python_code,
    extract_function_name,
    get_filename_from_user,
    extract_install_command,
)

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


class Skill:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def execute(self, *args, **kwargs):
        raise NotImplementedError(
            "La méthode execute doit être implémentée dans les sous-classes de Skill."
        )


class RunCodeSkill(Skill):
    def execute(self, filename: str):
        try:
            result = subprocess.run(
                ["python", filename], capture_output=True, text=True, check=True
            )
            print("The code run is valid ")
            return f"Output: {result.stdout}"
        except subprocess.CalledProcessError as e:
            if "No module named" in e.stderr:
                missing_module = e.stderr.split("'")[1]
                print(f"missing_module={missing_module}")
                install_feedback = InstallModuleSkill(
                    "install_module", "Installer un module"
                ).execute(missing_module)
                print(install_feedback)
                return self.execute(filename)
            else:
                print("Error Execution")
                return f"Error: {e.stderr}"
        except Exception as e:
            print(str(e))
            return str(e)


class GenerateCodeSkill(Skill):
    def execute(self, general_goal: str, filename: str):
        if os.path.isfile(path=f"./{filename}"):
            with open(filename, "r") as file:
                code = file.read()
            return code
        else:
            prompt = f"Write a Python code for: {general_goal}. I just want to have the code and an example of test"
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
            )
            openai_response = response.choices[0].message["content"]
            generated_code = extract_python_code(openai_response)
            create_python_file(generated_code, filename)
            if len(generated_code) < 100:
                feedback = generated_code
            else:
                feedback = f"Code généré avec succès et sauvegardé dans {filename}."
            return feedback


class FixCodeSkill(Skill):
    def execute(self, filename: str, error_message: str):
        with open(filename, "r") as file:
            code_content = file.read()

        prompt = (
            f"Given the following Python code:\n\n"
            f"{code_content}\n\nAnd the error message:\n\n"
            f"{error_message}\n\nPlease suggest a correction."
        )

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
        )

        suggested_fix = response.choices[0].message["content"]
        with open(filename, "w") as file:
            file.write(suggested_fix)

        return f"Correction applied to {filename}."


class AskForMoreInfoSkill(Skill):
    def execute(self, general_goal: str):
        return input(
            f"Je n'ai pas compris votre demande '{general_goal}'. Pouvez-vous fournir plus d'informations? "
        )


class GenerateTestCodeSkill(Skill):
    def execute(self, function_name: str, code: str, filename: str):
        if code is None or filename is None or function_name is None:
            return None
        prompt = (
            f"Given the following Python function:\n\n{code}\n\nPlease generate a unittest test case for this function."
            f"the function is imported from {filename}"
        )
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
        )
        openai_response = response.choices[0].message["content"]
        test_code = extract_python_code(openai_response)
        test_filename = f"test_{function_name}.py"
        with open(test_filename, "w") as test_file:
            test_file.write(test_code)

        return (
            f"Test file {test_filename} created with content:\n{test_code}",
            test_filename,
        )


class InstallModuleSkill(Skill):
    def execute(self, missing_module: str):
        prompt = (
            f"Give me the command line to install {missing_module}. "
            f"Pip is already installed. The command must be in bash"
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
                result = subprocess.run(
                    install_command.split(), capture_output=True, text=True, check=True
                )
                return f"Module {missing_module} installed successfully."
            except subprocess.CalledProcessError:
                return f"Error installing {missing_module}."
        print(f"install command = {install_command}")
        try:
            result = subprocess.run(
                install_command.split(), capture_output=True, text=True, check=True
            )
            return f"Module {missing_module} installed successfully."
        except subprocess.CalledProcessError:
            return f"Error installing {missing_module}."


class FinishSkill(Skill):
    def execute(self, *args, **kwargs):
        print(
            "Toutes les tâches ont été complétées ou l'agent a atteint un état final souhaité."
        )
        return "Terminé"


class TaskPlanner:
    def get_next_skill(
        self,
        skills: list[Skill],
        general_goal: str,
        executed_skills: list[str],
        feedback: str,
    ) -> Skill:
        skill_list_name = [skill.name for skill in skills]
        executed_skills_str = (
            ", ".join(executed_skills[-3:]) if executed_skills else "none"
        )
        summary = (
            f"User's request was: '{general_goal}'. "
            f"The last executed skills were: {executed_skills_str}. "
            f"Feedback from the last skill: '{feedback}'. "
            f"Based on the context, which skill from {skill_list_name} should be executed next?"
        )

        print(f"summary = {summary}")
        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=[{"role": "user", "content": summary}],
            max_tokens=50,
        )
        suggested_skill_name = None
        for skill_name in skill_list_name:
            if skill_name in response.choices[0].message["content"]:
                suggested_skill_name = skill_name
                break
        if suggested_skill_name is None:
            return AskForMoreInfoSkill("ask_info", "Demander plus d'informations")
        print(f"suggested_skill_name= {suggested_skill_name}")
        for skill in skills:
            if skill.name == suggested_skill_name:
                return skill

        return AskForMoreInfoSkill("ask_info", "Demander plus d'informations")


class Agent:
    def __init__(self, planner: TaskPlanner):
        self.planner = planner
        self.skills = []
        self.executed_skills = []

    def add_skill(self, skill: Skill):
        self.skills.append(skill)

    def execute(self, general_goal: str, max_iter=None):
        feedback = ""
        generated_code = ""
        iterations = 0
        filename = get_filename_from_user()

        while True:
            if max_iter and iterations >= max_iter:
                break

            skill = self.planner.get_next_skill(
                self.skills,
                general_goal,
                self.executed_skills,
                feedback,
            )
            if skill is None:
                print("Aucune compétence correspondante trouvée. Arrêt de l'exécution.")
                break

            if skill.name == "finish":
                break

            if isinstance(skill, GenerateCodeSkill):
                generated_code = skill.execute(general_goal, filename)
                feedback = generated_code
            elif isinstance(skill, RunCodeSkill):
                feedback = skill.execute(filename)
            elif isinstance(skill, FixCodeSkill):
                if "Error" not in feedback:
                    feedback = "Le code semble correct, aucune correction nécessaire."
                    continue
                else:
                    feedback = skill.execute(filename, feedback)
            elif isinstance(skill, GenerateTestCodeSkill):
                function_name = extract_function_name(filename)
                result = skill.execute(
                    function_name=function_name, code=generated_code, filename=filename
                )
                if isinstance(result, tuple) and len(result) == 2:
                    feedback, test_filename = result
                else:
                    feedback = result
                    test_filename = None
                test_feedback = RunCodeSkill("run_code", "Exécuter du code").execute(
                    test_filename
                )
                if test_feedback is not None and feedback is not None:
                    feedback += f"\n{test_feedback}"
            elif isinstance(skill, AskForMoreInfoSkill):
                feedback = skill.execute(feedback)

            self.executed_skills.append(skill.name)

            if feedback and (
                feedback.startswith("Output:")
                or "Fichier" in feedback
                or "Test réussi" in feedback
            ):
                self.skills = [s for s in self.skills if s.name != skill.name]

            iterations += 1
            time.sleep(2)
