# range to list, comprehension, complex range

## 3

n = 100
r1 = [i for i in range(n)]
r2 = list(range(n))
e1 = [i for i in range(n) if i % 2 == 0]
e2 = [i for i in range(0, n, 2)]
