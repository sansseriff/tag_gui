import numpy as np
import time
import redis
import struct


class ToRedis:
    def __init__(self, data_queue, redis_host="localhost", redis_port=6379):
        self.r = redis.Redis(host=redis_host, port=redis_port)
        self.data_queue = data_queue

    def run_loop(self, key):

        while 1:
            data = self.data_queue.get()
            h, w = data.shape
            shape = struct.pack(">II", h, w)
            encoded = shape + data.tobytes()

            # Store encoded data in Redis
            self.r.set(key, encoded)
            return
