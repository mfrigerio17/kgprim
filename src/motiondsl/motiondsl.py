'''
The actual implementation of the MotionDSL (`motiondsl`), using
[textX](https://github.com/textX/textX).

The module-level member `dsl` is the default instance of the `MotionDSL` class.
Normally, you will only need this preallocated instance to load a document in
the MotionDSL format.

For example:

    import os, sys
    import motiondsl.motiondsl as motdsl

    def main():
        if len(sys.argv) > 1 :
            ifile = sys.argv[1]
        else :
            ifile = os.path.join( os.path.dirname(__file__), 'sample.motdsl')

        # Load the motions-model from the input file
        motionsModel = motdsl.dsl.modelFromFile(ifile)

        print("Motions (poses) model name: ", motionsModel.name)

        # Convert the motions-model to a pose-specification model
        posesModel = motdsl.toPosesSpecification(motionsModel)
'''

import sympy as sp
import os
import textx
import kgprim.core as primitives
from kgprim.values import Variable
from kgprim.values import Parameter
from kgprim.values import Constant
from kgprim.values import MyPI
from kgprim.values import Expression
from kgprim.motions import Axis
from kgprim.motions import MotionStep
from kgprim.motions import MotionSequence
from kgprim.motions import PoseSpec
from kgprim.motions import PosesSpec


def _argValue(arg):
    if type(arg) == float :
        return arg
    else:
        return Expression(arg)

class MotionDSL:
    def __init__(self):
        here = os.path.dirname(os.path.abspath(__file__))
        self.mm = textx.metamodel_from_file(here+"/motiondsl.tx")
        obj_processors = {
            'PILiteral': lambda _ : MyPI.instance(),
            'Variable' : lambda x : Variable(name=x.name),
            'Parameter': lambda x : Parameter(name=x.name),
            'UserConstant': lambda x : Constant(name=x.name, value=x.value),
            'RefToConstant': lambda x : Constant(name=x.actual.name, value=x.actual.value),

            # the following result in a float or an Expression object
            'PlainExpr' : lambda e: (-1 if e.minus else 1) * _argValue( e.arg ),
            'MultExpr'  : lambda e: e.mult * _argValue( e.arg ),
            'DivExpr'   : lambda e: (-1 if e.minus else 1)* _argValue( e.arg ) / e.div,

            'Trx' : lambda m : MotionStep(MotionStep.Kind.Translation, Axis.X, m.expr),
            'Try' : lambda m : MotionStep(MotionStep.Kind.Translation, Axis.Y, m.expr),
            'Trz' : lambda m : MotionStep(MotionStep.Kind.Translation, Axis.Z, m.expr),
            'Rotx': lambda m : MotionStep(MotionStep.Kind.Rotation,    Axis.X, m.expr),
            'Roty': lambda m : MotionStep(MotionStep.Kind.Rotation,    Axis.Y, m.expr),
            'Rotz': lambda m : MotionStep(MotionStep.Kind.Rotation,    Axis.Z, m.expr)
        }
        self.mm.register_obj_processors( obj_processors )


    def modelFromFile(self, file):
        '''
        The MotionDSL model represented by the given conforming document.

        Arguments:
          - `file`: path of a MotionDSL document (i.e. a text file)
        '''
        return self.mm.model_from_file(file)


dsl = MotionDSL()

__mode_map = {
    "currentFrame" : MotionSequence.Mode.currentFrame,
    "fixedFrame"   : MotionSequence.Mode.fixedFrame
}


def toPosesSpecification(dslmodel):
    '''
    Convert a MotionDSL model into a `kgprim.motions.PosesSpec` instance.

    One typically gets a MotionDSL model by loading it from an input document;
    see `MotionDSL.modelFromFile()`
    '''
    mode = __mode_map[ dslmodel.convention ]
    poses = []
    for m in dslmodel.motions :
        ref  = primitives.Frame(m.start.name)
        tgt  = primitives.Frame(m.end.name)
        pose = primitives.Pose(target=tgt, reference=ref)
        motSeq = MotionSequence( m.primitiveMotions, mode)
        poses.append( PoseSpec(pose=pose, motion=motSeq) )

    return PosesSpec(name=dslmodel.name, poses=poses)



__ser_map = {
    MotionStep.Kind.Translation : {
        Axis.X : 'trx',
        Axis.Y : 'try',
        Axis.Z : 'trz',
    },
    MotionStep.Kind.Rotation : {
        Axis.X : 'rotx',
        Axis.Y : 'roty',
        Axis.Z : 'rotz',
    },
}

def poseSpecToMotionDSLSnippet(poseSpec):
    tgtF = poseSpec.pose.target
    refF = poseSpec.pose.reference
    path = ""
    for seq in poseSpec.motion.sequences :
        for step in seq.steps :
            path = path + ' {step}({amount})'.format(step=__ser_map[step.kind][step.axis], amount=step.amount.__str__())
    ret = '{ref} -> {tgt} : {path}'.format(ref=refF.name, tgt=tgtF.name, path=path)
    return ret

