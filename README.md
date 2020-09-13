nfclock
=======

Simple tool to identify and authenticate (cheap) NFC tags against a DB of known authorized keys. In the current version
this tool switches the GPIO pin of a raspberry pi to grant access to connected hardware.

Basic operation
---------------

nfclock can be started in two different modes, 'add-key' and 'authenticate-key'.

The 'add-key' mode is used to write a random secret to the tag and the corresponding bcrypt hash to an sqlite database.
The tag is then locked and can only be read by providing an access key which is also saved in the database.

The 'authencate-key' uses the identifier of a connected tag to retrieve access key and hash from the database, read the
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
python 3 -m nfclock [--add-key] [--database-file file] [--pin p]
    --add-key Switch nfclock to 'add-key' mode.
    --database-file file Use file as the key database. Defaults to /etc/nfclock/keystore.sqlite
    --pin p Switch this GPIO pin on succesful authentication.
```

In 'add-key' mode, simply put a tag on the reader and wait for the program to finish. nfclock will exit after each tag.

In 'authenticate-key' mode, nfclock will run in an endless loop and basically pull the configured pin high as long as a
valid tag is placed on the reader.
