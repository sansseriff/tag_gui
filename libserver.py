from ast import excepthandler
import sys
import selectors
import json
import io
import struct
import numpy as np
import traceback

request_search = {
    "morpheus": "Follow the white rabbit. \U0001f430",
    "ring": "In the caves beneath the Misty Mountains. \U0001f48d",
    "\U0001f436": "\U0001f43e Playing ball! \U0001f3d0",
}


class Message:
    def __init__(self, sock, addr, data_queue, message_queue):
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
        self._jsonheader_len = None
        self.jsonheader = None
        self.request = None
        self.response_created = False
        self.data_queue = data_queue
        self.message_queue = message_queue
        self.array_list = []
        self.data = b""

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
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")

    def _write(self):
        if self._send_buffer:
            # print("sending", repr(self._send_buffer), "to", self.addr)
            try:
                sent = self.sock.send(self._send_buffer)
                # for some reason using sendall bricks the client...
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            except:
                traceback.print_exc()
            else:
                self._send_buffer = self._send_buffer[sent:]
                # Close when the buffer is drained. The response has been sent.
                if sent and not self._send_buffer:
                    self.reset_message()

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(io.BytesIO(json_bytes), encoding=encoding, newline="")
        obj = json.load(tiow)
        tiow.close()
        return obj

    def _create_message(
        self, *, content_bytes, content_type, content_encoding, array_list
    ):
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": content_type,
            "content-encoding": content_encoding,
            "content-length": len(content_bytes),
            "array-list": array_list,  # could have just used self.array_list (?)
        }
        jsonheader_bytes = self._json_encode(jsonheader, "utf-8")
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + content_bytes
        return message

    # def _create_response_json_content(self):
    #     action = self.request.get("action")
    #     if action == "search":
    #         query = self.request.get("value")
    #         answer = request_search.get(query) or f'No match for "{query}".'
    #         content = {"result": answer}
    #     else:
    #         content = {"result": f'Error: invalid action "{action}".'}
    #     content_encoding = "utf-8"
    #     response = {
    #         "content_bytes": self._json_encode(content, content_encoding),
    #         "content_type": "text/json",
    #         "content_encoding": content_encoding,
    #     }
    #     return response

    def _create_response_binary_content(self):
        # this makes a diccionary with references to some large datastructures (self.data)
        response = {
            "content_bytes": self.data,  # which should already be bytes from load_data
            "content_type": "packed numpy data",
            "content_encoding": "binary",
            "array_list": self.array_list,  # a list of numpy array lengths
        }
        return response

    def load_data(self, data_dict):
        # pack the data diccionary into a big block of bytes
        self.data = b""
        self.array_list = []
        for key, array in data_dict.items():
            # self.array_list goes in the json header and is used to upack the serialized numpy arrays
            block = array.tobytes()
            self.array_list.append([key, len(block)])
            self.data += block

            # array_list looks like this (the numbers are random)
            #   [ {"clocks": 28389},
            #   {"pclocks": 283439},
            #   {"hist": 4839}]

    def process_events(self):
        self.read()  # this should be a non-blocking socket
        self.write()
        self._jsonheader_len = None

    def read(self):
        self._read()
        # need to check if anything was read?
        # print("jsonheader_len: ", self._jsonheader_len)
        # print("json header: ", type(self.jsonheader))
        if self._jsonheader_len is None:
            self.process_protoheader()

        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonheader()
                # print("processing json header")

        if self.jsonheader:
            # if self.request is None:
            #     self.process_request()
            self.enact_jsonheader()
            # self.reset_message()

    def write(self):
        self.create_response()
        self._write()
        self.reset_message()

    def reset_message(self):
        self._jsonheader_len = None
        self.jsonheader = None
        self.response = None

    def close(self):
        print("closing connection to", self.addr)
        #     try:
        #         self.selector.unregister(self.sock)
        #     except Exception as e:
        #         print(
        #             "error: selector.unregister() exception for",
        #             f"{self.addr}: {repr(e)}",
        #         )

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

    def process_protoheader(self):
        hdrlen = 2
        # print("length of recieve buffer: ", len(self._recv_buffer))
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack(">H", self._recv_buffer[:hdrlen])[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]
            # print("header processed")
            # print(" HEADER LENGTH: ", self._jsonheader_len)

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
            ):
                if reqhdr not in self.jsonheader:
                    raise ValueError(f'Missing required header "{reqhdr}".')

    def enact_jsonheader(self):
        content_len = self.jsonheader["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]
        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            self.request = self._json_decode(data, encoding)
            print("received request", repr(self.request), "from", self.addr)
            print("Exporting Settings to Tagger")
            self.message_queue.put(self.request)
        else:
            # Binary or unknown content-type
            self.request = data
            print(
                f'received {self.jsonheader["content-type"]} request from',
                self.addr,
            )
            print("Unexpected ################")
        self._jsonheader_len = None  # reset for next message (?)

    # def reset_message(self):
    #     self._jsonheader_len = None
    #     self.jsonheader = None

    # Set selector to listen for write events, we're done reading.
    # self._set_selector_events_mask("w")

    def create_response(self):
        # if self.jsonheader["content-type"] == "text/json":
        #     response = self._create_response_json_content()

        # Binary or unknown content-type
        response = self._create_response_binary_content()
        message = self._create_message(**response)
        self.response_created = True
        self._send_buffer += message
