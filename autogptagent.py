import openai
import os


class AutoGPTAgent:
    def __init__(self, api_key):
        openai.api_key = api_key

    def handle_request(self, user_input):
        actions = [
            "extract_task_description",
            "generate_python_code",
            "create_python_file",
            "test_and_correct_python_file",
        ]
        context = {
            "user_input": user_input,
            "task_description": None,
            "generated_code": None,
            "filename": "generated_code.py",
        }

        while actions:
            summarized_context = self.summarize_context(context)
            prompt = (f"Étant donné le contexte {summarized_context}"
                      f", quelle action devrais-je entreprendre ensuite parmi {actions} ?")
            response = openai.Completion.create(
                model="text-davinci-003", prompt=prompt, max_tokens=3000
            )
            action = response.choices[0].text.strip()
            action = action.lower()
            if action == "extract_task_description" or "extract" in action:
                context["task_description"] = self.extract_task_description(
                    context["user_input"]
                )
            elif "generate_python_code" in action or "générer" in action:
                context["generated_code"] = self.generate_python_code(
                    context["task_description"]
                )
            elif action == "create_python_file" or "créer" in action:
                self.create_python_file(context["generated_code"], context["filename"])
            elif action == "test_and_correct_python_file" or "test" in action:
                self.test_and_correct_python_file(context["filename"])

            if action in actions:
                actions.remove(action)
            else:
                print(f"Action '{action}' non reconnue ou déjà effectuée.")
                continue

    def generate_python_code(self, task_description):
        if task_description:
            prompt = f"Je souhaite un code Python pour {task_description}. Pouvez-vous me fournir un exemple ?"
            response = openai.Completion.create(
                model="text-davinci-003", prompt=prompt, max_tokens=2000
            )
            generated_code = response.choices[0].text.strip()
            return generated_code
        else:
            return None

    def create_python_file(self, code, filename="generated_code.py"):
        try:
            with open(filename, "w", encoding="utf-8") as file:
                file.write(code)
                file.flush()
            print(f"Fichier {filename} créé avec succès !")
        except Exception as e:
            print(f"Erreur lors de la création du fichier {filename} : {e}")

    def test_and_correct_python_file(self, filename="generated_code.py"):
        while True:
            exit_code = os.system(f"python {filename}")
            if exit_code == 0:
                print(f"Le fichier {filename} fonctionne correctement.")
                break
            else:
                print(f"Le fichier {filename} a rencontré une erreur.")
                correction = self.get_correction_from_chatgpt(filename)
                with open(filename, "w") as file:
                    file.write(correction)

    def get_correction_from_chatgpt(self, filename="generated_code.py"):
        with open(filename, "r") as file:
            code_content = file.read()
        prompt = f"Corrigez les erreurs dans le code Python suivant :\n{code_content}"
        response = openai.Completion.create(
            engine="text-davinci-003", prompt=prompt, max_tokens=2049
        )
        corrected_code = response.choices[0].text.strip()
        return corrected_code

    def extract_task_description(self, user_input):
        prompt = f"Quelle est la tâche principale décrite dans cette demande : '{user_input}'?"
        response = openai.Completion.create(
            model="text-davinci-003", prompt=prompt, max_tokens=2049
        )
        task_description = response.choices[0].text.strip()
        return task_description

    def summarize_context(self, context):
        prompt = f"Résumez le contexte suivant : {context}"
        print(f"summarize = {prompt}")
        response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=2000)
        return response.choices[0].text.strip()
