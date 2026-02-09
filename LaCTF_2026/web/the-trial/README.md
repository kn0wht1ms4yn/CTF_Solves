#### the-trial
- points earned: 100
#### Solution
- No source was provided with this challenge.
- Going to the target url, I see page with some animation and the text below
	```
	Want the flag? Just fill in the sentence and we'll send it right over.
	I want the xxxx.
	```
- Looking at the source I see
```javascript
 submit.addEventListener("click", async () => {
	const req = await fetch("/getflag", {
		method: "POST",
		body: `word=${encodeURIComponent(disp.textContent)}`,
		headers: {
			"Content-Type": "application/x-www-form-urlencoded"
		}
	});
	msg.textContent = await req.text();
});
```
- Based on this I create the request below which sets the `word` parameter to the only logical thing that completes the sentence, `I want the xxxx`.
```http
POST /getflag HTTP/1.1
Host: the-trial.chall.lac.tf
Content-Type: application/x-www-form-urlencoded

word=flag
```
