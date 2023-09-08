import ast
import importlib
import re
from typing import List, Optional

import openai


def is_module_installed(module_name: str) -> bool:
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False


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
            file.flush()
        print(f"Fichier {filename} créé avec succès !")
    except Exception as e:
        print(f"Erreur lors de la création du fichier {filename} : {e}")


def extract_python_code(text):
    # Recherche des balises de code
    matches = re.findall(r"```python(.*?)```", text, re.DOTALL)
    if matches:
        return matches[0].strip()

    patterns = [
        r"import .*",
        r"from .* import .*",
        r"def .*:",
        r"class .*:",
        r"for .* in .*:",
        r"if .*:",
        r"elif .*:",
        r"else:",
        r"while .*:",
        r"print(.*",
    ]
    code_lines = []
    for line in text.split("\n"):
        if any(re.match(pattern, line) for pattern in patterns):
            code_lines.append(line)
    return "\n".join(code_lines)


def extract_function_name(filename: str) -> Optional[str]:
    with open(filename, "r") as file:
        code = file.read()
    match = re.search(r"def (\w+)\(", code)
    if match:
        return match.group(1)
    return None


def extract_install_command(response_text):
    match = re.search(r"pip install (-U)?\s*([\w\-]+)", response_text)
    if match:
        return match.group(0)
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


def reformulate_request(user_request: str) -> str:
    prompt = f"Reformulate the following request to create a Python function with the goal of: '{user_request}'"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
    )
    reformulated_request = response.choices[0].message["content"]
    return reformulated_request
