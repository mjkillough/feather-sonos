SOURCES = discovery.py sonos.py upnp.py
TESTS = $(wildcard test_*.py) testhelpers.py


VENV_PY3 = venvs/py3
VENV_PY2 = venvs/py2
VENV_MPY = venvs/mpy

.DEFAULT_GOAL := micropython-test


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
	test -d $(VENV_MPY) || mkdir $(VENV_MPY)
	micropython -m upip install -p $(VENV_MPY) -r requirements-micropython.txt
	touch $(VENV_MPY)/marker

.PHONY: micropython-test
micropython-test: micropython-venv $(TESTS)
	( \
		export MICROPYPATH=$(VENV_MPY) && \
		for f in $(TESTS); do micropython $$f; done; \
	)


# MicroPython ESP8266 (depends on MicroPython Unix targets)
# Relies on a check-out of the MicroPython code and a working ESP8266 toolchain,
# as it bakes our code into the MicroPython firmware as frozen modules.
# (The source code is too large to run interpretted on the ESP8266)

MICROPYTHON_TREE=~/Code/micropython/
PORT=/dev/ttyUSB0

.PHONY: esp8266-python2-venv
esp8266-python2-venv: $(VENV_PY2)/marker
$(VENV_PY2)/marker: requirements-build.txt
	test -d $(VENV_PY2) || virtualenv -p python2 $(VENV_PY2)
	$(VENV_PY2)/bin/pip install -r requirements-build.txt
	touch $(VENV_PY2)/marker

.PHONY: esp8266-build
esp8266-build: $(MICROPYTHON_TREE)/esp8266/build/firmware-combined.bin
$(MICROPYTHON_TREE)/esp8266/build/firmware-combined.bin: $(VENV_PY2)/marker $(VENV_MPY)/marker $(SOURCES) $(TESTS)
	ls -lh $(MICROPYTHON_TREE)/esp8266/build/firmware-combined.bin
	# Copy SOURCES and TESTS into the MicroPython source tree. In the future,
	# we may want a target that doesn't copy the tests in.
	# This also copies the files in the MicroPython 'virtualenv'. Again, not
	# all of these are needed outside of the tests.
	for f in $(SOURCES) $(TESTS) $(wildcard $(VENV_MPY)/*.py); do cp $$f $(MICROPYTHON_TREE)/esp8266/modules/; done
	( \
		source $(VENV_PY2)/bin/activate && \
		make -C $(MICROPYTHON_TREE)/mpy-cross && \
		make -C $(MICROPYTHON_TREE)/esp8266 axtls && \
		make -C $(MICROPYTHON_TREE)/esp8266 \
	)

.PHONY: esp8266-deploy
esp8266-deploy: esp8266-build
	( \
		source $(VENV_PY2)/bin/activate && \
		make -C $(MICROPYTHON_TREE)/esp8266 PORT=$(PORT) deploy \
	)

.PHONY: esp8266-tests
esp8266-test: esp8266-deploy
	ampy -p $(PORT) run run-tests.py


clean:
	-@rm -r $(VENV_MPY) 2> /dev/null
	-@rm -r $(VENV_PY2) 2> /dev/null
	-@rm -r $(VENV_PY3) 2> /dev/null
	# Cleanup gunk that upip leaves behind.
	-@rm micropython-*.tar.gz
	-@rm .pkg.json
	# Cleanup files we copied into MicroPython source tree.
	-@for f in $(SOURCES) $(TESTS) $(wildcard $(VENV_MPY)/*.py); do rm $(MICROPYTHON_TREE)/esp8266/modules/$ff 2> /dev/null; done
	# Do a clean of MicroPython.
	make -C $(MICROPYTHON_TREE)/mpy-cross clean
	make -C $(MICROPYTHON_TREE)/lib/axtls clean
	make -C $(MICROPYTHON_TREE)/esp8266 clean
