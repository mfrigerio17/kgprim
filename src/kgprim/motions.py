'''
Rigid motion models: "primitive" motions like pure
translations/rotations, and sequences of them.

A sequence of rigid motions is really a specification of a relative pose
between Cartesian frames: the motions required to move from A to B identify
the pose of B relative to A. Conversely, the pose of B relative to A could be
_defined_ with a sequence of rigid motions that bring A to coincide with B.

Therefore, in this and related modules the term 'motion' and
'pose-specification' may be used as synonyms.
'''

from enum import Enum
from kgprim.core import Frame
from kgprim.core import Pose


class Axis(Enum):
    X=0
    Y=1
    Z=2

class MotionStep:
    '''
    A representation of a pure rotation/translation motion, about/along one
    Cartesian axis.

    Any instance also stores an `amount` member to quantify the magnitude of
    the step.
    '''
    class Kind(Enum):
        '''Either `Rotation` or `Translation`'''
        Rotation=0
        Translation=1

    def __init__(self, kind, axis, amount):
        self.kind   = kind
        self.axis   = axis
        self.amount = amount

    def __neg__(self):
        return MotionStep(self.kind, self.axis, - self.amount)

    __strbits = {
        Kind.Rotation    : "Rot",
        Kind.Translation : "Tr",
    }
    def __str__(self) :
        return MotionStep.__strbits[self.kind] + self.axis.name + "(" + str(self.amount) + ")"
    def __repr__(self): return self.__str__()

    def __eq__(self, rhs):
        return (isinstance(rhs, MotionStep)
               and self.kind == rhs.kind
               and self.axis == rhs.axis
               and self.amount == rhs.amount)
    def __hash__(self):
        return 7*hash(self.kind) + 13*hash(self.axis) + 17*hash(self.amount)

def translation(axis, amount): return MotionStep(MotionStep.Kind.Translation, axis, amount)
def rotation   (axis, amount): return MotionStep(MotionStep.Kind.Rotation   , axis, amount)



class MotionSequence:
    '''
    An ordered sequence of `MotionStep`s taking place according to
    the _same_ convention (see `MotionSequence.Mode`).

    A `MotionSequence` is a sequence of pure rotations/translations, in any
    order, plus an attribute telling how to interpret the sequence itself: see
    `Mode`.
    '''

    class Mode(Enum):
        '''
        The two possible ways of interpreting a sequence of motion steps.

        This is an enumeration with two items:

        - `currentFrame`: every motion step is taken with respect to the
           current, moving Cartesian frame
        - `fixedFrame`: the reference frame stands still, thus the `axis` of any
           motion step is always one of the fixed axes.
        '''
        currentFrame = 0
        fixedFrame   = 1

    def __init__(self, steps, mode=Mode.currentFrame):
        self.steps= steps
        self.mode = mode

    @property
    def sequences(self):
        '''
        A list containing only self.

        This property is implemented to emulate the behaviour of `MotionPath`, so
        that the two types can be used interchangeably.
        '''
        return [ self ]

    def translations(self):
        '''
        A list containing only the translations of this instance, in the same
        relative order.
        '''
        return [t for t in self.steps if t.kind == MotionStep.Kind.Translation]

    def rotations(self):
        '''
        A list containing only the rotations of this instance, in the same
        relative order.
        '''
        return [t for t in self.steps if t.kind == MotionStep.Kind.Rotation]



class MotionPath:
    '''
    A representation of a rigid motion, as a sequence of `MotionSequence`s.

    The point of this class is really to model a single sequence of motion
    steps (a "path") but to allow subsequences to follow a different convention
    (see `MotionSequence.Mode`).

    An instance can be constructed with a list of `MotionSequence` objects,
    or a list of `MotionPath` objects. In both cases, the objects are composed
    to form an individual descriptor.
    '''

    def __init__(self, sequences):

        # To make sure we internally store an homogeneous list of MotionSequence
        # objects, we must unwrap possible MotionPath objects given to this
        # constructor. When concatenating MotionPaths, we really want to
        # concatenate the MotionSequences stored internally. Composing
        # MotionPaths leads to another MotionPath whose sequence is the
        # composition of the sequences of the original MotionPaths

        self._sequences = []
        for motion in sequences :
            if isinstance(motion, MotionSequence) :
                self._sequences.append( motion )
            elif isinstance(motion, MotionPath ) :
                for subs in motion.sequences :
                    self._sequences.append( subs )
            else:
                raise RuntimeError("Unknonw motion type: " + str(type(motion)))

    @property
    def sequences(self):
        '''The list of `MotionSequences` this motion descriptor is comprised of.'''
        return self._sequences



def reverse(aMotion) :
    inverseSequences = []
    for seq in aMotion.sequences[::-1] :#reverse view
        if seq.mode == MotionSequence.Mode.currentFrame :
            steps = [ -step for step in seq.steps[::-1] ]
            inverseSequences.append( MotionSequence(steps, seq.mode) )
        else : # fixed-frame mode
            rot = seq.rotations()
            tr  = seq.translations()

            rot2 = [ -step for step in rot[::-1] ]
            tr2  = [ -step for step in tr[::-1] ]
            inverseSequences.append( MotionSequence(rot2, MotionSequence.Mode.fixedFrame) )
            inverseSequences.append( MotionSequence(tr2, MotionSequence.Mode.currentFrame) )

    return MotionPath(inverseSequences)


class PoseSpec:
    '''
    A relative Pose augmented with the corresponding motion description.

    A sequence of rigid motions is really a specification of a relative pose
    between Cartesian frames: the motions required to move from A to B identify
    the pose of B relative to A.
    '''

    def __init__(self, pose, motion):
        self._pose   = pose
        self._motion = motion
    @property
    def pose(self): return self._pose

    @property
    def motion(self): return self._motion



def inversePoseSpec(poseSpec):
    pose = Pose(target=poseSpec.pose.reference, reference=poseSpec.pose.target)
    motion = reverse(poseSpec.motion)
    return PoseSpec(pose, motion)



class PosesSpec:
    '''
    A simple named container for a list of `PoseSpec` instances.
    '''

    def __init__(self, name, poses):
        self.name = name
        self.poses = poses

    def mergeModel(self, otherModel, name=None):
        if name is None:
            name = self.name + '_' + otherModel.name
        poses = self.poses.copy() # A shallow copy
        poses.extend( otherModel.poses ) # only works for lists !
        return PosesSpec(name, poses)



import networkx as nx

class ConnectedFramesInspector:
    '''
    An inspector to determine which additional poses can be induced from an
    existing PosesSpec model.

    For example, if the model contains the pose of A relative to B, and A
    relative to C, it is obviously possible to infer the relation between B and
    C.
    '''
    def __init__(self, posesModel):
        self.posesModel = posesModel
        graph = nx.DiGraph()

        for poseSpec in posesModel.poses :
            pose   = poseSpec.pose
            motion = poseSpec.motion
            tgt  = pose.target
            ref  = pose.reference
            graph.add_edge( ref, tgt, motion=motion )
            graph.add_edge( tgt, ref, motion=reverse(motion) )

        self.graph = graph


    def hasRelativePose(self, frame1, frame2):
        if (frame1 not in self.graph) or (frame2 not in self.graph):
            return False
        return nx.has_path(self.graph, frame1, frame2)

    def getPoseSpec(self, targetFrame, referenceFrame):
        if not self.hasRelativePose(targetFrame, referenceFrame) :
            return None
        path = nx.shortest_path(self.graph, target=targetFrame, source=referenceFrame)
        if len(path) < 1:
            return None
        motions = []
        for v1,v2 in zip(path, path[1:]) :
            edgedata = self.graph.edges[v1,v2]
            motions.append(edgedata['motion'])

        pose = Pose(target=targetFrame, reference=referenceFrame)
        return PoseSpec(pose=pose, motion=MotionPath(motions))


