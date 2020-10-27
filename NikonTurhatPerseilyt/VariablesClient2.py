import variablesTest as vt
def returnVariableByName(name: str):
    return getattr(vt, name)