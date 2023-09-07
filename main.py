from agent import (
    TaskPlanner,
    Agent,
    GenerateCodeSkill,
    RunCodeSkill,
    InstallModuleSkill,
    FinishSkill,
    GenerateTestCodeSkill,
    FixCodeSkill,
    AskForMoreInfoSkill,
)
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
    user_request = input("Veuillez entrer votre objectif: ")
    general_goal = reformulate_request(user_request)
    agent.execute(general_goal, max_iter=15)


if __name__ == "__main__":
    main()
