all: test

VERSION = `./metadata syn/metadata.yml version` 

IMAGE = mbodenhamer/syn-dev
PYDEV = docker run --rm -it -e BE_UID=`id -u` -e BE_GID=`id -g` \
	-v $(CURDIR):/app $(IMAGE)
VERSIONS = 2.7.11,3.4.4,3.5.1

#-------------------------------------------------------------------------------
# Docker image management

docker-build:
	@docker build -t $(IMAGE):latest --build-arg versions=$(VERSIONS) .

docker-first-build:
	@docker build -t $(IMAGE):latest --build-arg versions=$(VERSIONS) \
	--build-arg reqs=requirements.in \
	--build-arg devreqs=dev-requirements.in .
	@$(PYDEV) pip-compile dev-requirements.in
	@$(PYDEV) pip-compile requirements.in

docker-rmi:
	@docker rmi $(IMAGE)

docker-push:
	@docker push ${IMAGE}:latest

docker-pull:
	@docker pull ${IMAGE}:latest

docker-shell:
	@$(PYDEV) bash

.PHONY: docker-build docker-first-build docker-rmi docker-shell
#-------------------------------------------------------------------------------
# Build management

check:
	@$(PYDEV) check-manifest

build: check
	@$(PYDEV) python setup.py sdist bdist_wheel

.PHONY: check build
#-------------------------------------------------------------------------------
# Documentation

docs:
	@$(PYDEV) sphinx-apidoc -f -o docs/ syn/ $$(find syn -name tests)
	@$(PYDEV) make -C docs html

view:
	@python -c "import webbrowser as wb; \
	wb.open('docs/_build/html/index.html')"

.PHONY: docs view
#-------------------------------------------------------------------------------
# Dependency management

pip-compile:
	@$(PYDEV) pip-compile dev-requirements.in
	@$(PYDEV) pip-compile requirements.in

print-version:
	@echo $(VERSION)

.PHONY: pip-compile print-version
#-------------------------------------------------------------------------------
# Tests

SAMPLES_1 = export SYN_TEST_SAMPLES=1
SAMPLES_100 = export SYN_TEST_SAMPLES=100
SAMPLES_1000 = export SYN_TEST_SAMPLES=1000
RANDOM_SEED = export SYN_RANDOM_SEED=1
SUPPRESS = export SYN_SUPPRESS_TEST_ERRORS
PY34 = source .tox/py34/bin/activate
QUICK_TEST = nosetests -v --pdb --pdb-failures
PROFILE_TEST = nosetests -v --with-profile
HEAVY_TEST = nosetests -v --processes=4 --process-timeout=40

test:
	@$(PYDEV) coverage erase
	@$(PYDEV) tox
	@$(PYDEV) coverage html

quick-test:
	@$(PYDEV) bash -c "$(SAMPLES_1); $(RANDOM_SEED); $(QUICK_TEST)"

unit-test:
	@$(PYDEV) bash -c "$(SAMPLES_100); $(HEAVY_TEST)"

unit-profile:
	@$(PYDEV) bash -c "$(SAMPLES_100); $(PROFILE_TEST)"

heavy-test:
	@$(PYDEV) bash -c "$(SAMPLES_1000); $(SUPPRESS); $(HEAVY_TEST)"

py3-quick-test:
	@$(PYDEV) bash -c "$(PY34); $(SAMPLES_1); $(RANDOM_SEED); $(QUICK_TEST)"

py3-unit-test:
	@$(PYDEV) bash -c "$(PY34); $(SAMPLES_100); $(HEAVY_TEST)"

py3-heavy-test:
	@$(PYDEV) bash -c "$(PY34); $(SAMPLES_1000); $(SUPPRESS); $(HEAVY_TEST)"

dist-test: build
	@$(PYDEV) dist-test $(VERSION)

show:
	@python -c "import webbrowser as wb; wb.open('htmlcov/index.html')"

.PHONY: test quick-test py3-quick-test unit-test py3-unit-test dist-test show
.PHONY: heavy-test py3-heavy-test
#-------------------------------------------------------------------------------
# Cleanup

clean:
	@$(PYDEV) fmap -r syn 'rm -f' '*.py[co]'
	@$(PYDEV) fmap -r syn -d rmdir __pycache__
	@$(PYDEV) make -C docs clean

.PHONY: clean
#-------------------------------------------------------------------------------
