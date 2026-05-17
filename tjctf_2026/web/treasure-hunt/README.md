#### treasure-hunt
- points earned: 100
#### Investigating the App
- This was just a fun, egg-hunt style challenge and no source code was provided.
- The challenge description states `Let's go hunt down some treasure! The flag is split into 4 parts. I'll give you the first one right here: tjctf`.
- The main app page is pretty basic and contains a button `Learn More`.
- Looking at the source for the main page I see  `<p hidden>_and_</p>` which appears to be a flag part.
- Clicking on `Learn More` brings me to another page `extra_info` which really doesn't seem to have anything special.  I checked the page source as well as `/static/style.css`.  I also checked `penguin.png` for anything that might indicate stenography.
- At this point I decided to check my browser cookies to see if I was given any cookies.  I find `silver-coffer={s1lv3r` which looks like another flag part.
	- Checking back through the requests I can see that when I clicked `Learn More` that it sent a POST request to `/` and in that response contained the `Set-Cookie` header for the `silver-coffer` cookie.
	- This doesn't really change anything but I was curious where and when I got the cookie.
- Continuing standard enumeration I check `/robots.txt` and get a new route in the reponse, `gold-coffer`.
	```
	User-agent: *
	Disallow: /gold-coffer
	Allow: /
	```
- Now, going to `/gold-coffer` on the live target returns `g0ld}` in the response body which is the final part of the flag that I needed
- Putting it all together I get.
	```
	tjctf{s1lv3r_and_g0ld}
	```
