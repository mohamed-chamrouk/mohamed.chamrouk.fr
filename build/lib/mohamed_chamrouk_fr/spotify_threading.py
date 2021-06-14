import threading
import mohamed_chamrouk_fr.startup as startup


class spotify_thread(threading.Thread):
    def __init__(self, time, name):
        threading.Thread.__init__(self)
        self.time = time
        self.name = name

    def run(self):
        while True:
            startup.refreshToken(self.time)


class spotify_stat_thread(threading.Thread):
    def __init__(self, time, name):
        threading.Thread.__init__(self)
        self.time = time
        self.name = name

    def run(self):
        while True:
            startup.refreshStat()
