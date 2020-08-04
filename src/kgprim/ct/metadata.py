from collections import OrderedDict

from kgprim.motions import MotionStep
import kgprim.values as numeric_argument


class TransformMetadata:
    '''
    Metadata of a single coordinate transform
    '''

    def __init__(self, coordinateTransform):
        self.vars, self.pars, self.consts =\
                               symbolicArgumentsOf(coordinateTransform)
        self.ct = coordinateTransform
        self.parametric = (len(self.pars)>0)
        self.constant   = (len(self.vars)==0 and len(self.pars)==0)

    @property
    def name(self): return str(self.ct)


class TransformsModelMetadata:
    def __init__(self, ctmodel):
        variables    = OrderedDict()
        parameters   = OrderedDict()
        constants    = OrderedDict()
        transforms = []
        def add(container, argument, expressions):
            if argument not in container.keys():
                container[ argument ] = expressions
            else :
                container[ argument ].update( expressions )

        for transf in ctmodel.transforms :
            tinfo = TransformMetadata(transf)
            for var, expressions in tinfo.vars.items() :
                add( variables, var, expressions )
                #rotOrTr(tinfo, var)
            for par, expressions in tinfo.pars.items() :
                add( parameters, par, expressions )
#                     if rotOrTr(tinfo, par) : #it is a rotation
#                         rotationPars.append( par )
#                     else :
#                         translationPars.append( par )
            for cc, expressions in tinfo.consts.items() :
                add( constants, cc, expressions )
                #    rotOrTr(tinfo, cc)
            transforms.append( tinfo )

        self.ctModel = ctmodel
        self.transformsMetadata = transforms
        self.variables  = variables
        self.parameters = parameters
        self.constants  = constants

    @property
    def name(self):   return self.ctModel.name

    def isParametric(self):
        return len(self.parameters)>0



class UniqueExpression:
    def __init__(self, ctPrimitive, coordinateTransform ):
        if not isinstance(ctPrimitive.amount, numeric_argument.Expression) :
            raise RuntimeError('Need to pass a transform with an Expression as argument')

        original = ctPrimitive.amount
        # Sympy specifics here... might not be very robust...
        # Essentially we want to isolate the same Expression but without any
        # '-' in front
        # We rely on the fact that the sympy epressions coming from an input
        # geometry model are not more complicated than 'coefficient * symbol'
        (mult, rest) = original.expr.as_coeff_mul()
        sympynew = abs(mult) * rest[0] # [0] here, assumption is that there is only one term other than the multiplier
        expression = numeric_argument.Expression(argument=original.arg, sympyExpr=sympynew)

        self.expression = expression
        self.rotation   = (ctPrimitive.kind == MotionStep.Kind.Rotation)

    @property
    def symbolicExpr(self): return self.expression.expr

    def isRotation(self): return self.rotation

    def isIdentity(self):
        return (self.expression.arg.symbol == self.expression.expr)

    def __eq__(self, rhs):
        return (self.expression == rhs.expression)
    def __hash__(self) :
        return 7*hash(self.expression)


def symbolicArgumentsOf(coordinateTransform):
    '''The set of variables, parameters and constants the given
    transform depends on.

    The argument must be a ct.models.CoordinateTransform instance (or a
    ct.models.PrimitiveCTransform).

    The returned containers are actually lists, as we want to preserve the
    order of the arguments, determined by the order of primitive
    transforms. However, the lists do not have any duplicate.

    The returned lists contain instances of vpc.vpc.Variable, vpc.vpc.Parameter,
    and vpc.vpc.Constant. Instances of vpc.vpc.MyPI and raw floating point
    numbers are not returned.
    '''
    varss = OrderedDict()
    pars  = OrderedDict()
    consts= OrderedDict()
    for pct in coordinateTransform.primitives :
        if isinstance(pct.amount, numeric_argument.Expression) :
            arg = pct.amount.arg
            rtexpr = UniqueExpression(pct, coordinateTransform)

            if isinstance(arg, numeric_argument.Variable) :
                if arg not in varss : varss[ arg ] = set()
                varss.get( arg ).add( rtexpr )
            elif isinstance(arg, numeric_argument.Parameter) :
                if arg not in pars : pars[ arg ] = set()
                pars.get( arg ).add( rtexpr )
            elif isinstance(arg, numeric_argument.Constant) :
                if arg not in consts : consts[ arg ] = set()
                consts.get( arg ).add( rtexpr )
    return varss, pars, consts






