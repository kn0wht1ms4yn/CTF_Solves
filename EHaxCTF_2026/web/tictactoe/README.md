#### tictactoe
- points earned: 141
#### Where's the flag?
- No source was provided so this is unknown.
#### Notes / Intuition
- The app is a tic tac toe game.
- During gameplay, requests containing the data below are sent to the backend
	```json
	{"mode":"3x3","state":[[1,0,0],[0,0,0],[0,0,0]]}
	```
- a sample response looks like this
	```json
	{
	    "message": "AI: I’ve simulated this 3x3 grid 10^6 times. You don't win in any of them.",
	    "ai_move": 4
	}
	```
- The first thing I tried to do was just to submit a winning match, for example,
	```json
	{"mode":"3x3","state":[[1,1,1],[-1,0,0],[0,-1,-1]]}
	```
- The app did not like this and responded with
	```json
	{
	    "message": "AI: Access denied... You’re playing by my rules. That was your first mistake.",
	    "ai_move": 6,
	    "gameOver": true
	}
	```
- Then I tried playing with the dimensions just to see what would happen.
```json
{"mode":"4x4","state":[[0,0,0],[0,0,0],[0,0,0]]}
```
- The app responded with
```json
{
    "message": "4x4_MODE_ACTIVE: AI sensors blind in ghost sectors."
}
```
- In that test I changed the dimensions in `mode`  but not in `state`.  So next I tried sending a state that matches the 4x4 dimensions with a win condition
	```json
	{"mode":"4x4","state":[[0,0,0,1],[0,0,0,1],[0,0,0,1],[0,0,0,1]]}
	```
- And this was successful.

#### Solution
- Send a POST request to `/api` with the json data below
	```json
	{"mode":"4x4","state":[[0,0,0,1],[0,0,0,1],[0,0,0,1],[0,0,0,1]]}
```
