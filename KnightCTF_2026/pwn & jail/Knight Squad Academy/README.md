#### Knight Squad Academy
- points earned: 100
#### Notes / Intuition
- I used `checksec` to begin investigating the binary
	```
	Arch:       amd64-64-little
	RELRO:      Full RELRO
	Stack:      No canary found
	NX:         NX enabled
	PIE:        No PIE (0x400000)
	```
	- `No Canary` indicates that I'm probably looking for a stack based buffer overflow.
	- `No PIE` indicates that I can probably use the hardcoded memory addresses
- I then tried just manually running binary to see if I could locate an overflow by provided large input strings.
	- I was able to get a `Seg Fault` with a large input to the `Enrollment Notes` prompt.
	- So this is probably the buffer I'm trying to overflow.
- Next, I used `Ghidra` to take a closer look at the binary and try to answer questions like `Is the flag loaded by the binary anywhere?` or `Am I trying to get command execution on the system?`
- Here's the section of code that relates to `Cadet Registration`
	```c
	void FUN_00401514(void)
	
	{
	  long lVar1;
	  void *pvVar2;
	  undefined1 local_78 [64];
	  undefined1 local_38 [40];
	  size_t local_10;
	  
	  puts("\n--- Cadet Registration ---");
	  puts("Cadet name:");
	  printf("> ");
	  fflush(stdout);
	  lVar1 = FUN_004011f7(0,local_38,0x20);
	  if (lVar1 < 0) {
	    FUN_004011c6("Input error.");
	  }
	  puts("Enrollment notes:");
	  printf("> ");
	  fflush(stdout);
	  local_10 = read(0,local_78,0xf0);
	  if ((long)local_10 < 1) {
	    FUN_004011c6("Input error.");
	  }
	  pvVar2 = memmem(local_78,local_10,"badge",5);
	  if (pvVar2 == (void *)0x0) {
	    pvVar2 = memmem(local_78,local_10,"token",5);
	    if (pvVar2 == (void *)0x0) {
	      puts("[Enrollment] Entry received.");
	      goto LAB_0040164b;
	    }
	  }
	  puts("[Audit] Entry queued for manual review.");
	LAB_0040164b:
	  printf("Welcome, Cadet %s.\n",local_38);
	  puts("Please wait for assignment.");
	  fflush(stdout);
	  return;
	}
	```
- `read(0,local_78,0xf0);` is reading `0xf0` or `240` bytes into `local_78` which has been defined to have `64` bytes.  This is what enables the overflow.
	- 40 bytes of space has also been reserved on the stack for `local_38`
	- Then i'll have a `rbp` and `ret`
	- So i'll need something like `112` or `120` bytes of offset here (I always get confused at this but I'll figure it out lol).
- Clicking through the functions I also noticed `FUN_004013ac` which, if `param_1 == 0x1337c0decafebeef` then it loads and prints the flag.
	```c
	void FUN_004013ac(long param_1)
	
	{
	  char local_98 [136];
	  FILE *local_10;
	  
	  if (param_1 != 0x1337c0decafebeef) {
	    puts("[SECURITY] Authorization failed.");
	    fflush(stdout);
	    FUN_004011c6("Session terminated.");
	  }
	  local_10 = fopen("./flag.txt","r");
	  if (local_10 == (FILE *)0x0) {
	    FUN_004011c6("Server error.");
	  }
	  local_98[0] = '\0';
	  local_98[1] = '\0';
	  // ... truncated
	  local_98[0x7e] = '\0';
	  local_98[0x7f] = '\0';
	  fgets(local_98,0x80,local_10);
	  fclose(local_10);
	  puts("[Registry] Clearance badge issued:");
	  puts(local_98);
	  fflush(stdout);
	  return;
	}
	```
- There's no other references to this function in the code, so I'm thinking that if I can set `param_1` then I can just `ret` to this function and get the flag.
- I used pwntools `ROP` to see if there is a `pop rdi; ret` gadget available.  There was, so at this point I think I have everything I need to pull this off.
	```python
	rop.find_gadget(['pop rdi', 'ret'])
	```
- I'm not too experienced with these so It's worth noting that I originally though that I would need to set `rdi` to a pointer to `0x1337c0decafebeef`.  I believe that would've been the case if `param_1` was a string, but since it is a long then `param_1` can contain the actual value.
- While writing out the solve script, I know that the stack should look like this:
	```
	[ padding ] [ pop_rdi ] [ 0x1337c0decafebeef ] [ FUN_004013ac ]
	```
#### Solution
- Overflow the `Enrollment Notes` buffer to reach `ret`
	- `pop rdi` to load `0x1337c0decafebeef` into rdi
	- then call `FUN_004013ac` which reads and prints the flag.
- I have added the solve script to this repo for reference.
