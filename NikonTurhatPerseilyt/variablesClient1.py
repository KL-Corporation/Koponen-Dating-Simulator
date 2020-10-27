import VariablesClient2 as vc2
import variablesTest as vt

print(vc2.returnVariableByName("variable4"))
print(vt.variable4)
vt.variable4 = 4
print(vc2.returnVariableByName("variable4"))
print(vt.variable4)
vt.variable4 = 9
print(vc2.returnVariableByName("variable4"))
print(vt.variable4)