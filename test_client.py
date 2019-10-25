# Send some values through OSC
# (See https://github.com/attwad/python-osc )
import math
import time
from pythonosc import osc_bundle_builder
from pythonosc import osc_message_builder
from pythonosc import udp_client

def make_bundle(**kwargs):
    bb = osc_bundle_builder.OscBundleBuilder(
            timestamp=osc_bundle_builder.IMMEDIATELY)
    for key, value in kwargs.items():
        mb = osc_message_builder.OscMessageBuilder(
                address=f'/{key}')
        mb.add_arg(value)
        bb.add_content(mb.build())
    return bb.build()

if __name__ == '__main__':
    print('Ctrl-C to quit')
    client = udp_client.SimpleUDPClient('127.0.0.1', 12345)
    t = 0.0
    while True:
        x = math.cos(2 * math.pi * t)
        y = math.sin(2 * math.pi * t)
        #bundle = make_bundle(x=x, y=y)
        #client.send(bundle)
        client.send_message('/x', x)
        client.send_message('/y', y)
        time.sleep(0.1)
        t += 0.1
