import os
import bcrypt


class KeyData:
    identifier: int = None
    access_key: bytes = None
    secret: bytes = None
    save_secret: str = None

    def __init__(self, identifier, access_key, secret, save_secret=None):
        self.identifier = identifier
        self.access_key = access_key
        self.secret = secret
        self.save_secret = save_secret
        if self.secret is not None and self.save_secret is not None:
            if not self.validate():
                raise Exception('Secret validation failed')

    @staticmethod
    def generate_new(identifier) -> list:
        secret = os.urandom(16)
        key = os.urandom(16)
        new_key = KeyData(identifier, key, secret)
        new_key.generate_save_secret()
        return [new_key, secret]

    def get_save_secret(self):
        return self.save_secret

    def get_identifier(self):
        return self.identifier

    def set_secret(self, secret):
        self.secret = secret

    def get_access_key(self):
        return self.access_key

    def generate_save_secret(self):
        self.save_secret = bcrypt.hashpw(self.secret.hex().encode('utf-8'), bcrypt.gensalt())
        return self.save_secret

    def validate(self, secret):
        if secret is not None and self.secret is None:
            self.secret = secret
        if self.secret is None:
            raise Exception('secret not set')
        if self.save_secret is None:
            raise Exception('save_secret not set or generated')
        return bcrypt.checkpw(self.secret.hex().encode('utf-8'), self.save_secret)
