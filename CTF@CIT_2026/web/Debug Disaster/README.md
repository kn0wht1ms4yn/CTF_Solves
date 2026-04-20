#### Debug Disaster
- points earned: 633
#### Where's the flag?
- There's no source code with this challenge so the flag location is unknown.
#### Solution
- The main page is extremely simple.
	- It contains the message `Welcome to Startup Portal` and that's it.
- Looking at the response headers I see `Server: Werkzeug/3.1.8 Python/3.11.15` so I know that we're working with a flask app.
- I do some manual enumeration of routes and find some points of interest:
	- `/console` returns `400 Bad Request` which I think is normal for a flask app where `debug=True` is set
	- `/admin` returns a standard flask exception page which 100% confirms `debug=True` is set
- At this point I'm thinking that perhaps I can somehow leak the information needed to calculate a console `PIN` and get access to a python console.
- I started clicking around on the exception to see if I can expose anything helpful and found:
	``` 
	def home(): 
		return "<h2>Welcome to Startup Portal</h2>"
	@app.route("/admin")
	def admin():
		raise Exception("Debug leak triggered: Dirbuster maybe in your future!")
	@app.route("/flg_bar")
	def env():
		return open(".env").read(), 200, {"Content-Type": "text/plain"}
	```
	- another route `/flg_bar`
- Navigating to `/flg_bar` on the target returns the contents of `.env` which contains the flag.
