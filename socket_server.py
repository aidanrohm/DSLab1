# -*- coding:utf-8 -*-

import socket
import threading

ip_port = ('127.0.0.1', 9999)

sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket.SOCK_STREAM is tcp
#sk = socket.socket()
sk.bind(ip_port)
# tcp has to use a listener
sk.listen(5)
print('start socket server，waiting client...')

clients = {}
histories = {}
client_id_count = 1
lock = threading.Lock()

def handle_client(conn, client_id):
    conn.sendall(f"Your ID is {client_id}".encode())
    while True:
        try: 
            data = conn.recv(1024).decode().strip()
            
            if not data:
                continue

            if data == "list":
                with lock:
                    ids = "Active clients: " + ", ".join(map(str, clients.keys()))
                conn.sendall(ids.encode())

            elif data.startswith("forward"):
                parts = data.split(" ", 2)

                if len(parts) < 3:
                    conn.sendall("Usage: Forward ID message".encode())
                    continue
            
                target_id, msg = parts[1], parts[2]
                target_id = int(target_id)

                with lock:
                    if target_id in clients:
                        full_msg = f"{client_id}: {msg}"
                        clients[target_id].sendall(full_msg.encode())

                        # Saving the history
                        key = tuple(sorted((client_id, target_id)))
                        histories.setdefault(key, []).append(full_msg)
                        conn.sendall(f"Message forwarded to {target_id}".encode())
                
                    else: # Error Message
                        conn.sendall(f"Client {target_id} not found!".encode())

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

            elif data =="exit":
                conn.sendall("Goodbye!".encode())
                break

            else:
                conn.sendall("Sorry, unknown command...".encode())

        except ConnectionResetError:
            break

    with lock:
        del clients[client_id]

    conn.close()
    print(f"Client {client_id} disconntected!")

while True:
    conn, address = sk.accept()
    with lock:
        client_id = client_id_counter
        client_id_counter += 1
        clients[client_id] = conn

    print(f"Client {client_id} connected from {address}")
    threading.Thread(target=handle_client, args=(conn, client_id), daemon=True).start()
