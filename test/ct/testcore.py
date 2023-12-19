'''
These test cases really address the combined working of `kgprim.motions` and
`kgprim.ct.frommotions`, because it is hard to test the motions models
independently, without resorting to numerical representations.
'''

import random, math, unittest, string, logging
import numpy as np
import sympy as sp

import kgprim.core    as primitives
import kgprim.motions as motions
import kgprim.values  as numeric_argument
from kgprim.motions import MotionSequence, MotionStep

import kgprim.ct.models as ctmodels
import kgprim.ct.metadata as ctmetadata
from kgprim.ct.frommotions import toCoordinateTransform
import kgprim.ct.backend.numeric  as numBackend
import kgprim.ct.backend.symbolic as symBackend
import kgprim.ct.repr.mxrepr as ctrepr
import kgprim.ct.repr.homogeneous as reprHomogeneous
import kgprim.ct.repr.spatial     as reprSpatial


logger = logging.getLogger(__name__)

kinds = list(MotionStep.Kind)
axes  = list(motions.Axis)

# A couple of random frames/poses placeholders to be used in the tests

frA = primitives.Frame("A")
frB = primitives.Frame("B")
frC = primitives.Frame("C")

pBA = primitives.Pose(reference=frA, target=frB)
pCB = primitives.Pose(reference=frB, target=frC)

R_ct_T = ctmodels.TransformPolarity.movedFrameOnTheRight
T_ct_R = ctmodels.TransformPolarity.movedFrameOnTheLeft


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



class NumericMixin():
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

    def backendMixin(self):
        return numBackend.NumericMixin

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

    def backendMixin(self):
        return symBackend.SymbolicMixin

    def prettyStr(self, mx):
        return sp.pretty(mx.mx)

    def _extract_sympy_matrix(self, mx):
        return mx.mx if isinstance(mx, symBackend.MyMx) else mx

class HomReprMixin():
    def __init__(self, **kwds):
        super().__init__(**kwds)
        class Repr(ctrepr.MatrixRepresentationMixin, self.backendMixin(), reprHomogeneous.HCoordinatesMixin): pass

        self.repr = Repr()

    def asMatrix(self, ct):
        return self.repr.matrix_repr(ct)

    def matrixSize(self):
        return 4

class SpatialReprMixin():
    def __init__(self, **kwds):
        super().__init__(**kwds)

        class ReprMotion(ctrepr.MatrixRepresentationMixin, self.backendMixin(), reprSpatial.MotionVectorMixin): pass
        class ReprForce (ctrepr.MatrixRepresentationMixin, self.backendMixin(), reprSpatial.ForceVectorMixin): pass
        self.repr_as_motion = ReprMotion()
        self.repr_as_force  = ReprForce()

    def asMatrix(self, ct):
         # defaults to motion vectors; I could randomize the choice of motion/force
        return self.repr_as_motion.matrix_repr(ct)

    def asMotionTransform(self, ct):
        return self.repr_as_motion.matrix_repr(ct)

    def asForceTransform(self, ct):
        return self.repr_as_force.matrix_repr(ct)

    def matrixSize(self):
        return 6


class GenericTests:
    def test_primitiveTransformPolarity(self):
        motion = self.backend.generator.randomMotion()
        pose = motions.PoseSpec(pose=pBA, motion=motion)
        tr1  = toCoordinateTransform( pose, primitives_polarity=R_ct_T )
        tr2  = toCoordinateTransform( pose, primitives_polarity=T_ct_R )
        M1   = self.backend.asMatrix(tr1)
        M2   = self.backend.asMatrix(tr2)

        equal = self.backend.equal_matrix(M1, M2)
        self.assertTrue( equal )


    def test_extrinsicIntrinsic(self):
        '''Test about extrinsic and intrinsic rotations

        Extrinsic rotations (ie about fixed axes) are equivalent to intrinsic
        rotations (about moving axes) in the opposite order'''

        rots = self.backend.randomRotations()
        extrinsic = MotionSequence(rots,       MotionSequence.Mode.fixedFrame)
        intrinsic = MotionSequence(rots[::-1], MotionSequence.Mode.currentFrame)

        e_pose = motions.PoseSpec(pose=pBA, motion=extrinsic)
        i_pose = motions.PoseSpec(pose=pCB, motion=intrinsic)

        e_ct = toCoordinateTransform(e_pose)
        i_ct = toCoordinateTransform(i_pose)

        e_repr = self.backend.asMatrix(e_ct)
        i_repr = self.backend.asMatrix(i_ct)

        self.assertTrue( self.backend.equal_matrix(e_repr, i_repr) )

    def test_motionInversion(self):
        '''Test the inversion of a motion model

        The coordinate transform associated to the inverse of a motion M,
        should be the inverse of the transform associated to M.'''

        mot = self.backend.randomMotion()

        pose = motions.PoseSpec(pose=pBA, motion=mot)
        ipose= motions.inversePoseSpec( pose )

        A_ct_B = toCoordinateTransform(pose)
        B_ct_A = toCoordinateTransform(ipose)

        A_X_B = self.backend.asMatrix(A_ct_B)
        B_X_A = self.backend.asMatrix(B_ct_A)

        equal = self.backend.equal_matrix(self.backend.mult_matrix(A_X_B, B_X_A), self.backend.identity())
        self.assertTrue( equal )


    def test_twoTransformsFromOnePose(self):
        '''
        Test the creation of a transform and its inverse from the same pose.

        Given a single pose, two coordinate transforms with opposite polarity
        can be constructed; they should be the inverse of each other.
        '''
        mot = self.backend.randomMotion()
        pose= motions.PoseSpec(pose=pBA, motion=mot)

        A_ct_B = toCoordinateTransform(poseSpec=pose, polarity=R_ct_T)
        B_ct_A = toCoordinateTransform(poseSpec=pose, polarity=T_ct_R)

        self.assertTrue( A_ct_B.leftFrame  == B_ct_A.rightFrame )
        self.assertTrue( A_ct_B.rightFrame == B_ct_A.leftFrame )

        # now check that the API is consistent, and we can use the
        # 'right_frame' argument instead of 'polarity', to achieve the same transforms
        A_ct_B_ = toCoordinateTransform(poseSpec=pose, right_frame=frB)
        B_ct_A_ = toCoordinateTransform(poseSpec=pose, right_frame=frA)
        self.assertTrue( A_ct_B == A_ct_B_ )
        equals = (B_ct_A == B_ct_A_)
        self.assertTrue( equals )

        # Finally check that the matrix representation is consistent, one should
        # be the inverse of the other
        A_X_B = self.backend.asMatrix(A_ct_B)
        B_X_A = self.backend.asMatrix(B_ct_A)
        equals = self.backend.equal_matrix( self.backend.mult_matrix(A_X_B, B_X_A) , self.backend.identity() )
        self.assertTrue( equals )

    def test_poseInference(self):
        mot1 = self.backend.randomMotion()
        mot2 = self.backend.randomMotion()
        pose1 = motions.PoseSpec(pose=pBA, motion=mot1)
        pose2 = motions.PoseSpec(pose=pCB, motion=mot2)

        model = motions.PosesSpec(name='test', poses=[pose1, pose2])
        inspector = motions.ConnectedFramesInspector(model)
        self.assertTrue( inspector.hasRelativePose(frA, frC))

        posespec = inspector.getPoseSpec(targetFrame=frC, referenceFrame=frA)
        A_ct_B = toCoordinateTransform(pose1)
        B_ct_C = toCoordinateTransform(pose2)
        A_ct_C = toCoordinateTransform(posespec) # to be tested

        A_X_B = self.backend.asMatrix(A_ct_B)
        B_X_C = self.backend.asMatrix(B_ct_C)
        A_X_C = self.backend.asMatrix(A_ct_C)

        self.assertTrue( self.backend.equal_matrix(self.backend.mult_matrix(A_X_B, B_X_C),  A_X_C) )


class SpatialVectorTests:
    '''Tests specifically for the coordinate transforms for spatial vectors.
    '''

    def test_duality(self):
        '''Check the relation between trasforms for spatial motion/force vectors.

        The transpose of a transform for spatial motion vectors is equal to the
        trasform for force vectors in the opposite polarity'''
        mot    = self.backend.randomMotion()
        pose   = motions.PoseSpec(pose=pBA, motion=mot)
        A_ct_B = toCoordinateTransform(poseSpec=pose, polarity=R_ct_T) # CT from B to A
        B_ct_A = toCoordinateTransform(poseSpec=pose, polarity=T_ct_R) # CT from A to B

        A_SM_B = self.backend.asMotionTransform(A_ct_B)
        B_SF_A = self.backend.asForceTransform(B_ct_A)
        good = self.backend.equal_matrix(self.backend.transpose(A_SM_B), B_SF_A)
        if not good:
            logger.error( "\n" + self.backend.prettyStr(A_SM_B) )
            logger.error( "\n" + self.backend.prettyStr(B_SF_A) )

        self.assertTrue( good  )


class SymbolicBackendTests :
    '''Tests addressing specifically only the symbolic backend
    '''

    def test_freeSymbols(self):
        '''Check the consistency of the data structures holding the free symbols of a matrix.
        '''
        mot1 = self.backend.randomMotion()
        pose1 = motions.PoseSpec(pose=pBA, motion=mot1)
        A_ct_B = toCoordinateTransform(pose1)

        A_X_B = self.backend.asMatrix(A_ct_B)

        setFromCTMetadata = set()
        setFromCTMetadata.update(
            [argument.symbol for argument in A_X_B.variables],
            [argument.symbol for argument in A_X_B.parameters],
            [argument.symbol for argument in A_X_B.constants]
        )
        correct = ( setFromCTMetadata == A_X_B.mx.free_symbols )
        if not correct:
            logger.error("Symbols from the CT metadata: {0}\nSymbols from the Sympy matrix: {1}"
                         .format( str(setFromCTMetadata), str(A_X_B.mx.free_symbols)) )
        self.assertTrue( correct )


class TransformMetadataTests :
    '''
    Check the consistency of the metadata of a transform
    '''

    def test_freeSymbols(self):
        '''
        The symbols used in the creation of a transform shall appear in its metadata
        '''

        v1 = numeric_argument.Variable(name="v1")
        p1 = numeric_argument.Parameter(name="p1")
        steps = [
            MotionStep(MotionStep.Kind.Rotation, motions.Axis.X,
                numeric_argument.Expression( v1 ) ),
            MotionStep(MotionStep.Kind.Translation, motions.Axis.X, 0.1234),
            MotionStep(MotionStep.Kind.Translation, motions.Axis.Y,
                numeric_argument.Expression( p1, 3*p1.symbol ) )
        ]
        mot1 = MotionSequence(steps)
        pose1 = motions.PoseSpec(pose=pBA, motion=mot1)
        A_ct_B = toCoordinateTransform(pose1)
        ctinfo = ctmetadata.TransformMetadata(A_ct_B)

        self.assertEqual(ctinfo.variables, {v1})
        self.assertEqual(ctinfo.parameters, {p1})

    def test_symbolExpressions(self):
        '''
        The symbolic expressions used in the definition of a transform shall
        appear in the metadata.
        '''

        v1 = numeric_argument.Variable(name="v1")
        p1 = numeric_argument.Parameter(name="p1")
        p1_expr1 = numeric_argument.Expression( p1, 3*p1.symbol )
        p1_expr2 = numeric_argument.Expression( p1, p1.symbol/(-2) )
        c1 = numeric_argument.Constant(name="c1", value = -1.05)
        c1_expr1 = numeric_argument.Expression( c1, c1.symbol/2 )
        steps = [
            MotionStep(MotionStep.Kind.Rotation, motions.Axis.X,
                numeric_argument.Expression( v1 ) ),
            MotionStep(MotionStep.Kind.Translation, motions.Axis.X, 0.1234),
            MotionStep(MotionStep.Kind.Translation, motions.Axis.Y, p1_expr1),
            MotionStep(MotionStep.Kind.Translation, motions.Axis.Y, p1_expr2),
            MotionStep(MotionStep.Kind.Rotation, motions.Axis.Z, c1_expr1)
        ]
        mot1 = MotionSequence(steps)
        pose1 = motions.PoseSpec(pose=pBA, motion=mot1)
        A_ct_B = toCoordinateTransform(pose1)
        varss, parss, constss = ctmetadata.symbolicArgumentsOf(A_ct_B)

        # Note the minus (to get the plus), because we expect the expressions
        # in the metadata to be without the minus, even when original expression
        # does have it
        self.assertEqual( [e.symbolicExpr for e in parss[p1]], [p1_expr1.expr, -p1_expr2.expr] )
        self.assertEqual( [e.symbolicExpr for e in constss[c1]], [c1_expr1.expr] )


class NumericHomogeneous (NumericMixin , HomReprMixin):   pass
class SymbolicHomogeneous(SymbolicMixin, HomReprMixin):   pass
class NumericSpatial (NumericMixin , SpatialReprMixin): pass
class SymbolicSpatial(SymbolicMixin, SpatialReprMixin): pass


class GenericTestNumericHomogeneous(unittest.TestCase, GenericTests):
    def setUp(self):
        self.backend = NumericHomogeneous()

class GenericTestNumericSpatial    (unittest.TestCase, GenericTests):
    def setUp(self):
        self.backend = NumericSpatial()

class GenericTestSymbolicHomogeneous(unittest.TestCase, GenericTests):
    def setUp(self):
        self.backend = SymbolicHomogeneous()

class GenericTestSymbolicSpatial(unittest.TestCase, GenericTests):
    def setUp(self):
        self.backend = SymbolicSpatial()

class TestSpatialNumeric(SpatialVectorTests, unittest.TestCase):
    def setUp(self):
        self.backend = NumericSpatial()

class TestSpatialSymbolic(SpatialVectorTests, unittest.TestCase):
    def setUp(self):
        self.backend = SymbolicSpatial()

class TestSymbolicHomogeneous(unittest.TestCase, SymbolicBackendTests):
    def setUp(self):
        self.backend = SymbolicHomogeneous()

class TestTransformMetadata(unittest.TestCase, TransformMetadataTests): pass


def getDebugSample(numMixin, reprMixin):
    class Mixin(numMixin, reprMixin): pass

    obj = Mixin()
    mot    = obj.randomMotion()
    pose   = motions.PoseSpec(pose=pBA, motion=mot)
    A_ct_B = toCoordinateTransform(poseSpec=pose, polarity=R_ct_T)
    A_X_B  = obj.asMatrix(A_ct_B)
    return mot, pose, A_ct_B, A_X_B


if __name__ == '__main__':
    unittest.main()


