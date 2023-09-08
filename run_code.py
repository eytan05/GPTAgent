import re

from skill_class import Skill


class RunCodeSkill(Skill):
    def execute(self, filename: str):
        with open(filename, "r") as file:
            code = file.read()
        try:
            print("running code", code)
            exec(code, globals())
            print("Code running is ok")
            return "Code executed successfully."
        except Exception as e:
            print(str(e))
            match = re.search(r"'(.+?)' is not defined", str(e))
            if match:
                missing_module = match.group(1)
                return f"Error: {str(e)}. Missing module: {missing_module}"
            return f"Error: {str(e)}"
