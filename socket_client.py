# -*- coding:utf-8 -*-

import socket

ip_port = ('127.0.0.1', 9999)

s = socket.socket()
s.connect(ip_port)

client_id = s.recv(1024).decode()
print(client_id)

while True:
    inp = input("Enter command: ").strip()
    if not inp:
        continue
    s.sendall(inp.encode())

    server_reply = s.recv(4096).decode()
    print(server_reply)

    if inp == "exit":
        break
s.close()
