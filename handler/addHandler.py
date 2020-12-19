from ..keystore import KeyStore
from .tagHandler import TagHandler


class AddHandler(TagHandler):
    def __init__(self, database_file, owner):
        self.database_file = database_file
        self.owner = owner

    def handle_tag(self, tag):
        if tag.__class__.__name__ != 'NTAG215':
            print(f'Wrong tag type ({tag.__class__.__name__})')
            return

        print('Adding key')
        keystore = KeyStore(self.database_file)
        (secret, key) = keystore.add_new_key(tag.identifier, self.owner)
        tag.write(6, secret[0:4])
        tag.write(7, secret[4:8])
        tag.write(8, secret[8:12])
        tag.write(9, secret[12:16])
        tag.protect(password=key.get_access_key(), read_protect=True, protect_from=4)
