import threading
import time
import uwsgi
import mohamed_chamrouk_fr.startup as startup
from mohamed_chamrouk_fr import app



class spotify_thread(threading.Thread):
    def __init__(self, time, name):
        threading.Thread.__init__(self)
        self.time = time
        self.name = name

    def run(self):
        app.logger.info(f"Cache value of isRunning is now : {uwsgi.cache_get('isRunning')}")
        app.logger.info(f"Starting thread {self.name}")
        while True:
            if True: #uwsgi.cache_get('stop_threads').decode('utf-8') == 'False':
                app.logger.info("Refreshing the token")
                startup.refreshToken(self.time)
                app.logger.info(f"{self.name} : Execution successful")
            else:
                app.logger.info(f"{self.name} : Execution is paused")
            time.sleep(600)
