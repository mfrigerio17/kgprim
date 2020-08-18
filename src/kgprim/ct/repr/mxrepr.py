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
    constants = []
    variables = []
    for r in range(0, symbMatrix.rows) :
        for c in range(0, symbMatrix.cols) :
            if symbMatrix[r,c].is_constant() :
                constants.append( (r,c) )
                # if symbMatrix[r,c].is_Float :
                #    floats.append( (r,c) )
            else :
                variables.append( (r,c) )
    return tuple(constants), tuple(variables)

class MatrixReprMetadata:
    '''
    Metadata of a matrix representation of a coordinate transform
    '''

    def __init__(self, coordinateTransformMetadata, matrixRepresentation,
                 reprKind):

        ccoeff, vcoeff = constantCoefficients(matrixRepresentation)
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

