from agent import (
    TaskPlanner,
    Agent,
    FinishSkill,
)
from fix_code import FixCodeSkill
from fix_test_code import FixTestCodeSkill
from generate_code import GenerateCodeSkill
from generate_test_code import GenerateTestCodeSkill
from install_module import InstallModuleSkill
from run_code import RunCodeSkill
from run_test_code import RunTestCodeSkill
from task_planner import AskForMoreInfoSkill
from utils import reformulate_request


def main():
    planner = TaskPlanner()
    agent = Agent(planner)
    agent.add_skill(AskForMoreInfoSkill("ask_info", "Demander des infos"))
    agent.add_skill(GenerateCodeSkill("generate_code", "Générer du code"))
    agent.add_skill(RunCodeSkill("run_code", "Exécuter du code"))
    agent.add_skill(FixCodeSkill("fix_code", "Corriger le code"))
    agent.add_skill(
        GenerateTestCodeSkill("generate_test_code", "Générer du code de test")
    )
    agent.add_skill(InstallModuleSkill("install_module", "Installer un module"))
    agent.add_skill(FinishSkill("finish", "Terminer l'exécution"))
    agent.add_skill(FixTestCodeSkill("fix_test_code", "Corriger le code de test"))
    agent.add_skill(RunTestCodeSkill("run_test_code", "Exécuter du code de test"))
    user_request = input("Veuillez entrer votre objectif: ")
    general_goal = reformulate_request(user_request)
    agent.execute(general_goal, max_iter=15)


if __name__ == "__main__":
    main()
