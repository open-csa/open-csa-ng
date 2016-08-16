
## Dependencies ##

* `python3`
* `sqlite3` (temporarily, until we get a dedicated db)

## How to install ##

First you need to clone the repository.

Then to setup the application, run the following command:

```
$ CSA_ENVIRONMENT=development make
```

Depending on the kind of installation you're after, you need to adjust the
`CSA_ENVIRONMENT` variable accordingly. (one of `production`, `development`,
`test`). The difference is in the dependencies that are installed, since some
dependencies are needed only for specific environments.

Running `make` will:

1. Create a virtual environment under `venv`.
2. Install dependencies (including dev and test dependencies).
3. Initialize the database.


## How to run ##

To run the application for development, do:

```
$ ./manage.py runserver
```

## Other ##

See folder `docs/` for some documentation and guidelines.
