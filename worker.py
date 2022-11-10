# from termios import PARODD

import numba
import numpy as np
from numba.typed import List
from numba import njit
import time
from numba.core.errors import NumbaDeprecationWarning, NumbaPendingDeprecationWarning
import warnings

"""
This works with numba version '0.54.1'

Later version of numba won't work due to 
depreciation of the default list type.
"""


warnings.simplefilter("ignore", category=NumbaDeprecationWarning)
warnings.simplefilter("ignore", category=NumbaPendingDeprecationWarning)


class Clock_Worker:
    def __init__(self, data_queue, grain, exit_event, client_ender, plotting_queue):
        self.dirty_clock_list = []
        self.clean_clock_list = []
        # for i in range(100):
        #     self.dirty_clock_list.append(np.arange(400000))
        # for i in range(100):
        #     self.clean_clock_list.append(np.arange(340000))
        self.data_queue = data_queue
        self.total_length = 0
        self.grain = grain
        self.exit_event = exit_event
        self.client_ender = client_ender
        self.stop_idx = 0
        self.plotting_queue = plotting_queue
        self.process_idx = 0

    def append_array(self, array_set):
        # load in the just recieved data
        dirty_clock = array_set[0]
        clean_clock = array_set[1]
        self.dirty_clock_list.append(dirty_clock)
        self.clean_clock_list.append(clean_clock)
        self.total_length = self.total_length + len(array_set[0])

    def loop(self):
        while 1:
            self.stop_idx += 1
            if self.exit_event.is_set():
                print("[END] exiting worker")  # this sometimes works???
                self.client_ender.set()
                break

            array_set = self.data_queue.get()  # blocking
            self.append_array(array_set)
            # print("lenght of array set: ", len(self.dirty_clock_list))
            self.process_idx += 1
            print("length dirtyclock list: ", len(self.dirty_clock_list))
            if self.process_idx == 5:
                print("Processing")
                self.process()
                self.process_idx = 0
            # print(np.shape(array1))
            # print("start of array1: ", self.array1[0:5])
            # print("end of array1: ", self.array1[-5:])

            # print("middle of array: ", self.array1[1500:1505])
            # print("len of array1: ", len(self.array1))
            # print("dtype of array1: ", self.array1.dtype)

            if len(self.dirty_clock_list) > 2:
                self.dirty_clock_list.pop(0)
                self.clean_clock_list.pop(0)

            if self.stop_idx == 400:
                self.plotting_queue.put([self.array1, self.array2])
                self.client_ender.set()
                break

    @staticmethod
    @njit
    def fast_process(dirty_clock_list, clean_clock_list, grain):

        tl_clean = 0
        tl_dirty = 0
        for array in dirty_clock_list:
            tl_dirty = tl_dirty + len(array)

        for array in clean_clock_list:
            tl_clean = tl_clean + len(array)

        # you need to make sure 10x of ideal clock matches 10x of original
        # take the 1st 10a sets of dirtyclock and make an idea clock to match that.

        ideal_clock = np.linspace(
            dirty_clock_list[0][0], dirty_clock_list[-1][-1], int(tl_dirty / grain)
        )
        out_clean = np.zeros(len(ideal_clock))
        out_dirty = np.zeros(len(ideal_clock))

        if tl_clean != tl_dirty:
            print("########### Length error")
            return out_dirty, out_clean

        i = 0
        j = 0

        # print("lengh of ideal clock: ", len(ideal_clock))
        # print("total length of dirty array list: ", tl_dirty)
        # print("ideal clock at beginning: ", ideal_clock[0])
        # print("ideal clock at end: ", ideal_clock[-1])
        # print()
        # print("dirty clock at beginning: ", dirty_clock_list[0][0])
        # print("dirty clock at end: ", dirty_clock_list[-1][-1])

        for k, ideal in enumerate(ideal_clock):
            # print("lenght of out dirty: ", len(out_dirty))
            # print("length of current dirty list: ", len(dirty_clock_list[j]))
            # print("this is i: ", i)
            # if k == 32:
            #     print("special 32: ")
            #     print(dirty_clock_list[j][i])
            #     print(ideal)
            out_dirty[k] = dirty_clock_list[j][i] - ideal
            # out_dirty[k] = dirty_clock_list[j][i]
            out_clean[k] = clean_clock_list[j][i] - ideal
            # out_clean[k] = ideal
            i = i + grain
            # print(len(dirty_clock_list))
            # print(dirty_clock_list[j][i])
            if i >= len(dirty_clock_list[j]):
                i = i - len(dirty_clock_list[j])
                j = j + 1

            if j > len(dirty_clock_list):
                return out_dirty, out_clean
        # print(dirty_clock_list[-1][:20] - clean_clock_list[-1][:20])
        return out_dirty, out_clean

    def process(self):
        (self.array1, self.array2) = Clock_Worker.fast_process(
            self.dirty_clock_list, self.clean_clock_list, self.grain
        )


if __name__ == "__main__":

    worker = Clock_Worker(3, 10)

    worker.process()
    t1 = time.time()
    worker.loop()
    print("elapsed: ", time.time() - t1)
