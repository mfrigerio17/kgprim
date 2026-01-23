'''
These test cases really address the combined working of `kgprim.motions` and
`kgprim.ct.frommotions`, because it is hard to test the motions models
independently, without resorting to numerical representations.
'''

import unittest, logging

import kgprim.core    as primitives
import kgprim.motions as motions
import kgprim.values  as numeric_argument
from kgprim.motions import MotionSequence, MotionStep

import kgprim.ct.models as ctmodels
import kgprim.ct.metadata as ctmetadata
from kgprim.ct.frommotions import toCoordinateTransform

import test.ct.utils as testutils

logger = logging.getLogger(__name__)


# A couple of random frames/poses placeholders to be used in the tests

frA = primitives.Frame("A")
frB = primitives.Frame("B")
frC = primitives.Frame("C")

pBA = primitives.Pose(reference=frA, target=frB)
pCB = primitives.Pose(reference=frB, target=frC)

R_ct_T = ctmodels.TransformPolarity.movedFrameOnTheRight
T_ct_R = ctmodels.TransformPolarity.movedFrameOnTheLeft


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





class GenericTestNumericHomogeneous(unittest.TestCase, GenericTests):
    def setUp(self):
        self.backend = testutils.NumericHomogeneous()

class GenericTestNumericSpatial(unittest.TestCase, GenericTests):
    def setUp(self):
        self.backend = testutils.NumericSpatial()

class GenericTestSymbolicHomogeneous(unittest.TestCase, GenericTests):
    def setUp(self):
        self.backend = testutils.SymbolicHomogeneous()

class GenericTestSymbolicSpatial(unittest.TestCase, GenericTests):
    def setUp(self):
        self.backend = testutils.SymbolicSpatial()

class TestSpatialNumeric(unittest.TestCase, SpatialVectorTests):
    def setUp(self):
        self.backend = testutils.NumericSpatial()

class TestSpatialSymbolic(unittest.TestCase, SpatialVectorTests):
    def setUp(self):
        self.backend = testutils.SymbolicSpatial()

class TestSymbolicHomogeneous(unittest.TestCase, SymbolicBackendTests):
    def setUp(self):
        self.backend = testutils.SymbolicHomogeneous()

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


