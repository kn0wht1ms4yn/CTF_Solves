#### Schrodinger's Sandbox
- points earned: 50

#### Where's the flag?
- This was an interesting challenge where you provide the app some python code.
- The app executes the code on 2 separate hosts.
- If the output of the code will be returned IF the output on hostA is the same as the output on hostB.
#### Solution
- The theory I was trying to use was to use the app as an oracle.
- However, in the process of working this theory, I found the flag in env vars.
- code
	```python
	import os
	print(f'{os.environ}')
	```
- output
	```python
	environ({'PATH': '/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'HOSTNAME': '0bdd8f5b596b', 'CHALLENGE_ID': '155', 'TEAM_ID': '548', 'USER_ID': '1177', 'LANG': 'C.UTF-8', 'GPG_KEY': 'A035C8C19219BA821ECEA86B64E628F8D684696D', 'PYTHON_VERSION': '3.11.14', 'PYTHON_SHA256': '8d3ed8ec5c88c1c95f5e558612a725450d2452813ddad5e58fdb1a53b1209b78', 'FLAG_REAL': '0xfun{schr0d1ng3r_c4t_l34ks_thr0ugh_t1m3}', 'FLAG_FAKE': '0xfun{qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq}', 'HOME': '/home/sandbox', 'WERKZEUG_SERVER_FD': '3', 'PYTHONDONTWRITEBYTECODE': '1'})
	```
