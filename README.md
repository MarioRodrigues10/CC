# CC

UMinho's Computer Communications 2024/25 assignment. See [Assignment.pdf](Assignment.pdf) for more
details.

Grade: 19.5 / 20 :star:

### Authors

 - Afonso Santos (A104276)
 - Humberto Gomes (A104348)
 - Mário Rodrigues (A100109)

# Setup

Start by cloning this repository, and creating a Python virtual environment:

```
$ git clone https://github.com/mariorodrigues10/CC.git
$ python -m venv .venv
```

To run the project, start by running:

```
$ source .venv/bin/activate
$ pip install .
```

To run the server and the agent, run, respectively:

```
$ python -m server
$ python -m agent
```

To exit the virtual environment, you can run:

```
$ deactivate
```

# Developers

All code must be verified with the `pylint` and `mypy` static checkers, which can be installed
(inside the `venv`) with the following command:

```
$ pip install pylint mypy
```

Before opening a Pull Request, please run your code though `pylint` and `mypy`, fixing any error
that may appear:

```
$ pylint server agent common
$ mypy server agent common
```

Our configuration for these checkers disallows the use of dynamic typing, and your PR won't be
accepted if these checks are failing.
