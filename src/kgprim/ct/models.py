from enum import Enum

class CoordinateTransformPlaceholder:
    def __init__(self, leftFrame, rightFrame):
        self.leftF  = leftFrame
        self.rightF = rightFrame
    @property
    def leftFrame(self): return self.leftF
    @property
    def rightFrame(self): return self.rightF


class CoordinateTransform:
    '''
    A model of the transform from `rightFrame` coordinates to `leftFrame`
    coordinates.
    '''

    def __init__(self, leftFrame, rightFrame, primitives):
        self.rightF = rightFrame
        self.leftF  = leftFrame
        self._primitives = primitives

    @property
    def leftFrame(self): return self.leftF
    @property
    def rightFrame(self): return self.rightF
    @property
    def primitives(self):
        '''The list of `PrimitiveCTransform` this instance is comprised of.'''
        return self._primitives

    def __str__(self): return self.leftFrame.name + "_X_" + self.rightFrame.name
    def __repr__(self): return self.__str__()
    def __eq__(self, rhs):
        return (isinstance(rhs, CoordinateTransform)
               and self.leftF == rhs.leftF
               and self.rightF == rhs.rightF
               and self._primitives == rhs._primitives) # TODO this is too strict: I could have a different sequence which leads to the same transform
    def __hash__(self):
        return 3*hash(self.leftF) + 93*hash(self.rightF) + 31*hash(tuple(self.primitives))

class TransformPolarity(Enum):
    '''
    The attribute distinguishing the two coordinate transforms associated to the
    same rigid motion.

    Consider frame A and B, where B is taken to be moved with respect to A
    (e.g. by a rotation about z of alpha radians).
    The corresponding transform can take two forms: either it takes B
    coordinates and gives back A coordinates for the same vector, or the
    other way round. We call the first A_X_B and the second B_X_A.
    Assuming the matrix is always left multiplied with a column vector of
    coordinates (as in A_X_B * pB), this notation immediately tells which are
    the "input" and "output" frames.

    A_X_B has the `movedFrameOnTheRight` polarity, because B appears on the
    right hand side, B_X_A is instead `movedFrameOnTheLeft`.

    Technically, the polarity is an attribute of the relation between a rigid
    motion and a related coordinate transform.
    '''
    movedFrameOnTheRight = 0
    movedFrameOnTheLeft  = 1


class PrimitiveCTransform:
    '''
    A coordinate transform for a pure rotation/translation about/along one
    of the Cartesian axis.

    Instances of this class model the coordinate transforms associated with
    "primitive" motion steps, see `kgprim.motions.MotionStep`.
    '''

    strbits = {
        TransformPolarity.movedFrameOnTheRight : "R",
        TransformPolarity.movedFrameOnTheLeft  : "L"
    }

    def __init__(self, motion_step, polarity):
        self.motion   = motion_step
        self.polarity_= polarity

    @property
    def kind(self): return self.motion.kind
    @property
    def amount(self): return self.motion.amount
    @property
    def axis(self): return self.motion.axis
    @property
    def polarity(self): return self.polarity_

    @property
    def primitives(self):
        '''
        A list with the self element only.

        This method is implemented to emulate the behaviour of `CoordinateTransform`.
        '''
        return [self]

    def __str__(self):
        return 'ct_{pol}_{motion}'.format(
            pol=PrimitiveCTransform.strbits[self.polarity],
            motion=str(self.motion))
    def __repr__(self):
        return self.__str__()
    def __eq__(self, rhs):
        return (isinstance(rhs, PrimitiveCTransform)
               and self.motion == rhs.motion
               and self.polarity == rhs.polarity)
    def __hash__(self):
        return hash(self.motion) + 111*hash(self.polarity)


class CTransformsModel:
    '''
    A simple named container of coordinate transforms.
    '''
    def __init__(self, name, transforms):
        self.name = name
        self.transforms = transforms
