#### narnes-and-bobles
- points earned: 106

#### Where's the flag?
- A string, `flag.txt`, exists in the `books.json` files.
- This file is sourced by `app.py` where each entry gets loaded into a `Map` called `booksLookup`.
- So the `flag` entry exists inside the `booksLookup` map and looks like:
```javascript
"2a16e349fb9045fa" => {
    "id": "2a16e349fb9045fa",
    "title": "Flag",
    "file": "flag.txt",
    "price": 1000000
  }
```
- The `flag.txt` file will be returned to the user as a pdf if that usr makes a full purchase of a book called `Flag`

#### Notes / Intuition
- Note: the solution that I found was unintended.
- One of the first things I noticed when going over the files was that, in `books.json`, the price for `The Part-Time Parliament` is quoted where all other prices are defined as integers.
- This prompted me to look at how the prices are being added together.
	```javascript
	const additionalSum = productsToAdd
		.filter((product) => !+product.is_sample)
		.map((product) => booksLookup.get(product.book_id).price ?? 99999999)
		.reduce((l, r) => l + r, 0);
	
	if (additionalSum + cartSum > balance) {
	    return res.json({ err: 'too poor, have you considered geting more money?' })
	  }
	```
	- This block is
		- iterating through the items in the cart and removing books that are not samples
		- getting the price of each book
		- and adding them together
	- Something interesting happens though when `The Part-Time Parliament` exists among those books.
	- For example if the cart contains `The Part-Time Parliament` and `Flag` then the math to create the total looks like `"10" + 1000000` which evaluates to a string `"101000000"`
- It's important to not here that, although you generally only add one item at a time via the UI, the `/car/add` route requires that you provide a `productsToAdd` array which can contain multiple items
- So tracing through the logic of the `/cart/add` route when adding `The Part-Time Parliament` followed by `Flag`
	- `additionalSum` evaluates to a string, `"0101000000"`
	- since its the first cart addition `cartSum` will be `null`, so `additionalSum + cartSum` evaluates to `"0101000000null"`
	- in nodeJS, something like `"meow" > 0` will evaluate to false.
		- This means that when we check if `additionalSum + cartSum > balance` it will evaluate to false, which tells the app that the user has enough money to make this purchase.
- Since validation to make sure that the user has enough funds to make the purchase ONLY happens in the `/cart/add` route the user can just continue to checkout to get the books.

#### Solution
- register a new user
- Send a request to add `The Part-Time Parliament` and `Flag` to the cart.
```http
POST /cart/add HTTP/1.1
Host: me:3000
Content-Length: 63
Cookie: session=019c44a9-6848-7000-b74d-88ea4a206d1d
Content-Type: application/json

{"products":[{"book_id":"a3e33c2505a19d18","is_sample":false},{"book_id":"2a16e349fb9045fa","is_sample":false}]}
```
- Then just checkout.  A zip will be downloaded containing the `flag.txt` file.