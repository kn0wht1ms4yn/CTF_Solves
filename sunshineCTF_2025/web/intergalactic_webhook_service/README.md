#### Intergalactic Web Hook
- points earned: 10

#### Notes
- since the source code is provided we know that the flag is located in a response from a POST request to `http://127.0.0.1:5001/flag`
- Looking at source for `/trigger` I see the code below which sends a post request to the address specified by a webhook as long as it passes checks in `is_ip_allowed(url)`.
    ```python
    url = registered_webhooks.get(webhook_id)
    if not url:
        return jsonify({'error': 'Webhook not found'}), 404
    allowed, reason = is_ip_allowed(url)
    if not allowed:
        return jsonify({'error': reason}), 400
    try:
        resp = requests.post(url, timeout=5, allow_redirects=False)
    ```
- `/register` uses the same `is_ip_allowed(url)` logic to check urls when they are registered
- Reviewing the code for `is_ip_allowed` I can see that it will return true as long as the provided URL does not resolve to a local ip.
    ```python
    def is_ip_allowed(url):
        parsed = urlparse(url)
        host = parsed.hostname or ''
        try:
            ip = socket.gethostbyname(host)
        except Exception:
            return False, f'Could not resolve host'
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_reserved:
            return False, f'IP "{ip}" not allowed'
        return True, None
    ```
- Since the overall logic goes through the process of
    1. check to see if URL resolves to local IP
    2. goto that URL
- ... it is starting to feel like a TOCTOA and I'm wondering if DNS rebinding works.
- further testing on local showed that this would work.

#### Solution
- I used `https://lock.cmpxchg8b.com/rebinder.html` to help with the DNS redbind attack.
    - this service takes 2 IPs and gives you an FQDN
    - when a request is sent to that FQDN then it has a 50% chance of resolving to one of the 2 provided requests.
    - In my case I used `127.0.0.1` and another non-local IP.
- It took a few tries to register the FQDN within the app through `/register`
- It also took a few tries on `/trigger` to get the app to properly send a response to `http://127.0.0.1:5001/flag`
- When it works as expected the flag is returned in the response.