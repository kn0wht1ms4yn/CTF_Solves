#### Lunar Auth
- points earned: 10

#### Solution
- `/robots.txt` shows `/admin`
- source code for `/admin` leaks credentials
```javascript
/*
TODO: implement proper encryption.
*/
const real_username = atob("YWxpbXVoYW1tYWRzZWN1cmVk");
const real_passwd   = atob("UzNjdXI0X1BAJCR3MFJEIQ==");
```
- these are base64 encoded
```
username: alimuhammadsecured
password: S3cur4_P@$$w0RD!
```
- flag is revealed once logged in