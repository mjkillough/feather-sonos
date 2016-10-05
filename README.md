# feather-sonos — [![Build Status](https://travis-ci.org/mjkillough/feather-sonos.svg?branch=master)](https://travis-ci.org/mjkillough/feather-sonos)

Controlling Sonos devices from a Feather HUZZAH (ESP8266) using MicroPython. :radio:


## Getting a development environment

### CPython

With Python 3.5+ installed:

```sh
virtualenv venv
. venv/bin/activate
pip install -r requirements-cpython.txt
```

### MicroPython (Unix)

With MicroPython 1.8.4+ installed:

```sh
export MICROPYPATH=lib/
micropython -m upip install -r requirements-micropython.txt
```


## Tests

The tests run on CPython and MicroPython's Unix port. They do not yet run on MicroPython's ESP8266 port.

### CPython

```sh
python -m unittest discover
```

### MicroPython (Unix)

```
for f in $(ls test_*); do micropython $f; done
```


## License

MIT

