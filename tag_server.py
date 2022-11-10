import matplotlib.pyplot as plt
import TimeTagger
import numpy as np
import numba
import math
from time import sleep
from CustomPLLHistogram import CustomPLLHistogram
import matplotlib.pyplot as plt
import traceback
import signal

from queue import Queue
import queue
import socket
import threading
import pickle

import libserver
import os


HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"


clients = set()
thread_lock = threading.Lock()
shutdown_flag = threading.Event()
data_queues = []
message_queues = []
threads = []


class Tagger:
    def __init__(self, out_queues, in_queues):
        print("Initializing Tagger...")
        self.tagger = TimeTagger.createTimeTagger()
        self.out_queues = out_queues
        self.in_queues = in_queues
        self.data = {}
        self.settings_request = None

    def run_tagger(
        self,
    ):
        while 1:
            try:
                # pull data from measurment
                clocks, pclocks, hist = self.PLL.getData()
                self.data["clocks"] = clocks
                self.data["pclocks"] = pclocks
                self.data["hist"] = hist

                # distribute data to clients
                self.data_to_clients()

                # check for new setting from clients
                self.check_settings()

            except:
                print("Caught Exception. ################")
                traceback.print_exc()
                self.PLL.stop()
                break

            if shutdown_flag.is_set():
                print("Shutting down tagger ########")
                self.PLL.stop()
                break

    def data_to_clients(self):
        # send data diccionary to client queues
        for client_queue in self.out_queues:
            client_queue.put(self.data)

    def startPLL(self, data_channel, clock_channel):
        self.data_channel = data_channel
        self.clock_channel = clock_channel
        self.tagger.setEventDivider(9, 100)
        self.tagger.setTriggerLevel(-5, -0.014)
        self.tagger.setTriggerLevel(9, 0.05)
        # I should be pulling these settings from a local diccionary...
        self.PLL = CustomPLLHistogram(
            self.tagger,
            self.data_channel,
            self.clock_channel,
            mult=50000,  # clock multiplier
            phase=0,
            deriv=40,
            prop=2e-12,
            n_bins=800000,
        )

    def settings_from_clients(self):
        for client_queue in self.in_queues:
            try:
                self.settings_request = client_queue.get(block=False)
            except queue.Empty:
                pass

    def check_settings(self):
        self.settings_from_clients()
        if self.settings_request:
            print("GOT SETTINGS: ")
            print(self.settings_request)  # prob a diccionary
            self.settings_request = None
        # TODO
        # parse the response and enact settings.


def handle_client(client, addr, data_queue, message_queue):
    with thread_lock:
        clients.add(client)

    message = libserver.Message(client, addr, data_queue, message_queue)

    while True:
        try:
            # sleep(.005)
            data = (
                data_queue.get()
            )  # this is blocking, so I'm won't move it into the message class

            # for key, value in data.items():
            #     print(key, ": ", value[:20])
            message.load_data(data)
            message.process_events()

        except ConnectionResetError:
            # traceback.print_exc()
            # print("Client Closed. ")
            clients.remove(client)
            message.close()
            break

        except:
            traceback.print_exc()
            clients.remove(client)
            message.close()
            break

        if shutdown_flag.is_set():
            print("Shutting down clients ########")
            break


data_channel = -5
clock_channel = 9
tagger = Tagger(data_queues, message_queues)
tagger.startPLL(data_channel, clock_channel)


# old_clock = 0

# queues starts as an empty array, but grows with each new client.
data_handler = threading.Thread(target=tagger.run_tagger)
data_handler.start()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind(ADDR)
    except:
        print("binding error")
        os._exit(1)

    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")

    while True:
        try:
            client, addr = server.accept()  # blocking
            client.setblocking(
                False
            )  # don't hang wainting for reads. Main purpose of server is to send timetaggs
            print("Connected by: ", addr)
            with thread_lock:
                data_queue = Queue()
                data_queues.append(data_queue)  # used by Tagger thread
                message_queue = Queue()
                message_queues.append(message_queue)  # used by Tagger thread
            thread = threading.Thread(
                target=handle_client, args=(client, addr, data_queue, message_queue)
            )
            threads.append(thread)
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 2}")
        except:
            traceback.print_exc()
            print("Shutting down socket ########")
            server.shutdown(socket.SHUT_RDWR)
            server.close()
            break

shutdown_flag.set()

# here I have all the queues and stuff in the global namespace.
# with that, every time a new client connects, the main thread goes through the while loop

# right now, tagger is in the main thread namespace
# but PLL gets instantiated in the main thread...

# TODO
# - get a timetagger settings_change function working, with messages from client.

# class Tagger would wrap the timetagger class, and I'd include new functions like

# right now handle_data does not have unqiue controll of the timetagger class.

# right now I have a callback function for timetagger controll. It would work if the timetagger is in the global namespace.
# if not...
# timetagge class could check_all_clients() for messages from their respective queues.
# if any valid messages come in, the class runs the message.
# the Tagger class will have a loop that the thread manages. -->

# I should find a way for a thread that manages the timetagger to:
#       1. Most of the time, handle data
#       2. Some of the time, get messages from the peers. With a nice way of figuring out which peer sent the message.

# WHen using classes with threads, there are 2 methods.
# 1. inherit from Thread()
# 2. Pass a method from an existing object to a thread
# I will use this.
