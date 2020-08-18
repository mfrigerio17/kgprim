'''
Functions to convert rigid-motion models (`kgprim.motions`) into
coordinate-transform models.

A sequence of rigid motions specifies the relative pose between two
Cartesian frames A and B. A corresponding coordinate-transform is an object that
maps between A/B-coordinate vectors.
'''


import logging
from kgprim.ct import models as ct
from kgprim import motions as mot

logger = logging.getLogger(__name__)


ctOnRight = ct.TransformPolarity.movedFrameOnTheRight
ctOnLeft  = ct.TransformPolarity.movedFrameOnTheLeft



# The following '__xxx' methods are for internal use.

# They embed the logic to convert a sequence of motion steps to a sequence of
# primitive coordinate transforms, such that the composition of these transforms
# is the total transform associated with the given motion, **with
# `movedFrameOnTheRight` polarity**.

# Whenever the user asks for the opposite polarity (see public functions below),
# we simply reverse the motion specification, and then rely again on these
# private functions.

# We have four functions for the four combinations of the attributes that
# matter: the `mode` of the motion steps, and the `polarity` of the primitive
# transforms. Again, the `polarity` of the desired composite transforms is dealt
# with in the public conversion function (`toCoordinateTransform`), where the
# motion specification is possibly inverted before calling these functions.

# So, yes, in principle, we actually have three binary attributes required for
# unambiguous specification, and thus 8 cases in total.

def __currentRight(motion):
    return [ ct.PrimitiveCTransform(m, ctOnRight) for m in motion.steps ]

def __currentLeft(motion):
    return [ ct.PrimitiveCTransform( -m , ctOnLeft)  for m in motion.steps ]

def __fixedRight(motion):
    a = [ ct.PrimitiveCTransform(tr, ctOnRight) for tr in motion.translations()]
    b = [ ct.PrimitiveCTransform(tr, ctOnRight) for tr in reversed(motion.rotations())]
    return a + b

def __fixedLeft(motion):
    a = [ ct.PrimitiveCTransform( -tr, ctOnLeft) for tr in motion.translations()]
    b = [ ct.PrimitiveCTransform( -tr, ctOnLeft) for tr in reversed(motion.rotations())]
    return a + b

# collect the handlers above in a dictionary, for vectorization
__motionToTransformsSequence = {
    ctOnRight : {
        mot.MotionSequence.Mode.currentFrame : __currentRight,
        mot.MotionSequence.Mode.fixedFrame   : __fixedRight
    },
    ctOnLeft : {
        mot.MotionSequence.Mode.currentFrame : __currentLeft,
        mot.MotionSequence.Mode.fixedFrame   : __fixedLeft
    }
}



def __make_ct(left_frame, right_frame, motion_sequences, primitives_polarity):
    primitives = []
    for sequence in motion_sequences :
        primitives += __motionToTransformsSequence[primitives_polarity][sequence.mode](sequence)
    return ct.CoordinateTransform(left_frame, right_frame, primitives)



def toCoordinateTransform(
        poseSpec,
        right_frame = None,
        polarity = ctOnRight,
        primitives_polarity = ctOnRight):
    '''
    Convert a `kgprim.motions.PoseSpec` into a
    `kgprim.ct.models.CoordinateTransform` object.

    The pose of T (target) relative to R (reference) is converted by default to
    the transform from T coordinates to R coordinates, R_X_T. To get
    the opposite transform, pass `right_frame` equal to R; alternatively, pass
    `polarity` equal to `movedFrameOnTheLeft` (see
    `kgprim.ct.models.TransformPolarity`).

    If `right_frame` is equal to one of the frames referenced by the pose, the
    `polarity` argument is ignored.
    '''
    #TODO checks on the arguments
    onTheRight = True
    if right_frame != None :
        onTheRight = (right_frame==poseSpec.pose.target)
    else :
        # check the polarity argument only if `right_frame` was not passed
        onTheRight = (polarity==ctOnRight)

    if onTheRight :
        # Default case, we want the R_X_T coordinate transform
        sequences  = poseSpec.motion.sequences
        leftFrame  = poseSpec.pose.reference  # R
        rightFrame = poseSpec.pose.target     # T
    else :
        sequences = mot.reverse(poseSpec.motion).sequences
        leftFrame  = poseSpec.pose.target
        rightFrame = poseSpec.pose.reference

    return __make_ct(leftFrame, rightFrame, sequences, primitives_polarity)


def motionsToCoordinateTransforms(
        posesModel,
        whichTransforms=None,
        retModelName=None,
        primitivesPolarity=ctOnRight):
    '''
    Create a model with the requested coordinate transforms, from a pose
    specification model.

    Keyword arguments:

      - `posesModel`: an instance of `kgprim.motions.PosesSpec` - the source
        information
      - `whichTransforms`: a list of `kgprim.ct.models.CoordinateTransformPlaceholder`,
        which specifies which transforms should be calculated
      - `retModelName`: the name (string) of the returned object; defaults to the
        same name of the input model
      - `primitivesPolarity`: one of `kgprim.ct.models.TransformPolarity`;
        ignore if in doubt

    Return a `CTransformsModel` object, whose field `transforms` is a list
    ordered like the input list `whichTransforms`. If `whichTransforms` is
    None, the default transforms will be returned: these are the A_X_B
    transforms for each input motion A-->B.

    '''
    retModelName = retModelName or posesModel.name
    if whichTransforms is None :
        return __convertModel(posesModel, retModelName)
    transforms = []
    inspector = mot.ConnectedFramesInspector(posesModel)
    for whichone in whichTransforms :
        poseSpec = inspector.getPoseSpec(targetFrame=whichone.leftFrame, referenceFrame=whichone.rightFrame)
        if poseSpec is None :
            logger.warning("Could not determine relative pose between '{0}' and '{1}'".format(whichone.leftFrame, whichone.rightFrame))
        else :
            myct = toCoordinateTransform(poseSpec, right_frame=whichone.rightFrame, primitives_polarity=primitivesPolarity)
            transforms.append(myct)
    return ct.CTransformsModel(retModelName, transforms)


def __convertModel(
        posesModel, retModelName,
        mode=ctOnRight,
        primitivesPolarity=ctOnRight):
    '''
    Create the default coordinate transforms model from a pose specification
    model.

    Returns a `kgprim.ct.models.CTransformsModel`.

    For each motion A-->B in `posesModel`, the returned transforms model
    will contain either the A_X_B or B_X_A transform, depending on `mode`.
    '''

    transforms = []
    for pose in posesModel.poses :
        transforms.append(
            toCoordinateTransform(pose, None, mode, primitives_polarity=primitivesPolarity) )

    return ct.CTransformsModel(retModelName, transforms)



