# -*- coding:utf-8 -*-
# Aidan Rohm CISC 5597 Lab 1 Assignment
# Oct 6, 2025

import socket
import threading
import sys

ip_port = ('10.128.0.2', 9999)  # server IP on node0

s = socket.socket()
s.connect(ip_port)

# Event to signal the main thread to stop when server says Goodbye
stop_event = threading.Event()

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

            if msg.strip() == "Goodbye!":
                print("\n[Server] Goodbye!")
                stop_event.set()  # Signal the main thread to exit
                break

            print("\n[Server] " + msg)
            print("Enter command: ", end="", flush=True)
        except:
            break

# Using a thread to listen for messages, this allows the client to immediately display a message
listener_thread = threading.Thread(target=listen_for_messages, args=(s,), daemon=True)
listener_thread.start()

# Main loop for sending commands
while not stop_event.is_set():
    try:
        # Standard user input to communicate over the connection
        inp = input("Enter command: ").strip()
        if not inp:
            continue
        s.sendall(inp.encode())

        # If user types exit manually, also set the stop_event to clean up
        if inp.lower() == "exit":
            stop_event.set()
            break

    except (KeyboardInterrupt, EOFError):
        print("\nExiting client...")
        s.sendall("exit".encode())
        stop_event.set()
        break

# Wait a short moment for the listener to print "Goodbye!" if it hasn't yet
listener_thread.join(timeout=0.5)

s.close()
