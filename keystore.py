import sqlite3
from .keydata import KeyData


class KeyStore:
    db = None

    def __init__(self, database_file):
        self.db = sqlite3.connect(database_file)

        if not self.db:
            raise ConnectionError()

        cursor = self.db.cursor()
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='keys'")
        if cursor.fetchone()[0] == 0:
            self.db.execute(
                "CREATE TABLE keys (id INTEGER PRIMARY KEY AUTOINCREMENT, identifier INTEGER UNIQUE, access_key TEXT, save_secret TEXT)")
        cursor.close()

    def add_new_key(self, identifier) -> KeyData or None:
        new_key = KeyData.generate_new(identifier)
        secret = new_key[1]
        new_key = new_key[0]
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO keys(identifier, access_key, save_secret) VALUES (?, ?, ?)",
                       [int.from_bytes(identifier, byteorder='big'), new_key.get_access_key().hex(),
                        new_key.get_save_secret()]).fetchone()
        self.db.commit()
        cursor.close()
        return [secret, new_key]

    def get_key_from_db(self, identifier) -> KeyData or None:
        cursor = self.db.cursor()
        cursor.execute("SELECT access_key, save_secret FROM keys WHERE identifier = ?", [int.from_bytes(identifier, byteorder='big')])
        key_raw = cursor.fetchone()
        if key_raw is None or len(key_raw) != 2:
            return None
        return KeyData(identifier, bytes().fromhex(key_raw[0]), None, key_raw[1])
