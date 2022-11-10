import sys
import selectors
import json
import io
import struct
from queue import Queue
import queue
import numpy as np
import os


class Message:
    def __init__(self, sock, addr, message_queue, data_queue):
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
        self._request_queued = False
        self._jsonheader_len = None
        self.jsonheader = None
        self.response = None
        self.request = None
        self.message_queue = message_queue
        self.data_queue = data_queue
        self.content_dict = {}

    # def _set_selector_events_mask(self, mode):
    #     """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
    #     if mode == "r":
    #         events = selectors.EVENT_READ
    #     elif mode == "w":
    #         events = selectors.EVENT_WRITE
    #     elif mode == "rw":
    #         events = selectors.EVENT_READ | selectors.EVENT_WRITE
    #     else:
    #         raise ValueError(f"Invalid events mask mode {repr(mode)}.")
    #     self.selector.modify(self.sock, events, data=self)

    def _read(self):
        try:
            # Should be ready to read
            data = self.sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")

    def write(self):
        if self._send_buffer:
            print("sending", repr(self._send_buffer), "to", self.addr)
            try:
                # Should be ready to write
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
            print("sent.")

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(io.BytesIO(json_bytes), encoding=encoding, newline="")
        obj = json.load(tiow)
        tiow.close()
        return obj

    def _create_message(self, *, content_bytes, content_type, content_encoding):
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": content_type,
            "content-encoding": content_encoding,
            "content-length": len(content_bytes),
        }
        jsonheader_bytes = self._json_encode(jsonheader, "utf-8")
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + content_bytes
        return message

    def _process_response_json_content(self):
        content = self.response
        result = content.get("result")
        print(f"got result: {result}")

    def _process_response_binary_content(self):

        array_list = self.jsonheader["array-list"]
        self.content_dict = {}
        content = self.response
        for item in array_list:
            array_name = item[0]
            array_length = item[1]
            # print()
            # print("array_name: ", array_name, " array_length: ", array_length)
            # print("length of content: ", len(content))
            # print("length of content[:array_length]: ", len(content[:array_length]))
            self.content_dict[array_name] = np.frombuffer(
                content[:array_length], dtype=np.float64
            )
            content = content[array_length:]

        # for key, value in self.content_dict.items():
        #     print(key, ": ", value[:20])

        # send to worker
        self.data_queue.put([self.content_dict["clocks"], self.content_dict["pclocks"]])

        # from here, I export the data to a processing thread

    def check_for_request(self):
        try:
            self.request = self.message_queue.get(block=False)
            self.queue_request()
        except queue.Empty:
            self.request = None

    def process_events(self):
        # print("len of send buffer: ", len(self._send_buffer))
        if len(self._send_buffer) != 0:
            # there exists a message to send to the peer
            self.write()
        else:
            # reading from peer is the default action
            self.read()

    def read(self):
        self._read()

        # print("json header len:", self._jsonheader_len)
        # print("json header: ", type(self.jsonheader))
        if self._jsonheader_len is None:
            self.process_protoheader()

        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonheader()

        if self.jsonheader:
            if self.response is None:
                self.process_response()

    def close(self):
        print("closing connection to", self.addr)
        try:
            self.sock.close()
        except OSError as e:
            print(
                "error: socket.close() exception for",
                f"{self.addr}: {repr(e)}",
            )
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None

    def queue_request(self):
        content = self.request["content"]
        content_type = self.request["type"]
        content_encoding = self.request["encoding"]
        if content_type == "text/json":
            req = {
                "content_bytes": self._json_encode(content, content_encoding),
                "content_type": content_type,
                "content_encoding": content_encoding,
            }
        else:
            req = {
                "content_bytes": content,
                "content_type": content_type,
                "content_encoding": content_encoding,
            }
        message = self._create_message(**req)
        self._send_buffer += message
        self._request_queued = True

    def process_protoheader(self):
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack(">H", self._recv_buffer[:hdrlen])[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]

    def process_jsonheader(self):
        hdrlen = self._jsonheader_len
        if len(self._recv_buffer) >= hdrlen:
            self.jsonheader = self._json_decode(self._recv_buffer[:hdrlen], "utf-8")
            self._recv_buffer = self._recv_buffer[hdrlen:]
            for reqhdr in (
                "byteorder",
                "content-length",
                "content-type",
                "content-encoding",
                "array-list",
            ):
                if reqhdr not in self.jsonheader:
                    raise ValueError(f'Missing required header "{reqhdr}".')

    def process_response(self):
        content_len = self.jsonheader["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]
        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            self.response = self._json_decode(data, encoding)
            print("received response", repr(self.response), "from", self.addr)
            self._process_response_json_content()
        else:
            # Binary or unknown content-type
            self.response = data
            self._process_response_binary_content()
            self.reset_message()  # only reset after the full message has been decoded

    def reset_message(self):
        self._jsonheader_len = None
        self.jsonheader = None
        self.response = None

        # Close when response has been processed
        # self.close()
