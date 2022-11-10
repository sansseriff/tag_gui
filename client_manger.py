import socket
from queue import Queue
import threading
import pickle
import libclient
import signal
import time

from worker import Clock_Worker
import matplotlib.pyplot as plt
import numpy as np

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

thread_lock = threading.Lock()
exit_event = threading.Event()
client_ender = threading.Event()
plotting_queue = Queue()

peers = set()
message_queues = (
    []
)  # message queues are for directing commands like setting changes from the client to the timetagger(s)
data_queues = (
    []
)  # data queues are for moving data from peer-handling threads to data-processing threads
threads = []


def handle_peer(peer, addr, _message_queue, _data_queue):

    message = libclient.Message(
        peer, addr, _message_queue, _data_queue
    )  # did I set up the queues yet?
    connected = True
    while connected:

        message.check_for_request()  # from _message_queue
        message.process_events()  # the main entry point to the message class
        # ouputs data objects to _data_queue

        if client_ender.is_set():
            message.close()
            break

    print("[END] exiting peer thread")


def add_peer(_ADDR):

    with thread_lock:
        message_queue = Queue()
        message_queues.append(message_queue)
        data_queue = Queue()
        data_queues.append(data_queue)
        clk_worker = Clock_Worker(
            data_queue, 1, exit_event, client_ender, plotting_queue
        )  # 10 is the coarse graining
        worker_handler = threading.Thread(target=clk_worker.loop)
    peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    peer.connect(ADDR)
    peer_handler = threading.Thread(
        target=handle_peer, args=(peer, _ADDR, message_queue, data_queue)
    )
    threads.append(peer_handler)
    peer_handler.start()
    worker_handler.start()
    print(f"[ACTIVE PEERS] {threading.activeCount() - 1}")


def create_request(action, value):
    if action == "search":
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action, value=value),
        )

    if action == "settings_change":
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action, value=value),
        )
    else:
        return dict(
            type="binary/custom-client-binary-type",
            encoding="binary",
            content=bytes(action + value, encoding="utf-8"),
        )


# def signal_handler(signum, frame):
#     exit_event.set()


# signal.signal(signal.SIGINT, signal_handler)


try:
    add_peer(ADDR)  # peer-handling thread starts running.
except ConnectionRefusedError:
    print("Connection Refused. Check if server is running. ")
    exit()


#  poor man's callback
# try:
ipt = None
# ipt = input("what is the message you want to send? ") #blocking


while 1:

    try:
        # ipt = input("what is the message you want to send? ")  # blocking
        ls = plotting_queue.get()  # blocking
        array1 = ls[0]
        array2 = ls[1]
        print("test")
        plt.plot(np.arange(len(array1)), array1, label="array1")
        plt.plot(np.arange(len(array1)), array2, label="array2")
        plt.legend()
        plt.show()

        # value = dict(trigger_level = ipt)
        # action = "settings_change"
        # create_request(action, value)
        # time.sleep(0.1)
        # if exit_event.is_set():
        #     time.sleep(0.1)

    except KeyboardInterrupt:
        exit_event.set()
        time.sleep(0.1)
        print("[END] exiting main thread")
        break
    else:
        value = dict(trigger_level=ipt)
        action = "settings_change"
        request = create_request(action, value)
        # just send to first peer for now.
        message_queues[0].put(request)
