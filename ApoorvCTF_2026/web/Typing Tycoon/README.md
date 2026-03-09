#### Typing Tycoon
- points earned: 50
#### Where's the flag?
- There was no source code provided with this challenge so the flag location is unknown.
#### Notes / Intuition
- The app is just a typing race.
- When the user selects to start they are presented with a paragraph of words and a place to type the words in.
- Each time a word is type, it is sent to the backend with a POST in the following format
	```json
	{
		"race_id": "race_1773096968099109989_5557",
		"word": "by",
		"progress": 0.008333333333333333,
		"wpm":1
	}
	```
- As part of standard enumeration I wanted to see what happens when I make it to the end of the game.
	- I wrote up a short script to do this (included in this repo)
	- To my surprise, the flag was returned when the script completed.

#### Solution
- Utilize that included script to complete the game and get the flag.
