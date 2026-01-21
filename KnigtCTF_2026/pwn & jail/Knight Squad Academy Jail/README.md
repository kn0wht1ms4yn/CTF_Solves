#### Knight Squad Academy Jail
- points earned: 
#### Notes / Intuition
- The first thing I wanted to try and do on this one was figure out what type of jail this is.
- I tried all sorts of inputs like `1`, `'a'`, `'meow'`, `1==1` which all seemed to respond as expected, no issues.
- `False` returned `False` which indicated that this could be a python jail based on the capital `F`.
- Trying things like `{}` and `[]` returned `error: node not allowed: Dict` and `error: node not allowed: List` which makes me pretty confident that this is a python jail.
- I tried a bunch of random things to see if I could learn anything else.
	- Standard things like `exec()` or `eval()` resulted in `error: unknown function`
	- I created a script to enumerate all python builtin functions like `any`, `all`, etc.  Most of them returned `error: name not allowed` with the exception of `exit` and `quit` which terminated the process.
- Thinking about the challenge description, `I don't like words but I love chars`, I decided to start enumerating single characters as names.
	- I tried all characters a-z and A-Z but got `name not allowed` on all of them
	- I then tried enumerating all characters as functions by calling a-z and A-Z like `A()`, `B()`, `C()`, etc and this is where I found some success.
- `L()` had the response:
	```
	28
	```
- `Q()` had the response:
	```
	error: Oracle.Q() missing 2 required positional arguments: 'i' and 'x'
	```
- `S()` had the response:
	```
	error: Oracle.S() missing 1 required positional argument: 'guess'
	```
- Playing with `Q()` I tried `Q('a','a')` and got the response `error: Q(i, x) expects ints`.
- Trying `Q(1,1)` gives me the response -1.
- Further playing with `Q()` showed that it responded with either `1`, `0`, or `-1`.  
- After some more playing around I began to wonder if `L()` was the length of the flag, `Q()` was a way to query characters in the flag, and `S()` was a way to check the flag value.
- Perhaps, in the definition `Q(i, x)`
	- `i` represents the character index in the flag string
	- and `x`  represents a character to test at that index
	- A response of `-1` would indicate that the character used for `x` was less than actual value.  `1` would indicate that it is greater than the actual value.  `0` would indicate a match.
- Since I know that the flag starts with `KCTF{` I can test this theory.
	- `K`, at position `0` in the flag, has the ascii value `75`
	- If I try `Q(0, 75)` then the response is `0`
	- `Q(0,74)` responds with `-1`
	- and `Q(0,76)` responds with `1`
	- So the theory seems to check out
- I tried this on the the other known characters `C`, `T` and `F` and everything checked out.
- So the solution is to basically test each character at each index until I get a response `0` which indicates a correct flag character.
- This becomes much easier when scripted.
#### Solution
- Use the `Q()` function to query all characters of the flag.
- A script for automating this has been included in the repo.