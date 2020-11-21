import json
import os
import io

class Testiluokka:
    def __init__(self) -> None:
        self.juusto = "testikappale"
        self.uijuma = "jos tää toimis"
        self.petteripunakuono = "homppeli"
        self.ika = 1
        self.onnellisuus = -1
        self.kaverit = None
        self.tulevatParisuhteet = 0
        self.menneetParisuhteet = 0
    
    
testiKakka = Testiluokka()
sverigeKötbullar = Testiluokka()

jsonText = json.dumps(testiKakka.__dict__)
jsonText += f"\n{json.dumps(sverigeKötbullar.__dict__)}"

with open(os.path.join(os.path.dirname(__file__), "testi.json"), "w") as f:
    f.write(jsonText)


with open(os.path.join(os.path.dirname(__file__), "testi.json"), "r") as f:
    print(json.loads(f.read()))

    