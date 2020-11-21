import json

class Juusto:
    def __init__(self) -> None:
        self.haisee = True
        self.Tero = 69
        self.hungalabungala = 420
        self.stringi = "string"
        
print(json.dumps(Juusto().__dict__))