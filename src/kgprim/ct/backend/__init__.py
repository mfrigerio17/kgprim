'''
Numeric (based on Numpy) or symbolic (Sympy) backends for the concrete matrix
representations of coordinate transforms.

The symbolic backend is required whenever the coordinate transform depends on
at least one non-constant argument, like a `kgprim.values.Variable` or a
`kgprim.values.Parameter`.
'''
