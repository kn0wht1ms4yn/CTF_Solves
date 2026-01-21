from pwn import *

p = remote('66.228.49.41', 1337)
p.recvuntil(b'> ')

min = 33
max = 126

i = 0
x = ((max - min) // 2) + min
flag = []
while True:
    print(f'[{i}] trying {x}')

    query = f'Q({i},{x})'
    p.sendline(query.encode())
    
    r = p.recvuntil(b'> ')
    r = r.split(b'\n')[0]
    r = int(r)
    print(f'{r=}')

    if r > 0: # guess is too high
        max = x
        x = ((max - min) // 2) + min
    elif r <0: # guess is too low
        min = x
        x = ((max - min) // 2) + min
    else: # guess is correct
        flag.append(x)
        min = 33
        max = 126
        x = ((max - min) // 2) + min
        i += 1
        print(f'{flag=}')
        if i >= 28: break
    
print(f'{flag=}')
flag = [chr(c) for c in flag]
flag = ''.join(flag)
print(f'{flag=}')