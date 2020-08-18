'''
Coordinate transforms models and concrete representations.

This package contains facilities to represent coordinate-transform objects, with
explicit semantics. The subpackages `kgprim.ct.repr` and `kgprim.ct.backend`
allow to get the concrete matrix representation of a transform.

The module `kgprim.ct.frommotions` allows to compute the coordinate transform(s)
associated with a rigid motion model from the module `kgprim.motions`.

See the file `test/ct/sample.py`:

```python
.. include:: ../../../test/ct/sample.py
```

'''
