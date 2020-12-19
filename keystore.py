import sqlite3
import sys
from .keydata import KeyData


class KeyStore:
    db = None

    def __init__(self, database_file):
        self.db = sqlite3.connect(database_file)

        def dict_factory(cursor, row):
            d = {}
            for index, column in enumerate(cursor.description):
                d[column[0]] = row[index]
            return d

        self.db.row_factory = dict_factory

        if not self.db:
            raise ConnectionError()

        cursor = self.db.cursor()
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='keys'")
        if cursor.fetchone()['count(*)'] == 0:
            self.db.execute(
                "CREATE TABLE keys ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "owner TEXT NOT NULL UNIQUE, "
                "identifier INTEGER UNIQUE, "
                "access_key TEXT, "
                "save_secret TEXT, "
                "enabled INTEGER DEFAULT 1"
                ")"
            )
            self.db.execute("CREATE TABLE metadata (key TEXT NOT NULL UNIQUE PRIMARY KEY, value TEXT)")
            self.db.execute("INSERT INTO metadata (key, value) VALUES ('db_version', '2')")
        cursor.close()

    def add_new_key(self, identifier, owner) -> KeyData or None:
        new_key, secret = KeyData.generate_new(identifier)
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO keys(identifier, owner, access_key, save_secret) VALUES (?, ?, ?, ?)",
            (int.from_bytes(identifier, byteorder='big'),
             owner,
             new_key.get_access_key().hex(),
             new_key.get_save_secret())
        )
        self.db.commit()
        cursor.close()
        return secret, new_key

    def get_key_from_db(self, identifier) -> KeyData or None:
        cursor = self.db.cursor()
        cursor.execute("SELECT access_key, save_secret FROM keys WHERE identifier = ?",
                       (int.from_bytes(identifier, byteorder='big'),))
        key_raw = cursor.fetchone()
        if key_raw is None or len(key_raw) != 2:
            return None
        return KeyData(identifier, bytes().fromhex(key_raw['access_key']), None, key_raw['save_secret'])

    def get_key_list(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT id, owner, identifier, access_key, save_secret, enabled FROM keys")
        return cursor.fetchall()

    def get_userdata(self, id_or_owner):
        cursor = self.db.cursor()
        if isinstance(id_or_owner, int):
            query = "SELECT id, owner, enabled FROM keys WHERE id = ?"
        else:
            query = "SELECT id, owner, enabled FROM keys WHERE owner = ?"

        cursor.execute(query, (id_or_owner,))
        key = cursor.fetchone()
        cursor.close()
        if not key:
            print(
                "Could not find key of owner with {} {}".format(
                    'ID' if isinstance(id_or_owner, int) else 'username',
                    id_or_owner
                )
            )
            sys.exit(1)

        return key

    def set_enabled(self, id_or_owner, active: bool):
        key = self.get_userdata(id_or_owner)

        if key['enabled'] == active:
            print("Key of owner {} already {}abled".format(key['owner'], 'en' if active else 'dis'))
        else:
            cursor = self.db.cursor()
            cursor.execute("UPDATE keys SET enabled = ? WHERE id = ?", (active, key['id']))
            self.db.commit()
            cursor.close()
            print("{}abled key of owner {}".format('En' if active else 'Dis', key['owner']))

    def remove(self, id_or_owner):
        key = self.get_userdata(id_or_owner)

        if key['enabled']:
            print("Key of owner {} is not disabled. Cannot remove enabled keys.".format(key['owner']))
            sys.exit(1)

        cursor = self.db.cursor()
        cursor.execute("DELETE FROM keys WHERE id = ? and enabled = 0", (key['id'],))
        self.db.commit()
        cursor.close()
        print("Removed key of owner {}".format(key['owner']))
