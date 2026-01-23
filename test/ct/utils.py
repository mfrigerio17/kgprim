import random, math, string
import numpy as np
import sympy as sp

import kgprim.motions as motions
import kgprim.values  as numeric_argument
from kgprim.motions import MotionSequence, MotionStep

import kgprim.ct.backend.symbolic as symBackend
import kgprim.ct.repr.mxrepr

kinds = list(MotionStep.Kind)
axes  = list(motions.Axis)


class RandomMotionGenerator:
    def __init__(self, stepSizeGenerator):
        self.stepSizeGen = stepSizeGenerator

    def randomMotionStep(self, kind=None, axis=None):
        kind = kind or random.choice(kinds)
        axis = axis or random.choice(axes)
        amount = self.stepSizeGen()
        return MotionStep(kind, axis, amount)

    def randomMotionSteps(self, maxStepsCount=8, stepKind=None):
        steps_count = math.floor( random.random() * (maxStepsCount+1) )
        return [self.randomMotionStep(stepKind) for _dummy_ in range(steps_count) ]

    def randomRotations(self, maxStepsCount=8):
        return self.randomMotionSteps(maxStepsCount, MotionStep.Kind.Rotation)

    def randomMotion(self, maxStepsCount=8):
        return MotionSequence(self.randomMotionSteps(maxStepsCount), MotionSequence.Mode.currentFrame)

    #TODO add randomPath, with motion sequences with different convention

def symbolsGenerator():
    # Generates a number 50% of the time, a symbol 50% of the time
    if random.random() > 0.5 :
        return random.random()
    else :
        return numeric_argument.Expression( numeric_argument.Variable(name=random.choice(string.ascii_letters)) )



class NumericMixin:
    '''
    A mixin class to help test the numeric backend for the matrix representation
    of coordinate transforms
    '''
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.generator = RandomMotionGenerator( random.random )

    def randomMotion(self):
        return self.generator.randomMotion()
    def randomRotations(self):
        return self.generator.randomRotations()

    def equal_matrix(self, M1, M2):
        return np.array_equal( np.round(M1,5) , np.round(M2,5) )

    def mult_matrix(self, M1, M2):
        return M1 @ M2

    def identity(self):
        return np.identity( self.matrixSize() )

    def transpose(self, mx):
        return np.transpose(mx)

    def prettyStr(self, mx):
        return mx.__str__()


class SymbolicMixin():
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.generator = RandomMotionGenerator( symbolsGenerator )

    def randomMotion(self):
        return self.generator.randomMotion(maxStepsCount=4) # a bit simpler cases (4 steps) otherwise the tests are too slow
    def randomRotations(self):
        return self.generator.randomRotations(maxStepsCount=4)

    def equal_matrix(self, M1, M2):
        M1 = self._extract_sympy_matrix(M1)
        M2 = self._extract_sympy_matrix(M2)
        M1 = sp.nsimplify(sp.trigsimp(M1), tolerance=1e-5, rational=True)
        M2 = sp.nsimplify(sp.trigsimp(M2), tolerance=1e-5, rational=True)
        return M1.equals(M2)

    def mult_matrix(self, M1, M2):
        M1 = self._extract_sympy_matrix(M1)
        M2 = self._extract_sympy_matrix(M2)
        return M1 @ M2 # sympy too supports the '@' operator

    def identity(self):
        return sp.eye( self.matrixSize() )

    def transpose(self, mx):
        mx = self._extract_sympy_matrix(mx)
        return sp.transpose(mx)

    def prettyStr(self, mx):
        return sp.pretty(mx.mx)

    def _extract_sympy_matrix(self, mx):
        return mx.mx if isinstance(mx, symBackend.MyMx) else mx


class HomReprMixin:
    def __init__(self, **kwds):
        super().__init__(**kwds)

    def matrixSize(self):
        return 4

class SpatialReprMixin():
    def __init__(self, **kwds):
        super().__init__(**kwds)

    def matrixSize(self):
        return 6


class NumericHomogeneous (NumericMixin , HomReprMixin):
    def asMatrix(self, ct):
        return kgprim.ct.repr.mxrepr.hCoordinatesNumeric(ct)

class SymbolicHomogeneous(SymbolicMixin, HomReprMixin):
    def asMatrix(self, ct):
        return kgprim.ct.repr.mxrepr.hCoordinatesSymbolic(ct)

class NumericSpatial (NumericMixin , SpatialReprMixin):
    def asMatrix(self, ct):
         # defaults to motion vectors; I could randomize the choice of motion/force
        return kgprim.ct.repr.mxrepr.spatialMotionNumeric(ct)

    def asMotionTransform(self, ct):
        return kgprim.ct.repr.mxrepr.spatialMotionNumeric(ct)

    def asForceTransform(self, ct):
        return kgprim.ct.repr.mxrepr.spatialForceNumeric(ct)

class SymbolicSpatial(SymbolicMixin, SpatialReprMixin):
    def asMatrix(self, ct):
         # defaults to motion vectors; I could randomize the choice of motion/force
        return kgprim.ct.repr.mxrepr.spatialMotionSymbolic(ct)

    def asMotionTransform(self, ct):
        return kgprim.ct.repr.mxrepr.spatialMotionSymbolic(ct)

    def asForceTransform(self, ct):
        return kgprim.ct.repr.mxrepr.spatialForceSymbolic(ct)

