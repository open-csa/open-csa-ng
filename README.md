
You will need python3 to run the application.

## How to install ##

Depending on the kind of installation you're looking for, you might need to
setup the `CSA_ENVIRONMENT` variable. For local development you should do:

```
$ CSA_ENVIRONMENT=development make
```

This will:

1. Create a virtual environment under `venv`.
2. Install dependencies (including dev and test dependencies).
3. Initialize the database.


## How to run ##

To run the application for development, do:

```
$ ./manage.py runserver
```
