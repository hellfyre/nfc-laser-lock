from ..keystore import KeyStore
from ..scheduler import Scheduler
from .tagHandler import TagHandler


class AuthenticateHandler(TagHandler):
    def __init__(self, database_file, pin):
        self.database_file = database_file
        self.pin = pin
        self.current_event = None

    def handle_tag(self, tag):
        if tag.__class__.__name__ != 'NTAG215':
            print(f'Wrong tag type ({tag.__class__.__name__})')
            return

        print('Authenticating key')
        keystore = KeyStore(self.database_file)
        key = keystore.get_key_from_db(tag.identifier)

        if key is None:
            print('No key found for tag')
            return

        if tag.authenticate(key.access_key) and key.validate(tag.read(6)):
            print('Switching on pin')
            self.pin.on()
            if self.pin.is_active:
                print('Renewing scheduler')
                if self.current_event:
                    self.current_event.cancel()
            self.current_event = Scheduler(10, self.pin.off)
            self.current_event.start()
