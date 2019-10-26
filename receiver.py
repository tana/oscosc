import time
import queue
import socket
import threading
from pythonosc import osc_bundle
from pythonosc import osc_message
from pythonosc import osc_bundle_builder

class Receiver:
    def __init__(self):
        self.queue = queue.Queue()
        self.should_stop = False

    def start_thread(self, port):
        self.thr = threading.Thread(target=self.listen_udp, args=(port,))
        self.thr.start()

    def stop_thread(self):
        self.should_stop = True
        self.thr.join()

    def listen_udp(self, port):
        max_data_size = 1024
        with socket.socket(
                family=socket.AF_INET, type=socket.SOCK_DGRAM) as sock:
            sock.bind(('', port))
            # TODO timeout or something.
            # should_stop might be not effective
            while not self.should_stop:
                data, sender = sock.recvfrom(max_data_size)
                self.process(data, sender)
    
    def get(self):
        return self.queue.get(block=False)

    def available(self):
        return not self.queue.empty()

    # Parse a packet
    def process(self, data, sender):
        now = time.time()
        # TODO exception handling
        if osc_bundle.OscBundle.dgram_is_bundle(data):
            bundle = osc_bundle.OscBundle(data)
            self.process_bundle(bundle, now, sender)
            return True
        elif osc_message.OscMessage.dgram_is_message(data):
            msg = osc_message.OscMessage(data)
            self.queue.put(([msg], now, sender))
            return True
        else:
            return False

    def process_bundle(self, bundle, now, sender):
        if bundle.timestamp == osc_bundle_builder.IMMEDIATELY:
            timestamp = now
        else:
            timestamp = bundle.timestamp

        included_bundles = []
        msgs = []
        for content in bundle:
            if isinstance(content, osc_message.OscMessage):
                msgs.append(content)
            elif isinstance(content, osc_bundle.OscBundle):
                included_bundles.append(content)

        self.queue.put((msgs, now, sender))
        for bndl in included_bundles:
            self.process_bundle(bndl)
