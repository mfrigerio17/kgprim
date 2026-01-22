'''
Matrix representations for coordinate transforms.

This module contains a few functors that create a matrix representation of the
given `kgprim.ct.models.CoordinateTransform` model. The available
representations are:
  - pure rotation matrix (possible translation components in the transform are
    discarded)
  - 4x4 matrix for homogeneous coordinates vectors
  - 6x6 matrix for spatial motion vectors
  - 6x6 matrix for spatial force vectors

For any matrix, one can choose between two concrete backends for the matrix
data: numeric and symbolic (using respectively Numpy and Sympy).
The symbolic option is required whenever the coordinate transform depends on at
least one non-constant argument, like a `kgprim.values.Variable` or a
`kgprim.values.Parameter`.

For example:

```python
import kgprim.ct.repr.mxrepr as mxrepr

H = mxrepr.hCoordinatesNumeric( ct )
R = mxrepr.rotationMatrixNumeric( ct )
M = mxrepr.spatialMotionSymbolic( ct )
```

Please see `test/ct/sample.py` in the project repository for a more complete
example.
'''

from kgprim.ct.repr import mxcommon
from kgprim.ct.repr import homogeneous
from kgprim.ct.repr import spatial
from kgprim.ct.backend.numeric  import NumericMixin
from kgprim.ct.backend.symbolic import SymbolicMixin

from enum import Enum

class MatrixRepresentation(Enum):
    '''
    Enumeration of the matrix representations available from this module
    '''

    homogeneous = 0
    spatial_motion = 1
    spatial_force = 2
    pure_rotation = 3


class MatrixRepresentationMixin:
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.matrix = {
            mxcommon.ROT : self.rotation,
            mxcommon.TR  : self.translation
        }

    def rotation(self, axis, polarity, angle):
        mx = self.identity()
        s  = self.sin(angle);
        c  = self.cos(angle);
        self.setRotation(axis, polarity, mx, s, c)
        return mx

    def translation(self, axis, polarity, length):
        mx = self.identity()
        self.setTranslation(axis, polarity, mx, length)
        return mx

    # make the object look like a functor, returning the matrix representation
    def __call__(self, ct):
        return self.matrix_repr(ct) # this is defined in the backend mixins


# Compose the mixins to get concrete types that can produce a matrix
# representation of a coordinate transform:

class RotationMatrixNumeric (MatrixRepresentationMixin, NumericMixin , homogeneous.RotationMatrixMixin): pass
class RotationMatrixSymbolic(MatrixRepresentationMixin, SymbolicMixin, homogeneous.RotationMatrixMixin): pass

class HCoordinatesNumeric (MatrixRepresentationMixin, NumericMixin , homogeneous.HCoordinatesMixin): pass
class HCoordinatesSymbolic(MatrixRepresentationMixin, SymbolicMixin, homogeneous.HCoordinatesMixin): pass

class SpatialMotionNumeric (MatrixRepresentationMixin, NumericMixin , spatial.MotionVectorMixin): pass
class SpatialMotionSymbolic(MatrixRepresentationMixin, SymbolicMixin, spatial.MotionVectorMixin): pass

class SpatialForceNumeric (MatrixRepresentationMixin, NumericMixin , spatial.ForceVectorMixin): pass
class SpatialForceSymbolic(MatrixRepresentationMixin, SymbolicMixin, spatial.ForceVectorMixin): pass

rotationMatrixNumeric  = RotationMatrixNumeric ()
rotationMatrixSymbolic = RotationMatrixSymbolic()

hCoordinatesNumeric    = HCoordinatesNumeric   ()
hCoordinatesSymbolic   = HCoordinatesSymbolic  ()

# The spatial motion representation defaults to the convention with rotational
# coordinates on top of the matrix. To use the other convention, pass the
# keyword argument, as in:
#
# obj = SpatialMotionNumeric(spatialCoordinatesConvention = spatial.CoordinatesConvention.translationOnTop)

spatialMotionNumeric   = SpatialMotionNumeric  ()
spatialMotionSymbolic  = SpatialMotionSymbolic ()

spatialForceNumeric    = SpatialForceNumeric   ()
spatialForceSymbolic   = SpatialForceSymbolic  ()

symbolic = {
    MatrixRepresentation.homogeneous    : hCoordinatesSymbolic,
    MatrixRepresentation.spatial_motion : spatialMotionSymbolic,
    MatrixRepresentation.spatial_force  : spatialForceSymbolic,
    MatrixRepresentation.pure_rotation  : rotationMatrixSymbolic
}


def constantCoefficients(symbMatrix):
    '''
    Returns a tuple with the list of (row,col) tuples corresponding to the
    constant coefficients of the given matrix, and a second tuple for the
    variable coefficients.
    `symbMatrix` is expected to be a Sympy matrix object.
    '''
    # The function internally uses Sympy's `is_number`, which essentially checks
    # whether the coefficient can evaluate to a number. That also works for
    # symbols inside `kgprim.values.Constant`, and does exactly what we want. If
    # there is any other symbol in the expression of the coefficient, from the
    # modeling standpoint that coefficient is "variable".
    # Note that Sympy's `is_constant` is much more sophisticated (and expensive)
    # and not required here

    constants = []
    variables = []
    for r in range(0, symbMatrix.rows) :
        for c in range(0, symbMatrix.cols) :
            if symbMatrix[r,c].is_number :
                constants.append( (r,c) )
                # if symbMatrix[r,c].is_Float :
                #    floats.append( (r,c) )
            else :
                variables.append( (r,c) )
    return tuple(constants), tuple(variables)


# We could leverage knowledge about the structure of the matrix, not to check
# the coefficients that are known to be constant (e.g. 0 or 1).
# See the code below for a way to do it. However, some basic profiling showed me
# that it is not worth the additional complexity. This is because Sympy's
# is_number is pretty fast, especially for coefficients which are structurally
# sympy.core.numbers...

##def __extend_coeff_lists(matrix, l_constants, l_variables, row_range, col_range):
##    for r in row_range :
##        for c in col_range :
##            if matrix[r,c].is_number :
##                l_constants.append( (r,c) )
##            else :
##                l_variables.append( (r,c) )
##
##def _constant_coefficients_rotationm(matrix):
##    constants = []
##    variables = []
##    __extend_coeff_lists(matrix, constants, variables, range(0, 3), range(0, 3))
##    return tuple(constants), tuple(variables)
##
##def _constant_coefficients_homogeneous(matrix):
##    constants = []
##    variables = []
##    __extend_coeff_lists(matrix, constants, variables, range(0, 3), range(0, 4))
##    constants.extend( [(3,0),(3,1),(3,2),(3,3)] )
##    return tuple(constants), tuple(variables)
##
##def _constant_coefficients_spatial(matrix, spatial_kind, coords_convention):
##    constants = []
##    variables = []
##
##    # The two 3x3 diagonal blocks are _invariably_ the same rotation matrix.
##    # So we check those coefficients first.
##    # I cannot reuse the common code, because here I add two (r,c) coordinates
##    #  at a time
##    for r in range(0, 3) :
##        for c in range(0, 3) :
##            if matrix[r,c].is_number :
##                constants.extend( [(r,c), (r+3,c+3)] )
##            else :
##                variables.extend( [(r,c), (r+3,c+3)] )
##
##    # One of the other two 3x3 blocks is always 0, the other is non-0. Their
##    # positions depend on the vector type (motion or force) and on the
##    # coordinates convention (angular on top/bottom)
##    # --> motion-angular_top is the same as force-angular_bottom <--
##    if ((spatial_kind == MatrixRepresentation.spatial_motion) and
##        (coords_convention == spatial.CoordinatesConvention.rotationOnTop)) or (
##          (spatial_kind == MatrixRepresentation.spatial_force) and
##        (coords_convention == spatial.CoordinatesConvention.translationOnTop)) :
##        # these are the zeros
##        constants.extend([ (0, 3), (0, 4), (0, 5), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5)] )
##        # non-zero, need to look at them
##        rows_to_check = range(3, 6)
##        cols_to_check = range(0, 3)
##    else :
##        constants.extend( [(3, 0), (3, 1), (3, 2), (4, 0), (4, 1), (4, 2), (5, 0), (5, 1), (5, 2)] )
##        rows_to_check = range(0, 3)
##        cols_to_check = range(3, 6)
##
##    __extend_coeff_lists(matrix, constants, variables, rows_to_check, cols_to_check)
##    return tuple(constants), tuple(variables)

class MatrixReprMetadata:
    '''
    Metadata of a matrix representation of a coordinate transform
    '''

    def __init__(self, coordinateTransformMetadata, matrixRepresentation,
                 reprKind):
        ccoeff, vcoeff = constantCoefficients(matrixRepresentation)
##        if reprKind == MatrixRepresentation.pure_rotation:
##            ccoeff, vcoeff = _constant_coefficients_rotationm(matrixRepresentation)
##        elif reprKind == MatrixRepresentation.homogeneous:
##            ccoeff, vcoeff = _constant_coefficients_homogeneous(matrixRepresentation)
##        else:
##            ccoeff, vcoeff = _constant_coefficients_spatial(matrixRepresentation, reprKind, spatialCoordsConvention)

        self.variableCoefficients = vcoeff
        self.constantCoefficients = ccoeff
        self.mx = matrixRepresentation
        self.representationKind = reprKind
        self.ctMetadata = coordinateTransformMetadata

    def rows(self):   return self.mx.rows
    def cols(self):   return self.mx.cols

    def __eq__(self, rhs):
        return (isinstance(rhs, MatrixReprMetadata)
                and (self.ctMetadata.ct == rhs.ctMetadata.ct)
                and (self.mx == rhs.mx))

    def __hash__(self) :
        return 31*hash(self.ctMetadata.ct) + 93*hash(self.mx)

    @property
    def constantCoefficientCoordinates(self):
        '''
        A sequence of the (row,col) tuples pointing at the constant coefficients
        of the matrix.
        '''
        return self.constantCoefficients

    @property
    def variableCoefficientCoordinates(self):
        '''
        A sequence of the (row,col) tuples pointing at the coefficients of the
        matrix which depend on variables/parameters.
        '''
        return self.variableCoefficients

    @property
    def transformMetadata(self):
        '''
        The metadata of the source coordinate transform this matrix is a
        representation of.
        This is the same object given to this instance's constructor.
        '''
        return self.ctMetadata
