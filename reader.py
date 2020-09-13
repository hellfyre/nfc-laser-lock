import nfc
import logging
from threading import Thread
from time import sleep


class Reader(Thread):
    def __init__(self):
        super().__init__()
        self.log = logging.getLogger('Reader')
        self.connect_handler = None
        self.release_handler = None
        self.stopped = False

        try:
            self.clf = nfc.ContactlessFrontend('usb')
        except IOError:
            raise

    def register_connect_handler(self, handler):
        self.connect_handler = handler

    def register_release_handler(self, handler):
        self.release_handler = handler

    def tag_connected(self, tag):
        if self.connect_handler:
            self.connect_handler(tag)

    def tag_released(self, tag):
        if self.release_handler:
            self.release_handler(tag)

    def stop(self):
        self.stopped = True

    def run(self):
        while not self.stopped:
            self.log.info('Entering new reader cycle')
            self.clf.connect(rdwr={'on-connect': self.tag_connected, 'on-release': self.tag_released})
            sleep(5)
