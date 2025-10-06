#### Puzzle
- points earned: 302

#### Create account with editor role
- Although a role is not included in the request when a user signs up, it can be included.
- The role can either be `1` for editor or `2` for user.
```http
POST /confirm-register HTTP/1.1
Host: puzzle-c4d26ae9.p1.securinets.tn
Content-Length: 347
User-Agent: meow
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryHSDoK8KxAUkbMjdg

------WebKitFormBoundaryHSDoK8KxAUkbMjdg
Content-Disposition: form-data; name="username"

mrMeow
------WebKitFormBoundaryHSDoK8KxAUkbMjdg
Content-Disposition: form-data; name="role"

1
------WebKitFormBoundaryHSDoK8KxAUkbMjdg
Content-Disposition: form-data; name="email"

a
------WebKitFormBoundaryHSDoK8KxAUkbMjdg
Content-Disposition: form-data; name="phone_number"

1231231233
------WebKitFormBoundaryHSDoK8KxAUkbMjdg--
```
- This is required because admin users can access the `/users/<uuid>` which reveals the password for the account that `uuid` belongs to.

#### Article creator can accept a collaboration request.
- If a user creates an article with a collaboration, they should have to wait for the collaborator to accept.
- However, the acceptance can be forced by sending a post request to `/collab/accept/<articleUuid>`
- The article UUID can be obtained within the DOM collaboration request.

#### Admin password leak
- since we have an account with the editor role we can access `/users/<uuid>`. So all we need is the `uuid` for the `admin` user and we can get their password.
- To do so, we first must create an article with `admin` as a collaborator.
- Via the above weakness we can accept that collaboration request.
- Once accepted, the article will appear in our user's `Your stories` area.
- Click on `Read Article` to access the article.
- The collaborator's uuid will be within the DOM of this page.
- Then we can go to `/users/<uuid>` to reveal the admin password `Adm1nooooX333!123!!%`.

#### Credentials Exposed in `dbConnect.exe` & flag
- Once we have the admin password we can log into their account.
- With admin privs we can access the endpoint `/data`
- `/data` has 2 files that can be downloaded. `secrets.zip` and `dbconnect.exe`.
- `secrets.zip` is a password protected archive.
- If we use the linux `strings` command on `dbconnect.exe` we can scroll through and see a set of db credentials.
```
database = 'puzzledb'
username = 'sa'
password = 'PUZZLE+7011_X207+!*'
```
- This password can be used to unzip `secrets.txt` which contains a single file `data.txt`
- and `data.txt` contains the flag.