#### Lunar File Invasion
- points earned: 463 

#### Notes
- The first thing to note is that the title screams LFI. So I'm focusing my search for vulnerabilities on LFI.
- Checking `robots.txt` which has been a theme for this CTF yields the following.
    ```
    Disallow: /.gitignore_test
    Disallow: /login
    Disallow: /admin/dashboard
    Disallow: /2FA
    ```
- Going to `/.gitignore_test` gives me a file with the following.
    ```
    # this tells the git CLI to ignore these files so they're not pushed to the repos by mistake.
    # this is because Muhammad noticed there were temporary files being stored on the disk when being edited
    # something about EMACs.

    # From MUHAMMAD: please make sure to name this .gitignore or it will not work !!!!

    # static files are stored in the /static directory.
    /index/static/login.html~
    /index/static/index.html~
    /index/static/error.html~
    ```
- I tried each one of the locations but only got a result for `/index/static/login.html~` which looks like a development copy of `login.html` and leaked credentials that can be used to login to the app.
    ```html
    <input value="admin@lunarfiles.muhammadali" type="text" name="email">
    <input value="jEJ&(32)DMC<!*###" type="text" name="password">
    ```
- After logging in I get sent to `/2FA` which is a two factor authentication.
- I also observed that, after loggin in, the response contained a `Set-Cookie` so before attempting to figure out the 2fa, I just tried navigating to `/admin/dashboard` which worked to allow me to bypass the 2fa authentication.
- Looking around there are a lot of hints and I eventually ended up clicking through `Manage Files` and `View` on one of the files.
- Watching the requests I see an interesting request for one of the file, `GET /admin/download/secret3.txt`, that I wanted to play with some more.
- There was quite a bit of trial and error here
    - Using `/admin/download//secret3.txt` had an interesting response because it was a redirect to `http://127.0.0.1:25307/admin/download/secret3.txt`.  This hinted at the idea that something was checking my input after `/admin/download/`.
    - Using `/admin/download/./secret1.txt` worked to provide the expected response.
    - Using `/admin/download/../../etc/passwd` returned a response indicating that the file does not exist BUT using `/admin/download/../../../etc/passwd` returned a `400 Bad Request`.  Not sure what to make of this but interesting and worth noting.
    - ULR encoding the same `../../` and `../../../` requests gave the same responses as above.
    - After more trial and error, I started to think about the first bullet point here and if server A is url decoding and passing to server B which might also be url decoding.
    - So I started to play with double url encoding and found that using something like `%252E%252Fsecret1%252Etxt` (souble url encoded `./secret1.txt`) provided the file.  Since this works, then it must mean the stack of servers is properly decoding a double url encoded path.
    - After much more trial and error of standard LFI techniques I eventuall landed on something that worked.  Alternating `./` and `../` was able to get me `/etc/passwd`.
        ```
        %252E%252F%252E%252E%252F%252E%252F%252E%252E%252F%252E%252F%252E%252E%252F%252E%252F%252E%252E%252F%252E%252F%252E%252E%252F%252E%252F%252E%252E%252F%252E%252F%252E%252E%252F%252E%252F%252E%252E%252F%252E%252F%252E%252E%252F%252E%252F%252E%252E%252Fetc%252Fpasswd
        ```
- At this point I have confirmed LFI works by leaking `/etc/passwd` by travering paths with `./../` and double url encoding.
- And there was also some more trial and error as I could not find the flag in standard CTF-style locations like `/flag.txt`
- Eventually I ended up looking for `app.py` by traversing 1 level of directories, then 2 levels, and so on.
- Awesomely I was successfully able to find `app.py` by traversing 3 levels of directories.
- inside the code was a reference to `flag.txt`.  It didn't actually do anything with it BUT it did tell me exactly where it lives.
```python
with open("./FLAG/flag.txt", "r") as f:
    FLAG = f.read()
```
- Now knowing the location of `flag.txt` i was able to reveal the flag and solve the challenge.


#### Solution
- `./.././.././../FLAG/flag.txt`
```http
GET /admin/download/%252E%252F%252E%252E%252F%252E%252F%252E%252E%252F%252E%252F%252E%252E%252FFLAG/flag.txt HTTP/1.1
```