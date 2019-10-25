import time
import queue
from pythonosc import osc_bundle
from pythonosc import osc_message
from pythonosc import osc_bundle_builder

class Receiver:
    def __init__(self):
        self.queue = queue.Queue()

    def get(self):
        try:
            return self.queue.get(block=False)
        except queue.Empty:
            return None

    # Parse a packet
    def process(data, sender):
        now = time.time()
        # TODO exception handling
        if osc_bundle.OscBundle.dgram_is_bundle(data):
            bundle = osc_bundle.OscBundle(data)
            self.process_bundle(bundle, now, sender)
            return True
        elif osc_message.OscMessage.dgram_is_message(data):
            msg = osc_message.OscMessage(data)
            queue.put(([msg], now, sender)])
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
                msgs.push(content)
            elif isinstance(content, osc_bundle.OscBundle):
                included_bundles.push(content)

        queue.put((msgs, now, sender))
        for bndl in included_bundles:
            self.process_bundle(bndl)
