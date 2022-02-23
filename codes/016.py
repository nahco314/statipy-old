# global variable in function, recursive funtion, complex code

## 4

def DFS(s):
    seen[s] = True
    order.append(s)
    for i in g[s]:
        if not seen[i]:
            DFS(i)


n, m = map(int, input().split())
g = [[] for _ in range(n)]
for i in range(m):
    u, v = map(int, input().split())
    g[u-1].append(v-1)

order = []
seen = [False] * n
DFS(0)

print(order)
