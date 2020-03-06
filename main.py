import nfc
import ndef
from threading import Thread
from keystore import KeyStore
import sys
import logging

LOG_LEVEL = logging.DEBUG

logging.basicConfig(stream=sys.stderr, level=LOG_LEVEL)
logger = logging.getLogger(__name__)


def work_on_tag(tag):
    logger.debug('Tag found: ' + str(tag))

    keystore = KeyStore()
    logger.debug('Trying to fetch key from DB')
    logger.debug(tag.dump())
    logger.debug(type(tag))
    key = keystore.get_key_from_db(tag.identifier)

    if key is None:
        key = keystore.add_new_key(tag.identifier)
        secret = key[0]
        key = key[1]
        tag.write(6, secret[0:4])
        tag.write(7, secret[4:8])
        tag.write(8, secret[8:12])
        tag.write(9, secret[12:16])
        tag.protect(password=key.get_access_key(), read_protect=True, protect_from=6)
    else:
        print(tag.authenticate(key.access_key))
        print(tag.read(6))
        print(key.validate(tag.read(6)))
        tag.protect(password=bytes(0), read_protect=False, protect_from=0)
        tag.format()

    # tag.format()


clf = nfc.ContactlessFrontend('usb')
clf.connect(rdwr={'on-connect': work_on_tag})



