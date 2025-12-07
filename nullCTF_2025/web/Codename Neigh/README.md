#### Codename Neigh
- points earned: 50

#### Notes
- I'm not really familiar with Pony lang so I'll do my best here.
- The flag is located in the `app/public/flag.html` file.
- The app will serve this file to requests for `/flag` if:
	- the request is for localhost
	- the requested path is not `/flag`
- However, the mechanism for validating these items are flawed.
	```
	try
	  conn = ctx.request.header("Host") as String
	end
	
	let path: String = ctx.request.uri().string()
	
	if (conn == "127.0.0.1") and (path != "/flag") and (path != "flag") then
		// serve flag.html
	```
- The problem with the verification for localhost is that the app is just checking that the `Host:` header is `127.0.0.1`.  An attacker can easily set the header to `1127.0.0.1` as long as the web server is not doing Host based routing.
- The problem with the requested path validation is that the app is testing the full URI against `/flag`.  An attacker can pass this check by including query parameters.  For example, `/flag?meow` routes the request to the correct handler and also passes the `/flag` check.
#### Solution
```http
GET /flag?meow HTTP/1.1
Host: 127.0.0.1


```