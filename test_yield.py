def a():
    for i in range(0, 10):
        yield i


def b():
    c = a()
    for j in c:
        print(j)


b()
