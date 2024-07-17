This is the Kinematics/Geometric primitives Python package.

This project provides some types and functions to represent entities
like rigid bodies, frames, points, rigid motions.

Most of the types are purely symbolic placeholders, and are meant to be used
for building models, with Python.

The `ct` package contains facilities to model coordinate-transforms, and also
to get concrete matrix representations.

# Code documentation

API and package documentation is hosted [here](https://mfrigerio17.github.io/kgprim/).

The HTML docs are generated from the docstrings in the source code,
using [pdoc](https://pdoc.dev/).

You can generate the docs offline from your working copy, with something
like:

```shell
cd src/
pdoc --no-show-source -o /tmp/docs kgprim/ motiondsl/
```

# Installation
```sh
git clone <repo> kgprim    # replace <repo> with the right URL
cd kgprim/
pip install .              # should also fetch and install the dependencies
```

Before doing the above, you might want to set up a Python3 virtual environment:

```sh
mkdir myvenv && python3 -m venv myvenv
source myvenv/bin/activate  # may need to pick another script depending on your shell
```


## Dependencies

Python > 3.3

Python packages:
  - [NetworkX](http://networkx.github.io/)

  - [SymPy](http://www.sympy.org), for the representation of variables,
    parameters and constants in the `values` module. Also for the symbolic
    matrix representation of coordinate transforms.

  - [NumPy](http://www.numpy.org), for the numerical matrix representation of
    coordinate transforms.

  - [textX](http://textx.github.io/textX/stable/), for the grammar of the
    MotionDSL language (required by the `motiondsl` package only).


# Testing
Testing code is based on the `unittest` framework from the standard library.
After installation (see above), one may run all the tests with something like:

```sh
python -m unittest discover --start-directory test/ --pattern '*.py'
```

The test modules can also be executed individually, e.g.:

```sh
python test/ct/testcore.py

# or
python -m test.ct.testcore

# or
python -m unittest test.ct.testcore
```

The module `test/ct/testcore.py` is a test suite for the `kgprim.ct` package
which indirectly also covers the `kgprim.motions` module.

Similarly, the `test/values.py` performs some simple tests on the types defined
in the `kgprim.values` module.

The package `test/motiondsl` has tests for the `motiondsl` package, though it
may also involve `kgprim.ct`.

# License
Copyright 2020-2024, Marco Frigerio

Distributed under the BSD 3-clause license. See the `LICENSE` file for more
details.
