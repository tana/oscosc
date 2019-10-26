import time
import receiver

if __name__ == '__main__':
    recv = receiver.Receiver()
    recv.start_thread(12345)
    try:
        while True:
            while recv.available():
                msgs = recv.get()
                print(msgs)
            time.sleep(1 / 60)
    finally:
        recv.stop_thread()
