import socket, time

# host = '35.227.38.232'
host = '127.0.0.1'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, 5000))

req = b'GET /fla'
s.send(req)

time.sleep(1)

req = [
    b'g.html HTTP/1.1',
    b'Host: ' + host.encode() + b':5000',
    b'Range: bytes=135-',
    b'Connection: close',
    b'',
    b''
]
req = b'\r\n'.join(req)
s.send(req)

dat = b''
while True:
    d = s.recv(1024)
    if not d:
        break
    dat += d
print(dat)