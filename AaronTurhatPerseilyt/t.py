def gen(x):
    while True:
        yield x + 1

s = gen(1)

for v in s:
    print(v)