# used to differentiate between different environments
# for example used in the deps target to install the appropriate dependencies.
CSA_ENVIRONMENT ?= production
export CSA_ENVIRONMENT

.PHONY: deps print-info test db-reset pep8 autopep8

# if make is run without any target, it runs the first one
all: print-info venv deps db-reset

print-info:
	@echo "--> Running for environment: $(CSA_ENVIRONMENT) <--"

# commands that need to run in the virtual environment need to activate it
# every time (hence `. venv/bin/activate &&`)

# install dependencies according to environment and also link ourselves as a
# package, grabbing information from setup.py
deps: print-info venv
	. venv/bin/activate && make deps-no-venv

deps-no-venv: print-info
	pip install -r requirements-$(CSA_ENVIRONMENT).txt $(PIP_ARGS)
	pip install -e .

# create python virtual environment
venv:
	virtualenv -p python3 venv --always-copy --prompt '(csa)'

test:
	. venv/bin/activate && python -m unittest -v ${TEST_ARGS}

# set LANG for variable localization (currency sign etc)
run-dev:
	. venv/bin/activate && LANG=el_GR.utf8 python ./manage.py runserver 0.0.0.0:8000

# drop existing tables, creates new ones, and insert test data
# TODO: don't do this when we release 1.0!
db-reset:
	. venv/bin/activate && python ./bin/db-setup.py --drop --init --test-data

pep8:
	. venv/bin/activate && \
		pep8 --exclude=csa/migrations,csa/settings.py csa

autopep8:
	. venv/bin/activate && \
		find ${SOURCE_FOLDERS} -name "*.py" | \
		    xargs autopep8 -j 0 --in-place

clean:
	rm -rf venv csa.egg-info
