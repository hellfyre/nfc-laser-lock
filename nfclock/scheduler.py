from sched import scheduler
from threading import Thread
from time import time, sleep


class Scheduler(Thread):

    def __init__(self, seconds, action):
        super().__init__()
        self.sched = scheduler(time, sleep)
        self.sched.enter(seconds, 1, action)

    def cancel(self):
        for event in self.sched.queue:
            self.sched.cancel(event)

    def run(self) -> None:
        while not self.sched.empty():
            self.sched.run(False)
            sleep(1)
