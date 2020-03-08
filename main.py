import nfc
from .keystore import KeyStore
import sys
import logging
import argparse
from gpiozero import OutputDevice
from sched import scheduler as Scheduler
from time import time, sleep

LOG_LEVEL = logging.DEBUG

logging.basicConfig(stream=sys.stderr, level=LOG_LEVEL)
logger = logging.getLogger(__name__)
parser = argparse.ArgumentParser(description='Authenticate via nfc.')
parser.add_argument('--add-key', action='store_true')
parser.add_argument('--daemon', action='store_true')
parser.add_argument('--pin')
args = parser.parse_args()
print(args)

pin = OutputDevice(args.pin)
scheduler = Scheduler(time, sleep)
currentEvent = None

def tag_connected(tag):
    global currentEvent
    logger.debug('Tag found: ' + str(tag))

    keystore = KeyStore()
    logger.debug('Trying to fetch key from DB')
    # logger.debug(tag.dump())
    logger.debug(type(tag))
    key = keystore.get_key_from_db(tag.identifier)
    print(tag.__class__.__name__)

    if key is None or tag.__class__.__name__ != 'NTAG215':
        return

    if args.add_key:
        key = keystore.add_new_key(tag.identifier)
        secret = key[0]
        key = key[1]
        tag.write(6, secret[0:4])
        tag.write(7, secret[4:8])
        tag.write(8, secret[8:12])
        tag.write(9, secret[12:16])
        tag.protect(password=key.get_access_key(), read_protect=True, protect_from=4)
    else:
        if tag.authenticate(key.access_key) and key.validate(tag.read(6)):
            if pin.is_active():
                pin.off()
                if currentEvent:
                    scheduler.cancel(currentEvent)
            else:
                pin.on()
                currentEvent = scheduler.enter(7200, 1, pin.off)

def tag_released(tag):
    global currentEvent
    if currentEvent:
        scheduler.cancel(currentEvent)

    currentEvent = scheduler.enter(10, 1, pin.off)


def main():
    try:
        clf = nfc.ContactlessFrontend('usb')
    except IOError as ioe:
        exit("Could not find NFC reader: {}".format(ioe))

    while args.daemon:
        clf.connect(rdwr={'on-connect': tag_connected, 'on-release': tag_released})

    clf.connect(rdwr={'on-connect': tag_connected})
