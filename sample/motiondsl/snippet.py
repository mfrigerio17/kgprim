# The MotionDSL main module
import motiondsl.motiondsl as mdsl

# To convert motions-models to coordinate-transform models
import kgprim.ct.frommotions as ct_from_m

# To get concrete matrix representations of a transform
import kgprim.ct.repr.mxrepr as mxrepr

from kgprim.ct.models import TransformPolarity as Polarity



pspec = mdsl.snippetToPoseSpec("fA -> fB : rotx(alpha) trz(c:TZ:3.41) trx(2.0 * c:TZ)")

ct = ct_from_m.toCoordinateTransform(pspec)
## alternatively:
# ct = ct_from_m.toCoordinateTransform(pspec, polarity=Polarity.movedFrameOnTheRight)  # default
# ct = ct_from_m.toCoordinateTransform(pspec, polarity=Polarity.movedFrameOnTheLeft)

mx = mxrepr.hCoordinatesSymbolic( ct )
## alternatives:
# mx = mxrepr.rotationMatrixSymbolic( ct )
# mx = mxrepr.spatialMotionSymbolic( ct )
# ...

## Can't request a numerical representation because the initial motion model
## depends on some symbols:
# mx = mxrepr.rotationMatrixNumeric( ct ) # exception


## Display the resulting matrix:
print("Matrix representation:", mx.mx)


# Demonstrate round-tripping
reconstructedSnippet = mdsl.poseSpecToMotionDSLSnippet(pspec)
print("Reconstructed Motion-DSL model:", reconstructedSnippet)
pspec2 = mdsl.snippetToPoseSpec(reconstructedSnippet)

print(pspec.motion.sequences[0].steps == pspec2.motion.sequences[0].steps)
