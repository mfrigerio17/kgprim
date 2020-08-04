from enum import Enum
import kgprim.ct.models as ctmodels
import kgprim.ct.repr.mxcommon as common


class CoordinatesConvention(Enum):
    rotationOnTop = 0
    translationOnTop = 1

class VectorType(Enum):
    motion = 0
    force  = 1

block_bottom_left = (slice(3,6),slice(0,3))
block_bottom_right= (slice(3,6),slice(3,6))
block_top_right   = (slice(0,3),slice(3,6))
block_top_left    = (slice(0,3),slice(0,3))


def __rotx__a_x_b(mx, s, c):
    common.__rotx__a_x_b(mx, s, c)
    #common.__rotx__a_x_b(mx[block_bottom_right], s, c) # this does not work with SymPy, the slice does not act as a view
    mx[block_bottom_right] = mx[block_top_left]  # this one instead works

def __rotx__b_x_a(mx, s, c):
    common.__rotx__b_x_a(mx, s, c)
    mx[block_bottom_right] = mx[block_top_left]

def __roty__a_x_b(mx, s, c):
    common.__roty__a_x_b(mx, s, c)
    mx[block_bottom_right] = mx[block_top_left]

def __roty__b_x_a(mx, s, c):
    common.__roty__b_x_a(mx, s, c)
    mx[block_bottom_right] = mx[block_top_left]

def __rotz__a_x_b(mx, s, c):
    common.__rotz__a_x_b(mx, s, c)
    mx[block_bottom_right] = mx[block_top_left]

def __rotz__b_x_a(mx, s, c):
    common.__rotz__b_x_a(mx, s, c)
    mx[block_bottom_right] = mx[block_top_left]



'''
The skew symmetric matrix associated with the vector (x,y,z)
         0   -z    y
         z    0   -x
        -y    x    0
'''
def __skew_x(mx, x):
    mx[1,2] = -x
    mx[2,1] =  x
def __skew_y(mx, y):
    mx[0,2] =  y
    mx[2,0] = -y
def __skew_z(mx, z):
    mx[0,1] = -z
    mx[1,0] =  z

def __set_skew(mx, length, blockSlice, whichSkew):
    # we need to do all these copies of subblocks because passing slices as r/w
    # views of the original matrix does NOT work in SymPy
    # With NumPy, the following would be sufficient:
    #   whichSkew( mx[ blockSlice ], length)

    block = mx[ blockSlice ]
    whichSkew(block, length)
    mx[ blockSlice ] = block



__tr_block = {
    CoordinatesConvention.rotationOnTop : {
        VectorType.motion : block_bottom_left,
        VectorType.force  : block_top_right
    },
    CoordinatesConvention.translationOnTop : {
        VectorType.motion : block_top_right,
        VectorType.force  : block_bottom_left
    }
}


onRight = ctmodels.TransformPolarity.movedFrameOnTheRight
onLeft  = ctmodels.TransformPolarity.movedFrameOnTheLeft

X = common.X
Y = common.Y
Z = common.Z


def _tr_matrix_setters(coordinates_convention):
    def matrix_setters(vector_kind):
        matrix_block     = __tr_block[coordinates_convention][vector_kind]
        return {
            X : {
                onRight : (lambda mx, length :  __set_skew(mx,  length, matrix_block, __skew_x)),
                onLeft  : (lambda mx, length :  __set_skew(mx, -length, matrix_block, __skew_x))
            },
            Y : {
                onRight : (lambda mx, length :  __set_skew(mx,  length, matrix_block, __skew_y)),
                onLeft  : (lambda mx, length :  __set_skew(mx, -length, matrix_block, __skew_y))
            },
            Z : {
                onRight : (lambda mx, length :  __set_skew(mx,  length, matrix_block, __skew_z)),
                onLeft  : (lambda mx, length :  __set_skew(mx, -length, matrix_block, __skew_z))
            }
        }
    return matrix_setters




# Pure rotation matrices for spatial vectors are the same regardless of the
# type of vector (motion or force), and regardless of the convention
setRot = {
    X : {
        onRight : __rotx__a_x_b,
        onLeft  : __rotx__b_x_a
    },
    Y : {
        onRight : __roty__a_x_b,
        onLeft  : __roty__b_x_a
    },
    Z : {
        onRight : __rotz__a_x_b,
        onLeft  : __rotz__b_x_a
    },
}


class SpatialCoordinatesMixin:
    def __init__(self, spatialCoordinatesConvention=CoordinatesConvention.rotationOnTop, **kwds):
        super().__init__(**kwds)
        self.coordinatesConvention = spatialCoordinatesConvention
        self.tr_matrix_setters = _tr_matrix_setters(spatialCoordinatesConvention)

    @property
    def matrixSize(self):
        return 6

    def setRotation(self, axis, polarity, mx, s, c):
        setRot[axis][polarity](mx, s, c)


class MotionVectorMixin(SpatialCoordinatesMixin):
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.translation_setters = self.tr_matrix_setters(VectorType.motion)

    def setTranslation(self, axis, polarity, mx, length):
        self.translation_setters[axis][polarity](mx, length)


class ForceVectorMixin(SpatialCoordinatesMixin):
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.translation_setters = self.tr_matrix_setters(VectorType.force)

    def setTranslation(self, axis, polarity, mx, length):
        self.translation_setters[axis][polarity](mx, length)

