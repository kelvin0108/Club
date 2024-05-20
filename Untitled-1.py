import random
name=[]
n=int(input('請輸入班上總共有幾人'))
for i in range(n):
    name.append(i+1)
random.shuffle(name)
while len(name)>0:
    n = int(input('抽幾個'))
    if n > len(name):
        n = len(name)
    for i in range(n):
        print(name[0],end=' ')
        name.pop(0)             
    print(f"\n剩{len(name)}人")