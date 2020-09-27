from .keystore import KeyStore
from .reader import Reader
from .scheduler import Scheduler
import sys
import logging
import argparse
from gpiozero import OutputDevice
import os

LOG_LEVEL = logging.DEBUG

logging.basicConfig(stream=sys.stderr, level=LOG_LEVEL)
logger = logging.getLogger(__name__)
parser = argparse.ArgumentParser(description='Authenticate via NFC', prog='nfclock')
parser.add_argument('command', nargs=1, choices=['auth', 'list', 'add', 'enable', 'disable', 'remove'], default='auth')
parser.add_argument('--database-file', default='/etc/nfclock/keystore.sqlite')
parser.add_argument('--pin', default="1")
parser.add_argument('--id')
parser.add_argument('--owner')
args = parser.parse_args()

pin = OutputDevice(args.pin)
currentEvent = None

args.database_file = os.path.abspath(args.database_file)
databaseFilePath = os.path.dirname(args.database_file)
os.makedirs(databaseFilePath, exist_ok=True)


def add_key(tag, owner):
    if tag.__class__.__name__ != 'NTAG215':
        logger.error(f'Wrong tag type ({tag.__class__.__name__})')
        return

    logger.info('Adding key')
    keystore = KeyStore(args.database_file)
    (secret, key) = keystore.add_new_key(tag.identifier, owner)
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


def tag_connected(tag):
    logger.debug('Tag found: ' + str(tag))

    logger.debug('Trying to fetch key from DB')
    logger.debug(type(tag))
    if tag.__class__.__name__ != 'NTAG215':
        logger.error(f'Wrong tag type ({tag.__class__.__name__})')
        return

    if args.add_key:
        owner = input('Please specify a descriptive name for the added tag: ')
        add_key(tag, owner)
    else:
        authenticate_key(tag)


def main():
    args.command = args.command[0]
    if args.command == 'auth':
        print("Entering authentication mode...")
        reader = Reader()
        reader.register_connect_handler(authenticate_key)

        reader.start()
    elif args.command == 'list':
        keystore = KeyStore(args.database_file)
        print('+------+----------------------+------------------+---------+')
        print('| ID   | Owner                | Identifier       | Enabled |')
        print('+------+----------------------+------------------+---------+')
        for key in keystore.get_key_list():
            print("| {0: >4d} | {1: <20s} | {2} | {3}     |".format(key['id'], key['owner'], key['identifier'], 'Yes' if key['enabled'] else 'No '))
        print('+------+----------------------+------------------+---------+')
    elif args.command == 'add':
        #TODO: add username input
        print("Adding key...")
        reader = Reader(True)
        reader.register_connect_handler(add_key)
    elif args.command == 'enable' or args.command == 'disable':
        if not args.id and not args.owner:
            print("To {} a key, set either its ID or its owner".format(args.command))
            sys.exit(1)
        id_or_owner = int(args.id) if args.id else args.owner
        keystore = KeyStore(args.database_file)
        keystore.set_enabled(id_or_owner, True if args.command == 'enable' else False)
    elif args.command == 'remove':
        if not args.id and not args.owner:
            print("To remove a key, set either its ID or its owner.")
            sys.exit(1)
        id_or_owner = int(args.id) if args.id else args.owner
        keystore = KeyStore(args.database_file)
        keystore.remove(id_or_owner)
