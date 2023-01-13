import kgprim.core as primitives
import kgprim.motions as mot
import kgprim.ct.frommotions as mot2ct
import kgprim.ct.repr.mxrepr as mxrepr

# make a motion sequence, with two steps
rx  = mot.MotionStep(mot.MotionStep.Kind.Rotation,    mot.Axis.X, 0.5)
ty  = mot.MotionStep(mot.MotionStep.Kind.Translation, mot.Axis.Y, 1.1)
seq = mot.MotionSequence([rx, ty], mot.MotionSequence.Mode.currentFrame)

# make a dummy pose
fR   = primitives.Frame('R')
fT   = primitives.Frame('T')
pose = primitives.Pose(reference=fR, target=fT)

# augment the pose with the motion spec; this object models the fact that to
# go from 'R' to 'T' one has to take the motion steps defined above
poseSpec = mot.PoseSpec(pose, seq)

# convert it to a coordinate transform model; by default, this is the transform
# from 'T' coordinates to 'R' coordinates, i.e. R_X_T
ct = mot2ct.toCoordinateTransform(poseSpec)

# use the functors in the matrix-representation module to get actual matrices
H = mxrepr.hCoordinatesNumeric( ct )
R = mxrepr.rotationMatrixNumeric( ct )

print(H)
print(R)