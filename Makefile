# used to differentiate between different environments
# for example used in the deps target to install the appropriate dependencies.
CSA_ENVIRONMENT ?= production

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
	. venv/bin/activate && pip install -r requirements-$(CSA_ENVIRONMENT).txt
	. venv/bin/activate && pip install -e .

# create python virtual environment
venv:
	virtualenv -p python3 venv --always-copy --prompt '(csa)'

test:
	. venv/bin/activate && python -m unittest -v ${TEST_ARGS}

run-dev:
	# set LANG for variable localization (currency sign etc)
	. venv/bin/activate && LANG=el_GR.utf8 python ./manage.py runserver 0.0.0.0:8000

# drop existing tables, creates new ones, and insert test data
db-reset:
	# TODO: don't do this when we release 1.0!
	rm -rf csa/migrations db.sqlite3
	. venv/bin/activate && python ./bin/db-setup.py --drop --init --test-data

pep8:
	. venv/bin/activate && \
		pep8 --exclude=csa/migrations,csa/settings.py csa

autopep8:
	. venv/bin/activate && \
		find ${SOURCE_FOLDERS} -name "*.py" | \
		    xargs autopep8 -j 0 --in-place

models-graph:
	. venv/bin/activate && \
		python ./manage.py graph_models csa -g -o models-graph.png

clean:
	rm -rf venv csa.egg-info db.sqlite3
