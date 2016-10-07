## Run in vagrant for local development ##

Whether you're running on windows or linux, you'll need a working vagrant
installation and the `vagrant-vbguest` plugin. On linux you can install the
plugin with `vagrant plugin install vagrant-vbguest`.

You'll need to git clone the `open-csa-ng` repository, and from within the
`open-csa-ng` directory, run:

```
vagrant up
```

This is going to take a while, especially if you don't have the vagrant box
being used. Then you run:

```
vagrant ssh
```

to get into the machine. `ls` and see that there is an `open-csa-ng` folder
with all the files in. This is a shared folder between your actual host
machine, and the guest (virtual) machine. The application has been installed
with all required dependencies automatically.

Now you can develop your changes on your host machine with your favorite
editor, and ssh into the vagrant box (`vagrant ssh`) and use the casual method
to run the application. See `How to run` below. The application when run,
listens on port 8000. The port is forwarded on the host machine, so you can
browse to http://localhost:8080 to see the application while it is running in
the VM.

## Dependencies ##

* `python3`
* `virtualenv`
* `make`
* `sqlite3` (temporarily, until we get a dedicated db)
* `pkg-config`
* `graphviz`
* `libgraphviz-dev`

These are the names of the packages for debian and possibly ubuntu.

## How to install ##

First you need to clone the repository.

Then to setup the application, run the following command:

```
CSA_ENVIRONMENT=development make
```

Depending on the kind of installation you're after, you need to adjust the
`CSA_ENVIRONMENT` variable accordingly. (one of `production`, `development`,
`test`). The difference is in the dependencies that are installed, since some
dependencies are needed only for specific environments.

Running `make` will:

1. Create a virtual environment under `venv`.
2. Install dependencies (including dev and test dependencies).
3. Initialize the database.

### Usual problems in installation

#### pygraphviz

You might experience some problems while installing `pygraphviz`, in this case
most probably you are missing some of its dependencies. You should make sure then
whether the following packages are installed on your system.
* `python3-dev`
* `graphviz`
* `graphviz-dev`(or `libgraphviz-dev`, `graphviz-dev` will install it either way)

## How to run ##

To run the application for development, do:

```
$ CSA_ENVIRONMENT=development make run-dev
```

See `bin/db-setup.py` for builtin data for testing.

## Other ##

See folder `docs/` for some documentation, guidelines, and a nice models graph!
