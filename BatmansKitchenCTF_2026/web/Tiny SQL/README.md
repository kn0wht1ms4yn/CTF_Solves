#### Tiny SQL
- points earned: 192
#### Where's the flag?
- The flag is loaded into the `app.py` file via an environment variable and used in the response to the `/forum/post/<int:post_id>` route if `post_id` is 3.

#### Notes / Intuition
- This was a weird challenge.  It provided a single source code file, `app.py`, and in that file it imports a library, `tinysql`, which appeared to be a customer library based on the code.
	- It's worth noting here that I had attempted some standard sql payloads without any luck.
	- There was another challenge `Tiny SQL 2` that actually includes the source for the `tinysql` library and makes the solution for this one clear.
	- In other words, I was unable to solve this challenge until i saw the source for `tinysql` in the `Tiny SQL 2` challenge.
- While reviewing the code I see a bunch of statements that look lilke they're crafting sql queries for the db.
	- `conn.query(f'I:bob:{token_hex(4)}')`
	- `code, results = conn.query('S:' + request.form['user'] + ':' + request.form['pass'])`
	- code, author = conn.query('S:' + str(post_id))
	- It's pretty easy to see that query strings starting with `I` are insert statements and queries that start with `S` are select statements.
- Before seeing the `tinysql` source code I was thinking that these query strings were being turned into their equivalent sql query.
	- For example, `I:bob:{token_hex(4)}` gets converted to something lik e`insert into users (name, token) values ('bob'. 11223344)`
	- This prompted me to try standard sql injection payloads to bypass the auth form.
		- For example, `username=bob&password=' or 1=1#`.
		- None of my attempts worked.
- Getting a chance to review the tinysql code made this a bit easier.
- The backend DB is not sql at all.  It is more like redis where data is stored in a file, each line represents an entry, each field in an entry is separated by a `:`.
- The DB is used to keep track of users.
- Looking through the app source code you can see that there is some mechanism that handles the `#` comment character.  This mechanism is defined in the `clean` function.
	```python
	def clean(stmt):
	    # remove comments and validate syntax
	    stmt = stmt.split('#')[0]
	    if len(stmt) < 1: return 'err', b'e:nullstmt', stmt
	    if (queryType := stmt[0]) not in TYPES: return 'err', b'e:querytype', stmt
	    if stmt.count(':') > 2 or stmt.count(':') < 1: return 'err', b'e:syntaxerror', stmt
	    return 'clean', queryType, stmt
	```
	- `stmt` at the beginning of this function might be `S:1#:`
	- after `stmt = stmt.split('#')[0]` `stmt` becomes `S:1`
	- Assert that the first character is `S` or `I`
	- Assert the the number of `:` in the current `stmt` is 1 or 2
	- return
	- Logic is kind of confusing but it's important to know the if `stmt` is `S:1#:` going into this function, then it will be returned as `S:1`
- There are 2 Select query type based on the number of parameters that are received in the query. For example:
	- `S:1` is a single param query
	- `S:bob:pw` is a 2 param query
- The single param query is user for determining which author created a post and expects a `user_id`.
- The 2 param query is used for validating that a user has provided the correct username and password and expects a username and password.
- Each query returns the same data structure `final = f"r:{tdb_id}:{tdb_user}:{tdb_pw}"`
- The problem
	- The login logic expects that there will be a 2 param query like `S:bob:bobspw`
	- However, it becomes a single param query if it is given `S:bob#:bobspw`
- This means that the login can be bypassed by providing a valid `user_id` followed by a `#` as the username

#### Solution
- Bypass the login with the following request:
```http
POST /login HTTP/1.1
Host: me:3000
Content-Length: 13
Content-Type: application/x-www-form-urlencoded

user=1#&pass=
```
- this returns a valid cookie that can be used to access the flag post
```http
GET /forum/post/3 HTTP/1.1
Host: me:3000
Content-Length: 13
Content-Type: application/x-www-form-urlencoded
Cookie: session=eyJ1c2VybmFtZSI6ImpvIn0.aZ0BRA.3XVzsEBdkslgd5XMo31ESBpk4fA


```
