#!/usr/bin/python3.8

import nfc
import ndef
from threading import Thread
from keystore import KeyStore
import sys
import logging
import argparse

LOG_LEVEL = logging.DEBUG

logging.basicConfig(stream=sys.stderr, level=LOG_LEVEL)
logger = logging.getLogger(__name__)
parser = argparse.ArgumentParser(description='Authenticate via nfc.')
parser.add_argument('--add-key', action='store_true')
parser.add_argument('--daemon', action='store_true')
args = parser.parse_args()
print(args)


def work_on_tag(tag):
    logger.debug('Tag found: ' + str(tag))

    keystore = KeyStore()
    logger.debug('Trying to fetch key from DB')
    # logger.debug(tag.dump())
    logger.debug(type(tag))
    key = keystore.get_key_from_db(tag.identifier)
    print(tag.__class__.__name__)

    if key is None and args.add_key and tag.__class__.__name__ == 'NTAG215':
        key = keystore.add_new_key(tag.identifier)
        secret = key[0]
        key = key[1]
        tag.write(6, secret[0:4])
        tag.write(7, secret[4:8])
        tag.write(8, secret[8:12])
        tag.write(9, secret[12:16])
        tag.protect(password=key.get_access_key(), read_protect=True, protect_from=4)
    else:
        if key is not None:
            print(tag.authenticate(key.access_key))
            print(key.validate(tag.read(6)))


clf = nfc.ContactlessFrontend('usb')

while args.daemon:
    clf.connect(rdwr={'on-connect': work_on_tag})

clf.connect(rdwr={'on-connect': work_on_tag})
