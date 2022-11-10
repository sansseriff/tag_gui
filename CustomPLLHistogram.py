import matplotlib.pyplot as plt
import TimeTagger
import numpy as np
import numba
import math
from time import sleep


class CustomPLLHistogram(TimeTagger.CustomMeasurement):
    """
    Example for a single start - multiple stop measurement.
        The class shows how to access the raw time-tag stream.
    """

    def __init__(
        self,
        tagger,
        data_channel,
        clock_channel,
        mult=1,
        phase=0,
        deriv=0.01,
        prop=2e-9,
        n_bins=2000000,
    ):
        TimeTagger.CustomMeasurement.__init__(self, tagger)
        self.data_channel = data_channel
        self.clock_channel = clock_channel
        self.mult = mult
        self.phase = phase
        self.deriv = deriv
        self.prop = prop
        self.clock0 = 0
        self.period = 1  # 12227788.110837
        self.phi_old = 0
        self.init = 1
        self.max_bins = n_bins
        self.clock_idx = 0
        self.hist_idx = 0
        self.error = 0
        self.old_clock_start = 0
        self.old_clock = 0

        # I want to return one or two numpy arrays. But I don't know how long to make them, because they scale with the
        # number of clocks that come in

        # you can initialize them to something... like 1000 and see if they get full.

        # The method register_channel(channel) activates
        # that data from the respective channels is transferred
        # from the Time Tagger to the PC.
        self.register_channel(channel=data_channel)
        self.register_channel(channel=clock_channel)

        # click becomes data
        # start becomes clock

        self.clear_impl()

        # At the end of a CustomMeasurement construction,
        # we must indicate that we have finished.
        self.finalize_init()

    def __del__(self):
        # The measurement must be stopped before deconstruction to avoid
        # concurrent process() calls.
        self.stop()

    def getData(self):
        # Acquire a lock this instance to guarantee that process() is not running in parallel
        # This ensures to return a consistent data.

        # self._lock()

        # if self.clock_data[0] == self.old_clock:
        #     print("yes")
        # else:
        #     print("############")
        # clocks = self.clock_data[:self.clock_idx].copy()
        # pclocks = self.lclock_data[:self.clock_idx].copy()
        # hist_tags = self.hist_tags_data[:self.clock_idx].copy()
        # if len(clocks) > 0:
        #     self.old_clock = clocks[0]
        # self._unlock()
        # # return clocks[:self.clock_idx], pclocks[:self.clock_idx], hist_tags[:self.hist_idx]
        # return clocks, pclocks, hist_tags
        clocks = np.zeros(50)
        pclocks = np.zeros(50)
        hist_tags = np.zeros(50)
        while 1:
            sleep(0.005)
            self._lock()
            if self.clock_idx == 0:
                self._unlock()
                continue
            if (self.old_clock_start != self.clock_data[0]) | (
                self.old_clock_start == 0
            ):
                clocks = self.clock_data[: self.clock_idx].copy()
                pclocks = self.lclock_data[: self.clock_idx].copy()
                hist_tags = self.hist_tags_data[: self.clock_idx].copy()
                self.old_clock_start = self.clock_data[0]
                self._unlock()
                return clocks, pclocks, hist_tags
            # else:
            #     print("nope")
            self._unlock()

    # def getIndex(self):
    #     # This method does not depend on the internal state, so there is no
    #     # need for a lock.
    #     arr = np.arange(0, self.max_bins) * self.binwidth
    #     return arr

    def clear_impl(self):
        # The lock is already acquired within the backend.
        self.last_start_timestamp = 0
        # self.data = np.zeros((self.max_bins,), dtype=np.uint64)

        self.clock_data = np.zeros((self.max_bins,), dtype=np.float64)
        self.lclock_data = np.zeros((self.max_bins,), dtype=np.float64)
        self.hist_tags_data = np.zeros((self.max_bins,), dtype=np.float64)

    def on_start(self):
        # The lock is already acquired within the backend.
        pass

    def on_stop(self):
        # The lock is already acquired within the backend.
        pass

    # I should support the measurment of the unfiltered clock with respect to the phase locked clock.

    @staticmethod
    @numba.jit(nopython=True, nogil=True)
    def fast_process(
        tags,
        clock_data,
        lclock_data,
        hist_tags_data,
        data_channel,
        clock_channel,
        init,
        clock0,
        period,
        phi_old,
        deriv,
        prop,
        phase,
        mult,
    ):

        """
        A precompiled version of the histogram algorithm for better performance
        nopython=True: Only a subset of the python syntax is supported.
                       Avoid everything but primitives and numpy arrays.
                       All slow operation will yield an exception
        nogil=True:    This method will release the global interpreter lock. So
                       this method can run in parallel with other python code
        """
        error = 0
        freq = 1 / period
        if init:
            # need a rough estimate of the period and frequency to start.
            # print("initializing")
            clock_idx = 0
            clock_portion = np.zeros(1000, dtype=np.uint64)
            # print("tag 20: ", tags[20])
            # print("tag 20 time: ", tags[20]['time'])
            for clock_idx, tag in enumerate(tags[:1000]):
                if tag["channel"] == clock_channel:
                    clock_portion[clock_idx] = tag["time"]
                    clock_idx += 1

            # Initial Estimates
            clock_portion = clock_portion[clock_portion > 0]  # cut off extra zeros
            # print(clock_portion[:100])
            # print(clock_portion[-100:])
            period = (clock_portion[-1] - clock_portion[0]) / (len(clock_portion) - 1)
            # print("clock start: ", clock_portion[0])
            # print("clock end: ", clock_portion[-1])
            freq = 1 / period
            # print("inter-period: ", period/1e12)
            # print("frequency of clocks: ", 1e12/period)
            init = 0
            clock0 = -1
            print("[READY] Finished FastProcess Initialization")

        clock_idx = 0  # overwrite the arrays
        hist_idx = 0

        # print("starting lock with period: ", period)
        # print("clock0: ", clock0)
        for i, tag in enumerate(tags):
            if tag["channel"] == clock_channel:
                current_clock = tag["time"]
                clock_data[clock_idx] = current_clock
                if clock0 == -1:
                    clock0 = current_clock - period
                arg = ((current_clock - (clock0 + period)) / period) * 2 * math.pi
                # print("arg: ", arg)
                phi0 = math.sin(arg)
                filterr = phi0 + (phi0 - phi_old) * deriv
                # print("filterr: ", filterr)
                # print("freq is: ", freq, " and filterr is: ", filterr, " and prop is: ", prop)
                freq = freq - filterr * prop

                # this will handle missed clocks
                cycles = round((current_clock - clock0) / period)

                clock0 = clock0 + cycles * (1 / freq)  # add one (or more) periods
                lclock_data[clock_idx] = clock0
                period = 1 / freq
                phi_old = phi0
                clock_idx += 1

            if tag["channel"] == data_channel:
                if clock0 != -1:
                    hist_tag = tag["time"] - clock0
                    sub_period = period / mult
                    minor_cycles = (hist_tag + phase) // sub_period
                    hist_tag = hist_tag - (sub_period * minor_cycles)
                    # if hist_tag > 10:
                    #     hist_tag = 10
                    # if hist_tag < 0:
                    #     hist_tag = 3
                    hist_tags_data[hist_idx] = hist_tag
                    hist_idx += 1
                else:
                    continue
            # print("period inside: ", period)
            # if period <= 0:
            #     error = 1
            #     break
            # print(f"clock0: {clock0}, period: {period}, tag['channel']: {tag['channel']}, phi0: {phi0}, clock0 - currentClock: {clock0 - current_clock}")

        # print("finishing with period: ", period)
        # print("clock0: ", clock0)
        # print("clock0: ", clock0, " period: ", period, " tag[channel] ", tag['channel'], "clock0 - currentClock: ", clock0 - current_clock, "clock_idx: ", clock_idx)
        # print(clock_idx)
        # sleep(.01)
        return clock0, period, phi_old, init, clock_idx, hist_idx, error

    def process(self, incoming_tags, begin_time, end_time):
        """
        Main processing method for the incoming raw time-tags.

        The lock is already acquired within the backend.
        self.data is provided as reference, so it must not be accessed
        anywhere else without locking the mutex.

        Parameters
        ----------
        incoming_tags
            The incoming raw time tag stream provided as a read-only reference.
            The storage will be deallocated after this call, so you must not store a reference to
            this object. Make a copy instead.
            Please note that the time tag stream of all channels is passed to the process method,
            not only the onces from register_channel(...).
        begin_time
            Begin timestamp of the of the current data block.
        end_time
            End timestamp of the of the current data block.
        """
        # maybe the jit function could change the memory location of that returned ints? So you need to pass them?
        # but numpy arrays are just pointers, and the class already has those. No need to pass them back.
        (
            self.clock0,
            self.period,
            self.phi_old,
            self.init,
            self.clock_idx,
            self.hist_idx,
            self.error,
        ) = CustomPLLHistogram.fast_process(
            incoming_tags,
            self.clock_data,
            self.lclock_data,
            self.hist_tags_data,
            self.data_channel,
            self.clock_channel,
            self.init,
            self.clock0,
            self.period,
            self.phi_old,
            self.deriv,
            self.prop,
            self.phase,
            self.mult,
        )


# Channel definitions
CHAN_START = 1
CHAN_STOP = 2

if __name__ == "__main__":

    print(
        """Custom Measurement example

Implementation of a custom single start, multiple stop measurement, histogramming
the time differences of the two input channels.

The custom implementation will be comparted to a the build-in Histogram class,
which is a multiple start, multiple stop measurement. But for the
selected time span of the histogram, multiple start does not make a difference.
"""
    )
    # fig, ax = plt.subplots()

    tagger = TimeTagger.createTimeTagger()
    data_channel = -5
    clock_channel = 9
    tagger.setEventDivider(9, 100)
    tagger.setTriggerLevel(-5, -0.014)
    tagger.setTriggerLevel(9, 0.05)
    PLL = CustomPLLHistogram(
        tagger,
        data_channel,
        clock_channel,
        10,
        phase=0,
        deriv=0.001,
        prop=2e-10,
        n_bins=800000,
    )
    # for i in range(40000):
    #     sleep(.05)
    #     clocks, pclocks, hist = PLL.getData()
    #     # print("1: ", clks1[:10])
    #     # print("HIST: ", hist[:20])
    #     print("length of clocks: ", len(clocks))
    #     diff = clocks - pclocks
    #     print("difference: ", diff[:10])
    for i in range(40000):
        sleep(0.05)
        clocks, pclocks, hist = PLL.getData()

    clocks, pclocks, hist = PLL.getData()

    basis = np.linspace(clocks[0], clocks[-1], len(clocks))
