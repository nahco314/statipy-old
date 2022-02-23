# input list

## 3

n = int(input())
a = list(map(int, input().split()))  ## n
ans = 0
for i in a:
    ans += i
print(ans)
