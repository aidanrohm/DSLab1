# -*- coding:utf-8 -*-
import socket
import threading
import sys

ip_port = ('10.128.0.2', 9999)  # server IP on node0

s = socket.socket()
s.connect(ip_port)

# Get assigned ID from server
client_id = s.recv(1024).decode()
print(client_id)

# Background thread to listen for server messages
# This function was implemented after some trial and error regarding the receiving of messages
# Without using a thread for message reception, the user needed to enter a command or key
# in order for the message to be displayed
def listen_for_messages(sock):
    while True:
        try:
            msg = sock.recv(4096).decode()
            if not msg:
                break
            print("\n[Server] " + msg)
            print("Enter command: ", end="", flush=True)  # re-prompt
        except:
            break

# Using a thread to listen for messages, this allows the client to immediately display a message
threading.Thread(target=listen_for_messages, args=(s,), daemon=True).start()

# Main loop for sending commands
while True:
    try:
        # Standard user input to communicate over the connection
        inp = input("Enter command: ").strip()
        if not inp:
            continue
        s.sendall(inp.encode())

        if inp == "exit":
            break
    except (KeyboardInterrupt, EOFError):
        print("\nExiting client...")
        s.sendall("exit".encode())
        break

s.close()
