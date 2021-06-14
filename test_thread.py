import threading
import time

stop_threads = False

class thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        i=0
        while True:
            i += 1
            time.sleep(1)
            print(f"booba : {i}")
            global stop_threads
            if stop_threads or i > 10:
                break

print(threading.enumerate())

th = thread()
th.start()

th1 = thread()
th1.start()

time.sleep(4)

stop_threads = True

time.sleep(4)
stop_threads = False
th.run()

