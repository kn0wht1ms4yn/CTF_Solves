#### blogler
- points earned: 10

#### Where's the flag?
- The flag is loaded into the docker container at `/flag`,
- There are no other references to the flag file in the src code.
- Based on this I'll be looking for an arbitrary file read or a command/code execution

#### Notes / Intuition
- the `/blog/<string:username>` contains the statement below which reads files on the target system
	```python
	mistune.html((blog_path / blog["name"]).read_text()
	```
- The app provides functionality to store a user blog config.
	- The config lives in the global `users` dict in the format
		```python
		{
			<username>: {
				'blogs': [ { 'name': <blog_filename>, 'title': <blog_title> } ],
				'user': { 'name': <username>, 'password': <password> }
			}
		}
		```
	- The config is accessed and saved via a GET or POST  to the `/config` route.
		- When the config is retrieved with the GET route, it is first converted from a dict into its YAML representation and then servered back to the user
			```python
			return yaml.dump(users[session["username"]]), 200
			```
		- When the config is saved the POST `/config` route calls `validate_conf` which converts the conf from YAML representation to a python dict and validates the input.
			```python
			conf = yaml.safe_load(uploaded_conf)
			```
		- `validate_conf` does the following:
			- Validates the input by checking types and making sure that `../` does not exist in any of the blog names.
			- Calls `display_name` to converts the user's name from `something_like_this` to `SomethingLikeThis`
- All of this seems pretty good, however there is a feature of YAML that the developer had not considered
- YAML Anchors and Aliases
	- Anchors and aliases are a feature of YAML that allows the user creating the YAML to reference part of the YAML object from another part. For example:
		```yaml
		thingA:
		- a: 1
		  b: 2
		thingB:
		  a: 1
		  b: 2
		```
	- translates to
		```python
		{
			'thingA': [{'a': 1, 'b': 2}],
			'thingB': {'a': 1, 'b': 2}
		}
		```
	- if the object in `thingA[0]` is the exact same as `thingB` then it can be represented with anchors and aliases like:
		```python
		thingA:
		- &ref
		  a: 1
		  b: 2
		thingB: *ref
		```
	- The key here is that after being processed by `PyYaml` `thingB` will actually be a reference to `thingA[0]`. This means that if a change is made to `thingA[0]` then the change will also be made to `thingB`
- This matters because if, inside the `users[<username>]` dict, if `user` is a reference to `blogs[0]` then when `display_name` alters the user's `name` it will end up altering the blog's `name` as well.
	- So although there is validation that prevents the blog's name from containing `../` or starting with `/` a blog name like `_/flag` will bypass this.
	- Why? The logic inside `display_name` splits a string on `_`, capitalizes the first letter of each item in the result, then concatenates all items.
		- `'_/flag'` becomes `['', '/flag']` after being split.
		- No changes happen after capitalization because you cannot capitalize `/`
		- and then results in `/flag` after being joined.
	- So now what then user access route `/blog/<username>` to access the blog, The file `/flag` will be used as the content of the blog entry.
#### Solution
- Create a new account
- Update the config with the following
```python
blogs:
- &ref
  name: _/flag
  password: a
  title: meow
user: *ref
```
- then view the user's blog
- flag will be in the blog content.
