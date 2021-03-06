This is the Kinematics/Geometric primitives Python package.

This project provides some types and functions to represent entities
relevant for kinematics like rigid bodies, frames, points, rigid motions.

Most of the types are purely symbolic placeholders, and are meant to be used
for building models, with Python.

The `ct` package contains facilities to model coordinate-transforms, and also
to get concrete matrix representations.

# Code documentation

More information about the packages and the modules of this project is available
in the code itself.

You can generate e.g. html documentation using
[pdoc3](https://pdoc3.github.io/pdoc/) (requires Python 3.5+).
For example:

```shell
pip install pdoc3  # don't forget the '3'
cd src/
pdoc --html --config show_source_code=False -o /tmp/docs kgprim/ motiondsl/
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
pip install wheel           # also required to set up the env

```

Do **not** use `python setup.py install`, as that will not work correctly (and
I believe it is deprecated anyway). You can however use
`python setup.py realclean` to remove installation artifacts from the source
tree.

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
The module `test/ct/testcore.py` is a test suite for the `kgprim.ct` package
which indirectly also covers the `kgprim.motions` module. If you installed the
packages correctly, run the tests simply by executing the module,
as in `python3 testcore.py`.

Similarly, the `test/values.py` performs some simple tests on the types defined
in the `kgprim.values` module.

# License
Copyright 2020, Marco Frigerio

Distributed under the BSD 3-clause license. See the `LICENSE` file for more
details.
