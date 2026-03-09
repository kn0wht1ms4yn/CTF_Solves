#### Days Of Future Past
- points earned: 50
#### Where's the flag?
- There was no source code provided with this challenge so the definitive location of the flag is unknown.
- The challenge description hints that the flag is contained within a 'secure message' inside the app.
#### App Summary
- The app has 2 features
	- The user can register.
	- The user can login.
- Something interesting is that when a user logs in, they are not brought to any profile page or anything, instead that are given a JWT token.
#### Notes / Intuition
- There's some interesting information in the src for the `/` route.
	```
	<!-- Debug endpoint available at /api/v1/health for system status -->
	
	<!-- ... TRUNCATED -->
	
	<!-- TODO: Remove before production deployment -->
	<!-- Developer Notes:
		- API Base: /api/v1/
		- Backup config was moved to /backup/ directory
		- Old JS app bundle still references config paths, clean up later
		- See /static/js/app.js for frontend API integration
	-->
	```
	- `API Base /api/v1` - there is an API
	- `Debug endpoint available at /api/v1/health` - api route
	- `Backup config moved to /backup/ directory` - a backup config exists in the `/backup` dir
	- `Old JS app bundle still references config paths` - JS might contain the name of the backup config file
	- `See /static/js/app.js for frontend API integration` - Perhaps some more intel.
- `app.js` has some interesting information
	```
	// TODO: Remove hardcoded backup path reference before production
	// The config backup at /backup/config.json.bak should be deleted
	```
	- `/backup/config.json` - backup config path
	- `/health, /debug, /auth/register, /auth/login, /vault/messages'` - valid api routes
	- There is some code that sends a request to `/api/v1/debug` with a header `X-API-KEY`
		```
		window.CryptoVaultAPI = {
			call: async function(endpoint, options = {}) {
				const url = CONFIG.apiBase + endpoint;
				const token = localStorage.getItem('jwt_token');
				
				const headers = {
					'Content-Type': 'application/json',
					...options.headers
				};
		
				if (token) {
					headers['Authorization'] = `Bearer ${token}`;
				}
		
				try {
					const response = await fetch(url, { ...options, headers });
					return await response.json();
				} catch (error) {
					console.error('[CryptoVault]', 'API call failed:', error);
					return { error: 'Network error' };
				}
			},
		
			// ... REDACTED
		
			// Debug info (requires API key)
			debug: function(apiKey) {
				return this.call('/debug', {
					headers: { 'X-API-Key': apiKey }
				});
			},
			
			// ... REDACTED
		```
		- This generates an api request.  Things I find interesting are
			- an `Authorization` header is being set with `jwt_token` from local storage.  I suspect that this is probably the jwt that was received during authentication.
			- an `X-API-Key` header is set for a request that goes to `/api/v1/debug`
- Sending an empty response (no jwt or api key) results in the following
	```json
	{
	    "error": "Invalid or missing API key",
	    "hint": "Did you check the backup files?"
	}
	```
- A request to `/backup/config.json.bak` results in the following
	```json
	{
	    "api_key": "d3v3l0p3r_acc355_k3y_2024",
	    "app_name": "CryptoVault",
	    "database": "sqlite:///cryptovault.db",
	    "debug_mode": true,
	    "internal_endpoints": ["/api/v1/debug", "/api/v1/health", "/api/v1/vault/messages"],
	    "jwt_algorithm": "HS256",
	    "notes": "Remember to rotate the API key before production deployment!",
	    "version": "1.0.3-internal"
	}
	```
	- The `api_key` is of particular interest given the context of the app so far.
	- Can I now get something out of `/api/v1/debug`?
- Access to `/api/v1/debug` is obtained by sending a request with the `X-API-Key` header set to `d3v3l0p3r_acc355_k3y_2024`.  It returns the following
	```json
	{
	    "debug_info": {
	        "auth_config": {
	            "algorithm": "HS256",
	            "roles": ["viewer", "editor", "admin"],
	            "secret_derivation_hint": "Company name (lowercase) concatenated with founding year",
	            "secret_key_hash_sha256": "e53e6e2d3018dce302f876eda97d3852f5f1a81192a5f947ed89da9832ea17b8",
	            "token_expiry_hours": 2
	        },
	        "company_info": {
	            "domain": "cryptovault.io",
	            "founded": 2026,
	            "name": "CryptoVault"
	        },
	        "framework": "Flask",
	        "python_version": "3.11.x",
	        "server": "CryptoVault v1.0.3",
	        "vault_info": {
	            "access_level_required": "admin",
	            "encryption_method": "XOR stream cipher",
	            "endpoint": "/api/v1/vault/messages",
	            "total_encrypted_messages": 15
	        },
	        "warning": "This debug endpoint should be disabled in production!"
	    }
	}
	```
	- `secret_derivation_hint` and `secret_key_hash_sha256` are both interesting but `secret_derivation_hint` explains how the secret key was made.
		- The main route `/` contains the name CryptoVault and a founded year 2026
		- Can I use this to forge a token for another role/user?
- Before attempting to forge a jwt, I want to try to get a feel for where I might be able to use a forged jwt,
	- Send a request to `/api/vault/messages` and it replies
		```json
		{
		    "error": "Missing or invalid Authorization header",
		    "format": "Bearer <token>"
		}
		```
	- Send another request but provide a jwt via the `Authorization` header. (Using the hwt obtained during login).  It replies:
		```json
		{
		    "error": "Insufficient privileges",
		    "message": "Only administrators can access the encrypted vault.",
		    "required_role": "admin",
		    "your_role": "viewer"
		}
		```
	- This is enough to inform a jwt forgery vector
		- The original jwt contains a field `role` which, in my case, is set to `viewer`
		- If I can create a new jwt with a role set to something like `admin` then maybe it will allow me to access the `/api/vault/messages` route.
- Creating a jwt with `jwt_tool.py`
	- `jwt_tool $jwt -S hs256 -p cryptovault2026 -I -pc role -pv admin`
	- `$jwt` in this example is the original jwt that was returned during the login process.
	- This jwt works to get access to `/api/v1/vault/messages`
- The `/api/v1/vault/messages` route returns the following.
	```json
	{
	    "access_level": "admin",
	    "disclaimer": "* Marketing department wrote this. Security team disagrees.",
	    "encryption": "XOR stream cipher (military-grade*)",
	    "messages": [{
	        "ciphertext_hex": "05c1534391cdc745386361e7e94b94c2819b45582673c78aba3b27cad5eb3f57bcb33bf1a7c4a16a17f76c02a8bee5a9f458b1ac52b85c0af52f8a4864f74b1f66f6235e3e6c7d4a793a809669b4e0f2fb221bf652058dc9c6b27d7948ff9b84d657f66d3b8c74f7d0",
	        "id": 1,
	        "length": 105,
	        "timestamp": "2026-01-01T10:00:00Z"
	    },
	    ...]
	}
	```
	- The response above is truncated and the actual messages contains 15 items with 15 different ciphertexts.
- The entire app is flooded with hints on the encryption of the messages.  For example, the landing page for this app contains `Store your most sensitive messages with our state-of-the-art XOR stream cipher protection`.
	- I learned in past CTFs that given a set of ciphertexts that were all created by XOR against the same secret key, then I can uncover the key and ciphertexts with an attack called a `cribwalk`

#### Crib Walk
- This attack makes use of the following fact
	- `plaintext ^ key = ciphertext`
	- `ciphertext ^ plaintext = key`
	- `ciphertext ^ key = plaintext`
- If I know that a specific plaintext exists within a ciphertext then I can do `ciphertext ^ plaintext` to get the key.  Then I can use the key to decode the other ciphertexts.
- More specifically,
	- In the context of this challenge, I guessed that the string `apoorvctf` existed somewhere in the messages.
	- Take any of the ciphertexts
	- starting at offset 0, XOR nine characters with `apoorvctf`
		- this results in a potential key used to encode the first 9 bytes
	- XOR the potential key against each one of the other ciphertexts at the same offset
		- IF the result looks like valid words (not garbage) then it is very like that the potential key is the correct key for that section of the cipher
		- IF the result is garbage, then this is not the correct key at this location
			- move on to the next offset
	- At this point you have 9 bytes of plaintext from each one of the ciphertexts.
	- You can now use the available plaintexts to make guesses on what the next/previous characters could be and then reiterate through this process to leak more bytes from each ciphertext.
- I have included the script which I used to do this in the repo.

#### Solution
- A series of information leaks yields access to `/api/v1/debug`
	- HTML source code on the main landing page
	- JS source code in `app.js`
	- api key leaked `/backup/config.json.bak`
- Gain access to `/api/v1/vault/messages` via a combination of information leaks and JWT forgery
	- `/api/v1/debug` provides information on how a secret key is made: `Company name (lowercase) concatenated with founding year`
	- Use `jwt_tool` to forge a valid `admin` jwt
		- `jwt_tool.py $jwt -S hs256 -p cryptovault2026 -I -pc role -pv admin`
- Attack the ciphertexts in `/api/v1/vault/messages` with `cribwalk` to obtain the flag.