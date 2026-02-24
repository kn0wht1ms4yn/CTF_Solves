#### My First Blog
- points earned: 112
#### Where's the flag?
- There was not source code for this challenge so the approach is just to go investigate and see where it gets me.
#### Notes / Intuition
- Images are used on each of the blog pages but the way they are sourced prompts me to check for arbitrary file read.
	- Blog 1, for example, has an image that is sourced from `/attachment?file=kidpix-blog-1.png` 
	- Based on this I tried some basic arbitrary file read and path traversal payloads without any luck.  Each of these responded with a 403 - Forbidden.
		- `/attachment?file=/flag.txt`
		- `/attachment?file=../../../../../../../../../flag.txt`
- There's an IDOR in the `/blog/<blogId>` route.
	- When you first look at the app there are links to 3 blog's, `blog 1`, `blog 2`, and `blog 4`
	- Clicking on `blog 1`, for example, brings you to `/blog/1`
	- This `/blog/N` pattern prompted me to check for IDOR and since 3 was missing on the main page I started there with a manual check.
- On `/blog/3` there is a PDF rendered.  Looking at the src code there is:
	```html
	<!-- i had to delete this bc it has my personal info on it :( -->
	<!-- for documents in the 'other' folder only people with the API key has access -->
	<object data="/attachment?file=resume.pdf&apiKey=cc7c7342d2ed198c38c08814cd754030" type="application/pdf" width="30%" height="600px">
	```
	- `/attachment?file=` is a new route that prompts me to check for arbitrary file read
	- Take note of the fact that `apiKey=cc7c7342d2ed198c38c08814cd754030` is used with this file.  This peaks curiosity on the original arbitrary file read vector and prompts me to try again including this key.
	- This worked and the flag was returned.

#### Solution
```http
GET /attachment?file=/flag.txt&apiKey=cc7c7342d2ed198c38c08814cd754030 HTTP/1.1
Host: 34.186.135.240:30000


```