from .handler.addHandler import AddHandler
from .handler.authenticateHandler import AuthenticateHandler
from .keystore import KeyStore
from .reader import Reader
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

args.database_file = os.path.abspath(args.database_file)
databaseFilePath = os.path.dirname(args.database_file)
os.makedirs(databaseFilePath, exist_ok=True)


def main():
    args.command = args.command[0]
    if args.command == 'auth':
        print("Entering authentication mode...")
        reader = Reader()
        reader.register_connect_handler(AuthenticateHandler(args.database_file, pin))

        reader.start()
    elif args.command == 'list':
        keystore = KeyStore(args.database_file)
        print('+------+----------------------+------------------+---------+')
        print('| ID   | Owner                | Identifier       | Enabled |')
        print('+------+----------------------+------------------+---------+')
        for key in keystore.get_key_list():
            print("| {0: >4d} | {1: <20s} | {2} | {3}     |".format(key['id'],
                                                                    key['owner'],
                                                                    key['identifier'],
                                                                    'Yes' if key['enabled'] else 'No '
                                                                    ))
        print('+------+----------------------+------------------+---------+')
    elif args.command == 'add':
        if not args.owner:
            print("To add a key, set --owner.")
            sys.exit(1)
        reader = Reader(True)
        reader.register_connect_handler(AddHandler(args.database_file, args.owner))

        reader.start()
    elif args.command == 'enable' or args.command == 'disable':
        if not args.id and not args.owner:
            print("To {} a key, set either --id or --owner".format(args.command))
            sys.exit(1)
        id_or_owner = int(args.id) if args.id else args.owner
        keystore = KeyStore(args.database_file)
        keystore.set_enabled(id_or_owner, True if args.command == 'enable' else False)
    elif args.command == 'remove':
        if not args.id and not args.owner:
            print("To remove a key, set either --id or --owner.")
            sys.exit(1)
        id_or_owner = int(args.id) if args.id else args.owner
        keystore = KeyStore(args.database_file)
        keystore.remove(id_or_owner)
