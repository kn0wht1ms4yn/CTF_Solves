#### lactf-invoice-generator
- points earned: 101

#### Where's the flag?
- The flag is returned in the response body of a GET request to `/flag` on the flag app.
- It's important to note that this service runs on its own docker container as specified in the `docker-compose` file.

#### Notes / Intuition
- The app allows a user to enter a Customer Name, Item Description, Cost, and Date Purchased and then returns a PDF based on the information entered.
- The app uses puppeteer to generate the PDF.
	- It does this by inserting the input values mentioned above into a template which is then rendered bu puppeteer and exported as a PDF.
- There's no validation on the input, so injecting html into the Customer Name field, for example, will work as expected and gets rendered as HTML into the final PDF.
- So we can pretty much just use an iframe as the Customer Name and have the iframe source the flag services `/flag` route.
- A cool thing to note here is that since the name of the service, as specified by the `docker-compose` file is `flag`, then the name `flag` will resolve to the ip address of the container within the context of the docker network.
	```yaml
	  flag:
	    build: ./flag
	    networks:
	      - app-network
	```
	- For example `http://flag:8081/flag` will send a request to the flag service as expected.

#### Solution
- Complete all the fields in the Invoice Generator form making sure to include the XSS below in the Customer Name field
```html
<iframe src="http://flag:8081/flag"></iframe>
```
