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
            import_error_match = re.search(r"No module named '(.+?)'", str(e))
            if import_error_match:
                missing_module = import_error_match.group(1)
                return f"Error: {str(e)}. Missing module: {missing_module}"
            name_error_match = re.search(r"'(.+?)' is not defined", str(e))
            if name_error_match:
                missing_module = name_error_match.group(1)
                return f"Error: {str(e)}. Missing module: {missing_module}"
            return f"Error: {str(e)}"
