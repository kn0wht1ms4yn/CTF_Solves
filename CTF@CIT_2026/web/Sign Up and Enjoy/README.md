#### Sign Up and Enjoy
- points earned: 886
#### Where's the flag?
- There's no source code with this challenge so the flag location is unknown.
#### Solution
- Investigation the app, I see a header `# Secure access for modern document operations.` with some functionality that allows login and registration.
- After creating an account and logging in I am brought to a `Creator Workspace` page.
- I don't see any functionality but there is a `Open Link Preview` link that leads to `/tools/link-preview`.
- On `/tools/link-preview` there's a form with a `Target URL` input and a button labeled `Fetch preview`.
	- I added a url for my exfil server and submitted it.
	- The page displayed `Currently Processing... this may take a moment.`
	- I waited
	- Then the page displayed `Error occurred, something went wrong.`
	- I did not see any requests in exfil server logs so it seems that no request was ever sent.
- I took a look at the client side source code and could see that the source that the server returns from the POST included some JS at the bottom
	```html
	<script>
		setTimeout(function() {
			var title = document.getElementById('preview-status-title');
			var copy = document.getElementById('preview-status-copy');
			if (title) {
				title.textContent = 'Error occurred, something went wrong.';
			}
			if (copy) {
				copy.textContent = 'The preview service could not complete the request at this time.';
			}
		}, 10000);
	</script>
	```
	- This basically just waits 10 seconds then displays `Error occurred, something went wrong.`
- At this point I'm thinking, 'wait, does this page even do anything?'
- I go back to the CTF page and look at the challenge description.
	- It is: `I'm confused, what does this application do exactly?`
	- 😂
- I spent some time looking through everything again making sure that I didn't miss anything.
- Eventually I got around to investigating the cookie which looked like a normal Flask issued cookie.
- I decided to check for a weak secret and found some juice.
	```bash
	flask-unsign --unsign --cookie 'eyJyb2xlIjoic3RhbmRhcmQiLCJ1aWQiOiJ1XzVmY2MxZDg4IiwidXNlcm5hbWUiOiJtZW93In0.aeMEBQ.-ItCY9bz_76xMpBaMtO4_opLtro' --wordlist ~/opt/wordlists/rockyou.txt --no-literal-eval
	```
	- This actually worked and I found `Password1!` was being used as the secret.
- I can decode the data segment to see that it holds `{"role":"standard","uid":"u_2d49b981","username":"bbbbbb"}`
- From here I can forge a cookie with `role` set to `admin`.
	```
	flask-unsign --sign --cookie '{"role":"admin","uid":"u_5fcc1d88","username":"meow"}' --secret 'Password1!'
	```
- I plugged the cookie produced in the last step into the `session` cookie in the browser and reloaded the page.
	- Nothing
- I started manually enumerating some common routes and found `/admin` was available and displayed the flag.