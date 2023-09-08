class Skill:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def execute(self, *args, **kwargs):
        raise NotImplementedError(
            "La méthode execute doit être implémentée dans les sous-classes de Skill."
        )
