import socket 
import threading
import pickle
import numpy as np
import time


HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"



# def handle_client(conn, addr):
#     print(f"[NEW CONNECTION] {addr} connected.")

#     connected = True
#     while connected:
#         msg_length = conn.recv(HEADER).decode(FORMAT)
#         if msg_length:
#             msg_length = int(msg_length)
#             msg = conn.recv(msg_length).decode(FORMAT)
#             if msg == DISCONNECT_MESSAGE:
#                 connected = False

#             print(f"[{addr}] {msg}")
#             conn.send("Msg received".encode(FORMAT))

#     conn.close()


def server_receive(conn):
    connected = True
    full_msg = b''
    new_msg = True
    # i = 0
    while connected:
        try:
            msg = conn.recv(4096)
            # print("message length: ", len(msg))
            # print("            full message length: ", len(full_msg))
            
            if len(msg):
                # print("*********")
                # print('new msg length: ', len(msg))
                if new_msg:
                    print(f"new msg length: {msg[:HEADER]}")
                    msglen = int(msg[:HEADER])
                    new_msg = False
                full_msg += msg

                if len(msg) != 4096:
                    print("full message: ", len(full_msg)-HEADER, "and msglen is: ", msglen)

                if len(full_msg)-HEADER == msglen:
                    d = pickle.loads(full_msg[HEADER:])
                    # print(d[:10], " shape: ", np.shape(d))
                    new_msg = True
                    full_msg = b''
                else: 
                    pass
                    # if longer, either the current set was corrupted (unlikely) or two messages got combined. 
                    
        except KeyboardInterrupt:
            print("Exiting")
            if connected:
                conn.close()
                connected = False
            break

    conn.close()
        

# def start():
#     server.listen()
#     print(f"[LISTENING] Server is listening on {SERVER}")
#     while True:
#         conn, addr = server.accept()
#         thread = threading.Thread(target=handle_client, args=(conn, addr))
#         thread.start()
#         print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn.connect(ADDR)

server_receive(conn)
