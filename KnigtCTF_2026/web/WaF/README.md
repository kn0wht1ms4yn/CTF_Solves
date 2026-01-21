#### WaF
- points earned: 
#### Notes / Intuition
- The challenge description indicates that there is a file `/flag.txt` that contains the flag.
- There's a comment on the main landing page that shows insight into the backend web app.
	```html
	<!-- @app.after_request    
	    def index(filename: str = "index.html"):
	    if ".." in filename or "%" in filename:
	        return "No no not like that :("
	    
	    -->
	```
- This is a filter which prevents `..` and `%` in the file name.  So I won't just be able to `../../../flag.txt` and things like double url encoding are out of the picture.
- My guess is that the app is doing something like
	```python
	send_file(f'views/{filename}', as_attachment=True)
	```
- I tried some standard stuff without much luck.  One thing was `%2fflag.txt` which would work if the filename was going through `path.join()` but no joy.
- I noticed the line below from the main landing page.  Curious about `a="{a}"` I tried navigating to `/{index.html}` and this worked to render the `index.html` page.
	```html
	<input a="{a}" type="text" required>
	```
- This indicates that the `{` and `}` characters are being parsed.  To be honest, I'd like to see the code because I'm not quite sure what's happening here.  Is this python code parsing out things between `{` and `}` or does it have to do with some bash shell expansion or something?
- Knowing about this weird behavior I wondered if I can do something like `/{.}/index.html`.  Sure enough this works to server the `index.html` page.
- From here it's pretty easy to imagine that I can probably traverse directories with `/{.}{.}/{.}{.}/` which does work as expected.
#### Solution
```http
GET /{.}{.}/{.}{.}/flag.txt HTTP/1.1
```