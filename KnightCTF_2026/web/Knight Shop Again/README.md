#### Knight Shop Again
- points earned: 100
#### Notes / Intuition
- After creating an account, I logged in and took a look at the src to try and get an understanding for what might be going on in this app.  Looks like a react app.
- While scrolling through `main.<>.js` my eyes were drawn toward the following block of code.
	```js
	e.jsx)("button", {
		onClick: async () => {
			d("");
			const e = await fetch("/api/checkout", {
				method: "POST",
				headers: {
					"Content-Type": "application/json"
				},
				body: JSON.stringify({
					discountCode: u > 0 ? o : "",
					discountCount: u
				})
			})
			  , r = await e.json();
			e.ok ? (n(c(c({}, t), {}, {
				balance: r.balance
			})),
			l([]),
			s(0),
			r.flag ? d("\ud83c\udf89 Purchase successful! Your flag: ".concat(r.flag)) : d("\u2705 Purchase successful!"),
			setTimeout( () => p("/orders"), 2e3)) : d("\u274c ".concat(r.error))
		}
		,
		className: "btn-primary btn-large",
		children: "Checkout"
	})]
	```
- It looks like when the user checks out, a flag may be returned as part of the response.
- I started investigating the check out mechanism.  Added an item to the cart and navigated to the checkout form. I noticed there's a way to apply a coupon.
- I tried submitting a random coupon and got an error 'Invalid Coupon Code'.  However, the a key point that I noticed here was that no request was ever sent to the backend.  So the logic for handling the coupon was on the frontend.  It is likely that this mechanism can be broken.
- I searched the source for `coupon` and found `applyCoupon` which led me to `processTransaction` which led me to a function named `_0x1a8c`.
	```js
	function _0x1a8c(input) {
	  const base = [75, 78, 73, 71, 72, 84];
	  const suffix = [50, 53];
	  
	  if (!input || input.length < 5) return { valid: false };
	  
	  const prefix = input.substring(0, 6);
	  const ending = input.substring(6);
	  
	  let match = true;
	  for (let i = 0; i < 6; i++) {
	    if (prefix.charCodeAt(i) !== base[i]) {
	      match = false;
	      break;
	    }
	  }
	  
	  if (match && ending.length === 2) {
	    if (ending.charCodeAt(0) === suffix[0] && ending.charCodeAt(1) === suffix[1]) {
	      const cookieName = 'promo_applied';
	      const existingCookie = document.cookie.split(';').find(c => c.trim().startsWith(cookieName + '='));
	      
	      if (existingCookie) {
	        return { valid: false };
	      }
	      
	      document.cookie = cookieName + '=1; path=/';
	      return { valid: true, code: input };
	    }
	  }
	  
	  return { valid: false };
	}
	```
- The basic gist is that if a coupon code is submitted that is `KNIGHT25` then the value of the cart is reduced by 25%.  Once complete a cookie, `promo_applied` is stored in the browser to indicate that a coupon had been used.  This is the mechanism used to prevent multiple coupons from being used.  So a user can just delete the cookie and resubmit the coupon again to get another 25% discount.
- It's worth noting here that, since I had been mostly looking around in the code, I hadn't yet noticed that there was an existing user balance on the account.
- My theory was that perhaps I can apply enough coupons where the total balance evaluates to `$0.00`
- I applied the coupon a few times and hit the `Checkout` button and to my suprise, I saw the flag.  It was at this point I noticed that there was an existing balance that I was supposed to be targeting.
- Taking a look at the actual request to `/api/checkout` showed an easier solution. 
- `/api/checkout` takes a `discountCode` and a `discountCount` and then calculates the total based on those values.  If a user provides the correct `discountCode` and a high enough `discountCount` to bring the total below the account balance, then the transaction will go through and the flag is returned.

#### Solution
```http
POST /api/checkout HTTP/1.1
Host: 23.239.26.112:8087
Content-Type: application/json
Cookie: connect.sid=s%3A7-vIPcTwaKy1-kfek1E3s3URmBLqOmLq.Pml8IjVfJLvth7xeQE84JLPK5JtDVE3HG7xGCCLOgi0; promo_applied=1

{"discountCode":"KNIGHT25","discountCount":4}
```