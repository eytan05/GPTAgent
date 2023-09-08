import os
import time

import openai
from dotenv import load_dotenv

from fix_code import FixCodeSkill
from fix_test_code import FixTestCodeSkill
from generate_code import GenerateCodeSkill
from generate_test_code import GenerateTestCodeSkill
from install_module import InstallModuleSkill
from run_code import RunCodeSkill
from run_test_code import RunTestCodeSkill
from skill_class import Skill
from task_planner import TaskPlanner, AskForMoreInfoSkill
from utils import (
    get_filename_from_user,
)

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


class FinishSkill(Skill):
    def execute(self, *args, **kwargs):
        print(
            "Toutes les tâches ont été complétées ou l'agent a atteint un état final souhaité."
        )
        return "Terminé"


class Agent:
    def __init__(self, planner: TaskPlanner):
        self.planner = planner
        self.skills = []
        self.executed_skills = []

    def add_skill(self, skill: Skill):
        self.skills.append(skill)

    def execute(self, general_goal: str, max_iter=None):
        feedback = ""
        iterations = 0
        filename = get_filename_from_user()
        test_filename = None
        missing_module = None
        while True:
            print(f"filename={filename}")

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
                feedback = skill.execute(general_goal, filename)
            elif isinstance(skill, RunCodeSkill):
                feedback = skill.execute(filename)
                if "Missing module:" in feedback:
                    missing_module = feedback.split("Missing module:")[-1].strip()
            elif isinstance(skill, FixCodeSkill):
                if "Error" not in feedback:
                    feedback = "Le code semble correct, aucune correction nécessaire."
                    continue
                else:
                    feedback = skill.execute(filename, feedback)
            elif isinstance(skill, GenerateTestCodeSkill):
                result = skill.execute(filename=filename)
                if isinstance(result, tuple) and len(result) == 2:
                    feedback, test_filename = result
                else:
                    feedback = result
                    test_filename = None
                if test_filename is not None:
                    test_feedback = "Test file has been generated"
                else:
                    test_feedback = "No test file generated."
                if test_feedback is not None and feedback is not None:
                    feedback += f"\n{test_feedback}"
            elif isinstance(skill, AskForMoreInfoSkill):
                feedback = skill.execute(feedback)
            elif isinstance(skill, FixTestCodeSkill):
                feedback = skill.execute(test_filename, feedback)
            elif isinstance(skill, RunTestCodeSkill):
                feedback = skill.execute(test_filename)
                if "Missing module:" in feedback:
                    missing_module = feedback.split("Missing module:")[-1].strip()
            elif isinstance(skill, InstallModuleSkill):
                feedback = skill.execute(missing_module)
            self.executed_skills.append(skill.name)

            if feedback and (
                feedback.startswith("Output:")
                or "Fichier" in feedback
                or "Test réussi" in feedback
            ):
                self.skills = [s for s in self.skills if s.name != skill.name]

            iterations += 1
            time.sleep(2)
