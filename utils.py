import ast
import re
from typing import List, Optional


def extract_imports(filename: str) -> list[str]:
    with open(filename, "r") as file:
        node = ast.parse(file.read())

    imports = [n.name for n in ast.walk(node) if isinstance(n, ast.Import)]
    from_imports = [n.module for n in ast.walk(node) if isinstance(n, ast.ImportFrom)]

    return imports + from_imports


def get_missing_modules(filename: str) -> list[str]:
    modules = extract_imports(filename)
    missing_modules = []

    for module in modules:
        try:
            exec(f"import {module}")
        except ModuleNotFoundError:
            missing_modules.append(module)

    return missing_modules


def create_python_file(code: str, filename):
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(code)
        print(f"Fichier {filename} créé avec succès !")
    except Exception as e:
        print(f"Erreur lors de la création du fichier {filename} : {e}")


def extract_python_code(text: str):
    pattern = r"```python(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches


def extract_function_name(code: str) -> Optional[str]:
    match = re.search(r"def (\w+)\(", code)
    if match:
        return match.group(1)
    return None


def get_str_from_list(text_list: List[str]) -> str:
    if len(text_list) > 0:
        code = text_list[0]
        for i in range(1, len(text_list)):
            code = code + "\n" + text_list[i]
        return code
    else:
        return ""


def get_filename_from_user() -> str:
    filename = input("Choose a filename for your new python file: ")
    return filename + ".py"
