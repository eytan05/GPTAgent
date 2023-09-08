import openai

from skill_class import Skill


class AskForMoreInfoSkill(Skill):
    def execute(self, general_goal: str):
        return input(
            f"Je n'ai pas compris votre demande '{general_goal}'. Pouvez-vous fournir plus d'informations? "
        )


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
            f"You don't need to execute all skills but at least 4 differents must be executed. "
            f"Feedback from the last skill: '{feedback}'. "
            f"Based on the context, which skill from {skill_list_name} should be executed next?"
        )
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
