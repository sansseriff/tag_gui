import numpy as np
import time
import redis
import struct


class FromRedis:
    def __init__(self, data_queue, redis_host="localhost", redis_port=6379):
        self.r = redis.Redis(host=redis_host, port=redis_port)
        self.data_queue = data_queue

    def return_data(self, key):
        encoded = self.r.get(key)
        h, w = struct.unpack(">II", encoded[:8])
        # Add slicing here, or else the array would differ from the original
        return np.frombuffer(encoded[8:]).reshape(h, w)
