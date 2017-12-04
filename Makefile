.PHONY: test upload clean bootstrap

test:
	sh -c '. venv/bin/activate; pip3 install -r requirements-dev.txt; py.test'

test-all:
	tox

upload: test-all
	python setup.py sdist bdist_wheel upload
	make clean

register:
	python setup.py register

clean:
	rm -f MANIFEST
	rm -rf build dist
	rm -rf .tox
	rm -rf *.egg-info
	rm -rf docs/_build/*
	rm -rf htmlcov

bootstrap: virtualenv
	venv/bin/pip3 install -e .
ifneq ($(wildcard requirements.txt),)
	venv/bin/pip3 install -r requirements.txt
endif
ifneq ($(wildcard requirements-dev.txt),)
	venv/bin/pip3 install -r requirements-dev.txt
endif
	make clean

virtualenv:
	virtualenv venv
	venv/bin/pip3 install --upgrade setuptools

init:
	sh -c '. . venv/bin/activate; pip3 install -r requirements.txt;'

dev-init:
	sh -c '. venv/bin/activate; pip3 install -r requirements-dev.txt;'

run:
	sh -c '. venv/bin/activate; python3 copdai_core/__main__.py;'

