#### Just Another Notes App
- points earned: 50
#### Notes
- This was a weird challenge in that it didn't follow the flow of a general 'Notes' challenge.  The solution that I arrived upon seemed too easy and I'm unsure if it was the intended solution.
- The flag is loaded into the app via an environment variable.  The flag will be served back as a cookie to a user who sends a request to `/admin` under the following conditions
	- the user is authenticated
	- the users account has `is_admin=True`
	- the users request does not already contain a cookie named `flag`
- A user can have their account promoted to `is_admin=True` with the following flow
	- an admin user creates an `InviteCode` by accessing `/admin/generate_invite`
	- As a result the admin user is then redirected to `/getToken` which:
		- Finds the most recently created, unused `InviteCode` and redirects to `/getToken?token=<InviteCode>`
		- The second time around `/getToken` queries for the `InviteCode`, confirms it is not expired or used, and then redirects to `/accept_invite?token=<InviteCode>`
		- I think the idea on `/accept_invite` is that the non-admin user would be provided with the `Invite Code`, then they navigate to `/accept_invite`, enter the code, and get the `is_admin=True` permission.
- One of the problems that I saw here was that `/getToken` was not an admin-only route.  Any user can navigate to this endpoint and get the last `InviteCode` that was created, if it exists.  Also, the invites codes are not specific to 1 user, so any user and use any other user's code.
	- This became my solution.  I'm not sure if I stole someone's `InviteCode` OR there was a bot setup to repeatedly create them.
	- I suspect that the correct solution might have been to create a note that gets viewed by an admin bot.  The note contains XSS that forces that admin bot to access `/generate_invite` to create the `InviteCode`
#### Solution
- Create an account / login
- Navigate to `/getToken` --redirects-to--> `/accept_invite` with valid token
- Click `Accept Invite`
- Go to `/admin`
- Check the cookies to get the flag ... ¯\\\_(ツ)\_/¯

#### Suspected Correct Solution
- Create a note, like below, that an admin bot checks to trigger the `/admin/generate_invite` endpoint.
```html
<script>
	fetch('/admin/generate_invite', { method: 'POST' });
</script>
```
- then follow the steps in the solution above