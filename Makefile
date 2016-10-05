SOURCES = discovery.py sonos.py upnp.py
TESTS = $(wildcard test_*.py)


VENV_PY3 = venvs/py3
VENV_PY2 = venvs/py2
VENV_MPY = venvs/lib


# CPython

.PHONY: cpython-venv
cpython-venv: $(VENV_PY3)/bin/activate
$(VENV_PY3)/bin/activate: requirements-cpython.txt
	test -d $(VENV_PY3) || virtualenv $(VENV_PY3)
	$(VENV_PY3)/bin/pip install -Ur requirements-cpython.txt
	touch $(VENV_PY3)/bin/activate

.PHONY: cpython-test
cpython-test: cpython-venv
	$(VENV_PY3)/bin/python -m unittest discover


# MicroPython Unix

.PHONY: micropython-venv
micropython-venv: $(VENV_MPY)/marker
$(VENV_MPY)/marker: requirements-micropython.txt
	export MICROPYPATH=$(VENV_MPY)
	test -d $(VENV_MPY) || mkdir $(VENV_MPY)
	micropython -m upip install -r requirements-micropython.txt
	touch $(VENV_MPY)/marker

.PHONY: micropython-test
micropython-test: micropython-venv $(TESTS)
	export MICROPYPATH=$(VENV_MPY)
	for f in $(TESTS); do micropython $$f; done


# MicroPython ESP8266 (depends on MicroPython Unix targets)
# Relies on a check-out of the MicroPython code and a working ESP8266 toolchain,
# as it bakes our code into the MicroPython firmware as frozen modules.
# (The source code is too large to run interpretted on the ESP8266)

MICROPYTHON_TREE=~/Code/micropython/

.PHONY: esp8266-python2-venv
esp8266-python2-venv: $(VENV_PY2)/bin/activate
$(VENV_PY2)/bin/activate:
	test -d $(VENV_PY2) || virtualenv -p python2 $(VENV_PY2)
	$(VENV_PY2)/bin/pip install pyserial
	touch $(VENV_PY2)/bin/activate

.PHONY: esp8266-build
esp8266-build: esp8266-python2-venv micropython-venv $(SOURCES) $(TESTS)
	# Copy SOURCES and TESTS into the MicroPython source tree. In the future,
	# we may want a target that doesn't copy the tests in.
	for f in $(SOURCES) $(TESTS); do cp $$f $(MICROPYTHON_TREE)/esp8266/modules/; done
	( \
		source $(VENV_PY2)/bin/activate && \
		make -C $(MICROPYTHON_TREE)/mpy-cross && \
		make -C $(MICROPYTHON_TREE)/esp8266 axtls && \
		make -C $(MICROPYTHON_TREE)/esp8266 \
	)
	# NOTE: Leaves files behind in the MicroPython source tree. This means if
	# a module/dependency is removed, it is left in the firmware until you do
	# a `make clean` in the MicroPython tree.
