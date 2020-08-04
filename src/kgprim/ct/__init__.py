'''
Coordinate transforms models and concrete representations.

This package contains facilities to represent coordinate transforms models, with
explicit semantics. The subpackages `repr` and `backend` allow to get concrete
matrix representations.

The module `frommotions` works in combination with the representations of
rigid motions in `kgprim.motions`, and allows to automatically compute the
coordinate transforms associated with a relative pose.
'''