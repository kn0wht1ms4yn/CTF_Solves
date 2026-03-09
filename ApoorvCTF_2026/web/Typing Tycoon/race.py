import requests

host = 'http://chals1.apoorvctf.xyz:4001'

# start
r = requests.post(f'{host}/api/v1/race/start')
dat = r.json()
race_id = dat['race_id']
text = dat['text']
print(f'{race_id=}')
print(f'{text=}')


text = text.split(' ')
for word in text:
    # sync
    data = {
        "race_id": race_id,
        "word": word,
        "progress": 0,
        "wpm":0
    }
    r = requests.post(f'{host}/api/v1/race/sync', json=data)
    dat = r.json()
    print(f'{dat=}')
