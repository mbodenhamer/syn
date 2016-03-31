all: test

#-------------------------------------------------------------------------------

check:
	@check-manifest

build: check
	@python setup.py sdist bdist_wheel

.PHONY: check build
#-------------------------------------------------------------------------------

test:
	@coverage erase
	@tox
	@coverage html

show:
	@chromium-browser htmlcov/index.html

.PHONY: test show
#-------------------------------------------------------------------------------

cleandeps:
	@if [ -z $$(which fmap) ]; then \
	echo "fmap required; installing via pip" \
	sudo pip install fmap \
	fi

clean: cleandeps
	@fmap 'rm -f' '*.py[co]'
	@fmap -b rmdir __pycache__

.PHONY: cleandeps clean
#-------------------------------------------------------------------------------
