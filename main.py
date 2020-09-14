#!/usr/bin/python3.8

import nfc
from keystore import KeyStore
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

pin = OutputDevice(args.pin)
currentEvent = None

args.database_file = os.path.abspath(args.database_file)
databaseFilePath = os.path.dirname(args.database_file)
os.makedirs(databaseFilePath, exist_ok=True)


def add_key(tag):
    if tag.__class__.__name__ != 'NTAG215':
        logger.error(f'Wrong tag type ({tag.__class__.__name__})')
        return

    logger.info('Adding key')
    keystore = KeyStore(args.database_file)
    key = keystore.add_new_key(tag.identifier)
    secret = key[0]
    key = key[1]
    tag.write(6, secret[0:4])
    tag.write(7, secret[4:8])
    tag.write(8, secret[8:12])
    tag.write(9, secret[12:16])
    tag.protect(password=key.get_access_key(), read_protect=True, protect_from=4)


def authenticate_key(tag):
    global currentEvent, pin

    if tag.__class__.__name__ != 'NTAG215':
        logger.error(f'Wrong tag type ({tag.__class__.__name__})')
        return
    
    logger.info('Authenticating key')
    keystore = KeyStore(args.database_file)
    key = keystore.get_key_from_db(tag.identifier)

    if key is None:
        logger.error('No key found for tag')
        return

    if tag.authenticate(key.access_key) and key.validate(tag.read(6)):
        logger.info('Switching on pin')
        pin.on()
        if pin.is_active:
            logger.info('Renewing scheduler')
            if currentEvent:
                currentEvent.cancel()
        currentEvent = Scheduler(10, pin.off)
        currentEvent.start()

pin = OutputDevice(args.pin)
scheduler = Scheduler(time, sleep)
currentEvent = None


def work_on_tag(tag):
    global currentEvent
    logger.debug('Tag found: ' + str(tag))

    logger.debug('Trying to fetch key from DB')
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

    if args.add_key:
        add_key(tag)
    else:
        authenticate_key(tag)


def main():
    if args.add_key:
        reader = Reader(True)
        reader.register_connect_handler(add_key)
    else:
        reader = Reader()
        reader.register_connect_handler(authenticate_key)

    reader.start()
