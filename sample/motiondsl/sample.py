import os, sys
import motiondsl.motiondsl as motdsl
import kgprim.ct.frommotions
import kgprim.ct.repr.mxrepr
import kgprim.ct.metadata


def main():
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

    # Get the coordinate transforms model from the motions model
    ctModel = kgprim.ct.frommotions.motionsToCoordinateTransforms(posesModel)
    for transf in ctModel.transforms :
        print("\n\nTransform: ", transf)
        varss, pars, _ = kgprim.ct.metadata.symbolicArgumentsOf(transf)
        print("\tParameters: ", pars.keys() )
        print("\tVariables: ", varss.keys() )

        H = kgprim.ct.repr.mxrepr.hCoordinatesSymbolic(transf)
        print("\tHomogeneous coordinates:\n", repr(H.mx))

    return ctModel


if __name__ == '__main__':
    main()
