import json

d = json.dumps({"dark": False}, indent=2)
print(d)

with open("ah.txt", "w") as f:
    f.write("KKKKKKKKKKKKKK")

print("done")