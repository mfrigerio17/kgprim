import os, sys
import motiondsl.motiondsl as motdsl
import kgprim.values as numeric_argument


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

    # Display the individual motion steps of each pose specification
    for poseSpec in posesModel.poses :
        print("Pose {}".format(poseSpec.pose))
        for s in poseSpec.motion.sequences:
            print("\tsequence:")
            for st in s.steps:
                amount = st.amount
                if isinstance(amount, numeric_argument.Expression):
                    print("\t\tstep: {}\t- amount = {} (argument = {})".format(st, amount, amount.arg.name ))
                else:
                    print("\t\tstep: {}\t- amount = {}".format(st, amount))

    # Print infos about the parameters in the model
    for poseSpec in posesModel.poses :
        for s in poseSpec.motion.sequences:
            for st in s.steps:
                amount = st.amount
                if isinstance(amount, numeric_argument.Expression):
                    arg = amount.arg
                    if isinstance(arg, numeric_argument.Parameter):
                        print("Parameter '{}', def value = {}".format(arg, arg.defaultValue))


if __name__ == '__main__':
    main()
