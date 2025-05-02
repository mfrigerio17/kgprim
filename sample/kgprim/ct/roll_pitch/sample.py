'''
This sample demonstrates how to programmatically model a sequence of two
rotations about two different axes.

It refers to the problem of the representation of the orientation of a rigid
body undergoing "rolling" and "pitching" motion.

By using the types in the `kgprim` package, we can represent the motions (i.e.
the rotations) explicitly, and a model of one associated coordinate transform
can be derived automatically.

The example demonstrates how a different convention for the rotations, that is
whether they happen about fixed or moving axes, ultimately lead to a different
orientation, and thus a different matrix representation of such orientation.
'''

import kgprim.core as primitives
import kgprim.values as symbvalues
import kgprim.motions as mot
import kgprim.ct.frommotions as mot2ct
import kgprim.ct.repr.mxrepr as mxrepr

import sympy

# Roll and pitch angles are rotations about X and Y

roll  = symbvalues.Expression(symbvalues.Variable("roll"))
pitch = symbvalues.Expression(symbvalues.Variable("pitch"))

rx = mot.MotionStep(mot.MotionStep.Kind.Rotation, mot.Axis.X, roll)
ry = mot.MotionStep(mot.MotionStep.Kind.Rotation, mot.Axis.Y, pitch)

# It makes a difference whether the rotations happen about fixed or moving axes

extrinsic = mot.MotionSequence([rx, ry], mot.MotionSequence.Mode.fixedFrame)
intrinsic = mot.MotionSequence([rx, ry], mot.MotionSequence.Mode.currentFrame)


# A pose object, to give a name to the frames

world = primitives.Frame('W')
body  = primitives.Frame('B')
pose  = primitives.Pose(reference=world, target=body)
# that was the pose of the frame 'body' relative to the frame 'world'


# From symbolic-pose and motion sequence to pose-specification, and then to
# coordinate transform

extrinsic = mot.PoseSpec(pose, extrinsic)
intrinsic = mot.PoseSpec(pose, intrinsic)

extrinsic = mot2ct.toCoordinateTransform(extrinsic)
intrinsic = mot2ct.toCoordinateTransform(intrinsic)


# Get the matrix representation of the coordinate transforms.
# In fact, get the matrix representation of the individual factors (ie the
# primitive transforms that correspond to the motion steps), so that we can
# visualize the composition (product) explicitly

eR1 = mxrepr.rotationMatrixSymbolic( extrinsic.primitives[0] )
eR2 = mxrepr.rotationMatrixSymbolic( extrinsic.primitives[1] )

iR1 = mxrepr.rotationMatrixSymbolic( intrinsic.primitives[0] )
iR2 = mxrepr.rotationMatrixSymbolic( intrinsic.primitives[1] )

print("")
print("The coordinate transform from Body to World, after Body moved with roll and pitch rotations, has this form:\n")
print("Rotations about fixed axes (extrinsic):")
sympy.pprint( sympy.Eq(eR1.mx @ eR2.mx, sympy.MatMul(eR1.mx,eR2.mx)) )
print("\n")
print("Rotations about moving axes (intrinsic):")
sympy.pprint( sympy.Eq(iR1.mx @ iR2.mx, sympy.MatMul(iR1.mx,iR2.mx)) )
print("\n")


# Normally, you probably want the matrix representation of the whole transform
eR = mxrepr.rotationMatrixSymbolic( extrinsic )
iR = mxrepr.rotationMatrixSymbolic( intrinsic )

assert(eR.mx == eR1.mx @ eR2.mx)
assert(iR.mx == iR1.mx @ iR2.mx)
