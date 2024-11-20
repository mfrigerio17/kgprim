import os, sys
import motiondsl.motiondsl as motdsl

from kgprim.core import Frame
import kgprim.motions
import kgprim.ct.frommotions
import kgprim.ct.repr.mxrepr
import kgprim.ct.metadata



if len(sys.argv) > 1 :
    ifile = sys.argv[1]
else :
    ifile = os.path.join( os.path.dirname(__file__), 'model.motdsl')

# Load the DSL model from the input file
motionsModel = motdsl.dsl.modelFromFile(ifile)

print("Motions (poses) model name: ", motionsModel.name)

# Convert the DSL model to the pose-specification model implemented in
# kgprim.motions
posesModel = motdsl.toPosesSpecification(motionsModel)

inspector = kgprim.motions.ConnectedFramesInspector(posesModel)

def getAll(tgtFrame, refFrame):
    pose = inspector.getPoseSpec(targetFrame=Frame(tgtFrame), referenceFrame=Frame(refFrame))
    ct   = kgprim.ct.frommotions.toCoordinateTransform(pose)
    mx   = kgprim.ct.repr.mxrepr.hCoordinatesSymbolic(ct)

    metadata = kgprim.ct.metadata.TransformMetadata(ct)
    return pose, ct, mx, metadata

