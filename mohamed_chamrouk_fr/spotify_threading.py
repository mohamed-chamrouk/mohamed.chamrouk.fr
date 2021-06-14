import threading
import time
import mohamed_chamrouk_fr.startup as startup
from mohamed_chamrouk_fr import app

stop_threads = False


class spotify_thread(threading.Thread):
    def __init__(self, time, name):
        threading.Thread.__init__(self)
        self.time = time
        self.name = name

    def run(self):
        app.logger.info(f"Starting thread {self.name}")
        while True:
            time.sleep(600)
            global stop_threads
            if not stop_threads:
                startup.refreshToken(self.time)
                app.logger.info(f"{self.name} : Execution successful")
            else:
                app.logger.info(f"{self.name} : Execution is paused")
