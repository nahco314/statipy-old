# complex swap

## 3

a, b, c, d, e, f = map(int, input().split())
a, b, c = c, b, a
a, b = b, a
a, b, c, d, e = e, f, a, b, b
a, b, c, f = f, d, a + b, c * f

print(a, b, c, d, e, f)
