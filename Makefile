.PHONY: cpython-venv
cpython-venv: venv/bin/activate
venv/bin/activate: requirements-cpython.txt
	test -d venv || virtualenv venv
	venv/bin/pip install -Ur requirements-cpython.txt
	touch venv/bin/activate

.PHONY: cpython-test
cpython-test: cpython-venv
	venv/bin/python -m unittest discover


.PHONY: micropython-venv
micropython-venv: lib/marker
lib/marker: requirements-micropython.txt
	export MICROPYPATH=lib/
	test -d lib || mkdir lib
	micropython -m upip install -r requirements-micropython.txt
	touch lib/marker

.PHONY: micropython-test
micropython-test: micropython-venv
	export MICROPYPATH=lib/
	for f in $$(ls test_*); do micropython $$f; done
