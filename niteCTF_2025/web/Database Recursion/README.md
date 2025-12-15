#### Database Recursion
- points earned: 50

#### Notes
- The initial auth form is vulnerable to sql injection which allows auth bypass.  Here's how I discovered this:
	- Doing standard testing I tried username `admin` and password `' or 1=1-- -` which returned an error `Citadel SysSec: Input rejected by security filter`.
		- This tells me that there is some validation on the user input that checking for potentially malicious characters or strings.
		- I tested further to try and verify exactly what characters/strings the validator doesn't like.  I tried sending requests with username `admin` and different passwords like `'`, `1=1`, `or`, `--`.  I was able to determine that, in this case, the input validation doesn't like the word `or` and the comment chars `--`.  This indicates that the backend db is probably something like `MySQL` or `SQLite`.
		- I then continued checking for standard sql auth bypasses:
			- username `admin` password `'||'a'='a`
				- This request was not blocked by validation but it also did not let me bypass auth.
				- This made me think.  Something like this would work if the query that I'm injecting into is something like `select username, password from users where username='' and password='';`.  Perhaps somehow there's multiple entries returned and it fails because of that?
			- username `admin` password `' union select 'a','b`
				- This request was not blocked by validation but still not letting me bypass auth
			- username `admin` password `' union select 1,'a','b`
				- This worked! And the response provided a session cookie and a redirect to `/search`
				- The reason I tried this is because it is common for an app to do a query like `select * from users where username=''` and receive back an `id`,`username`, and `passwordHash`.  Then the app will hash the password provided by the user and compare against what was retrieved from the db.  This is not the case here as I was allowed to bypass auth.  If it did not bypass auth, I would have explored this option more.
- The `/search` page is an `Employee Directory` that provides a way to search the directory for a name.  There's also an `Admin Passcode` form that looks like it's a way to auth as an admin.  So it would appear that this is the goal.  Here's how I progressed:
	- I tried a basic bypass in the `Admin Passcode` form by using `' or 1=1-- -`.  This returned an error `Invalid Passcode`.  No message from any input validation.
	- I then tried some standard testing by doing an employee search for `'` and received an error response `SQL error: unrecognized token: "''' ORDER BY id LIMIT 4"`.
		- Part of the sql query is in this message and its telling me that there can only be a max of 4 results returned from this query.
	- At this point I noticed a hint on the main landing page for `/search`.  The first entry contains a note saying `I heard Kiwi from Management has the passcode`.
		- Now I'm wondering, 'Is there a user with the name Kiwi' who has the passcode in their note?.
	- I search just for the user `Kiwi` and I see 4 results, none of them contain the password in the note section.  However, since I know that the query is limited to 4 results, I am curious whether there are more entries for `Kiwi`.
	- The next search I do is for `Kiwi' and id>13 and 'a'='a`.
		- And this works! I see a single result for user `Kiwi` with a passcode in their note.
		- On the initial search for just `Kiwi` I saw ids `10`, `11`, `12`, and `13` so this is why the query if `id>13`
		- Other tries before this returned errors from the backend validation proving that the same mechanism is in place and this is why I included `and '1'='1`.
- Submitting the `Admin Passcode` form with the retrieved passcode redirects to `/admin`.  I was hoping to immediately see a flag here, but no joy, there is more work to be done.  The `admin` page with a form that looks like it allows queries on the `reports` table.  Here's how I progressed:
	- The bottom of this page contains a section `Metadata Directory` that looks like it is just listing valid table names in the DB.  One of them is `REDACTED` which is very curious.  My goal now is to figure out what the name of that table is.
	- I do a report query with just `'` and get an error `SQL error: unrecognized token: "'''"` so I know there is sql injection here.
	- I do a report query with `Q1` and check the results.  I do another query for `Q1'-- -` and get the same results.
		- This tells me that the query string I'm injecting into is something like `select id,quater,note,revenue from reports where quarter=''`
		- it's also telling me that the validation mechanism that has caused issues so far is no longer at play.
	- I do a report query like `' union select 1,2,3,4-- -` and get a single result where the fields are `1`, `2`, `3`, and `4`.
		- This shows that my suspicions on the query string are likely correct.
	- I do a query like `meow' union select 1,sqlite_version(),3,4-- -` and see the value `3.46.1` in the `Quarter` column.
		- this confirms that the backend db is `sqLite`.
	- I do a query `meow' union select 1,sql,3,4 from sqlite_master-- -` which returns 6 results, 1 for each table in the db.
		- One of those tables is named `CITADEL_ARCHIVE_2077` with a single column `secrets`.  Highly suspicious.
	- The final query is `' union select 1,secrets,3,4 from CITADEL_ARCHIVE_2077-- -` which returns the flag

#### Solution
- Bypass authentication with any username and password `' union select 1,'a','b`
- Locate the admin passcode in Kiwi's notes with `Kiwi' and id>13 and 'a'='a`
- Use the passcode to get to the admin panel
- Learn the name of the `REDACTED` table with 'meow' union select 1,sql,3,4 from sqlite_master-- -'
- Get the flag with `x' union select 1,secrets,3,4 from CITADEL_ARCHIVE_2077-- -`