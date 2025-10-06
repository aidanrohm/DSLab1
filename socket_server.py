# -*- coding:utf-8 -*-
# Aidan Rohm CISC 5597 Lab 1 Assignment
# Oct 6, 2025

import socket
import threading

# Listening on the internal ip of node0 which will be used as the server itself
ip_port = ('10.128.0.2', 9999)

# Socket.SOCK_STREAM is tcp
sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sk.bind(ip_port)

sk.listen(5) # TCP has to use a listener
print('start socket server，waiting client...')

clients = {} # Used to map the client_id to the socket
histories = {} # Maps the id used to a history of messages
client_id_counter = 1 # Keeps track of the number of clients (for this case there are 2 clients)
lock = threading.Lock() # Used to synchronize access to shared data

def handle_client(conn, client_id):
    conn.sendall(f"Your ID is {client_id}".encode()) # Used to communicate to the client what their id number is
    while True:
        try:
            data = conn.recv(1024).decode().strip()

            if not data:
                continue

            # Used to handle the list command
            if data == "list":
                with lock:
                    ids = "Active clients: " + ", ".join(map(str, clients.keys())) # Listing all active clients
                conn.sendall(ids.encode())

            # Used to handle the forward command
            elif data.startswith("forward"):
                parts = data.split(" ", 2)

                if len(parts) < 3: # Checks the length of the user input
                    conn.sendall("Usage: Forward ID message".encode())
                    continue

                # Assigning the input as the target client and the actual message to forward
                target_id, msg = parts[1], parts[2]
                target_id = int(target_id)

                # A lock is used to secure the thread to sending the message
                with lock:
                    # Assuming the argument is valid, the client is forwarded the message
                    if target_id in clients:
                        full_msg = f"{client_id}: {msg}"
                        clients[target_id].sendall(full_msg.encode())

                        # Saving the history so that it can be accessed via the history command
                        key = tuple(sorted((client_id, target_id)))
                        histories.setdefault(key, []).append(full_msg)
                        conn.sendall(f"Message forwarded to {target_id}".encode())

                    else: # Error Message
                        conn.sendall(f"Client {target_id} not found!".encode())

            # Handling the history command
            elif data.startswith("history"):
                parts = data.split(" ", 1)
                if len(parts) < 2:
                    conn.sendall("Usage: history ID".encode())
                    continue
                target_id = int(parts[1])

                key = tuple(sorted((client_id, target_id)))
                with lock:
                    history = histories.get(key, [])
                if history:
                    conn.sendall("\n".join(history).encode())
                else:
                    conn.sendall("No history!".encode())

            # Handling the exit command
            elif data =="exit":
                conn.sendall("Goodbye!".encode())
                break

            # IF the user input is not one of the previously implemented commands...
            else:
                conn.sendall("Sorry, unknown command...".encode())

        # Error handling
        except ConnectionResetError:
            break

    # Cleans and deletes the connection after useage is over
    with lock:
        if client_id in clients:
            del clients[client_id]

    conn.close()
    print(f"Client {client_id} disconntected!")

# The main accept loop
while True:
    conn, address = sk.accept()
    with lock:
        client_id = client_id_counter
        client_id_counter += 1 # Increases the active client count, along with the subsequent id
        clients[client_id] = conn

    # Starts a new thread in order to handle the client
    print(f"Client {client_id} connected from {address}")
    threading.Thread(target=handle_client, args=(conn, client_id), daemon=True).start()
