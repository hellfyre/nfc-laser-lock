nfclock
=======

Simple tool to identify and authenticate (cheap) NFC tags against a DB of known authorized keys. In the current version
this tool switches the GPIO pin of a raspberry pi to grant access to connected hardware.

Basic operation
---------------

nfclock has a very simple CLI interface, which expects a command. The most important two are 'add' and 'auth'.

The 'add' command is used to write a random secret to the tag and the corresponding bcrypt hash to an sqlite database.
The tag is then locked and can only be read by providing an access key which is also saved in the database.

The 'auth' command uses the identifier of a connected tag to retrieve access key and hash from the database, read the
secret and compare its hash to the saved hash. If the hashes match, the configured GPIO pin is set to high and a timer
is started. After 15 seconds, the reader checks whether the tag is still present and if so, re-authenticates the tag. If
the authentication is successful, the cycle continues. If not, the pin is set to low 10 seconds after the failed
authentication.

Requirements
------------

This project uses
* bcrypt
* nfcpy
* gpiozero

Installation
------------

Either copy all *.py files to a directory on the target machine or build a wheel by running

```
setyp.py sdist bdist_wheel
```

Usage
-----

Run this tool as a module:

```
python 3 -m nfclock [-h] [--database-file DATABASE_FILE] [--pin PIN] [--id ID] [--owner OWNER] {auth,list,add,enable,disable,remove}
    -h This usage message
    --database-file file Use file as the key database. Defaults to /etc/nfclock/keystore.sqlite
    --pin PIN Switch this GPIO pin on succesful authentication.
    --id ID Identifier of the key to enable/disable/remove
    --owner OWNER Text-Identifier of the key to enable/disable/remove
    auth Start authentication loop
    list List keys in database
    add Add a new key; needs option --owner
    enable Enable a disabled key; needs option --id or --owner
    disable Disable an enabled key; needs option --id or --owner
    remove Remove a disabled key; needs option --id or --owner
```

### `auth`
The `auth` command lets nfclock run in an endless loop and basically pull the configured pin high as long as a valid tag
is placed on the reader.

### `list`
Lists all keys in the database provided by option `database-file`. You can check the key's ID, owner-string and
enabled/disabled status here.

### `add`
To add a new key, provide an arbitrary string to the `--owner` option while using the `add` command.

### `enable`
Re-enables disabled keys. Needs either `--id` or `--owner`.

### `disable`
Keys can be disabled to (temporarily) prevent them from successfully authenticating. Needs either `--id` or `--owner`.

### `remove`
To remove a key, it needs to be disabled first. Needs either `--id` or `--owner`.


