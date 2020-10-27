lista = []

class Juusto:
    def __init__(self, juusto: int = 0) -> None:
        self.juusto = juusto
        self.Porkkana = "kakka"
        self.Tero = "Juutalainen"
        
    def deleteMe(self) -> None:
        del lista[self.juusto]
        
    def KerroJuusto(self):
        print(self.juusto)

for i in range(10): lista.append(Juusto(i))

lista[3].KerroJuusto()
print(len(lista))
lista[3].deleteMe()
print(len(lista))
lista[3].KerroJuusto()