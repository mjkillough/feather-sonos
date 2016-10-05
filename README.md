# feather-sonos — [![Build Status](https://travis-ci.org/mjkillough/feather-sonos.svg?branch=master)](https://travis-ci.org/mjkillough/feather-sonos)

Controlling Sonos devices from a Feather HUZZAH (ESP8266) using MicroPython. :radio:


## Tests

### CPython

With Python 3.5+ installed, run:

```sh
make cpython-tests
```

... or the hard way:

```sh
virtualenv venv
. venv/bin/activate
pip install -r requirements-cpython.txt

python -m unittest discover
```

### MicroPython (Unix)

With MicroPython 1.8.4+ installed, run:

```sh
make micropython-test
```

... or the hard way:

```sh
export MICROPYPATH=lib/
micropython -m upip install -r requirements-micropython.txt

for f in $(ls test_*); do micropython $f; done
```


## License

MIT

