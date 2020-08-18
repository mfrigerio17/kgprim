from collections import OrderedDict

from kgprim.motions import MotionStep
import kgprim.values as numeric_argument


class TransformMetadata:
    '''
    Metadata of a single coordinate transform model.

    A metadata object contains the set of variables, parameters and constants
    which are part of the transform, and also two flags to tell whether the
    transform is parametric or constant.
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
    '''
    Metadata for a whole transforms-model (that is, a set of transforms)
    '''

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
    '''
    Wraps a `kgprim.values.Expression` after stripping any leading minus.
    Expressions like `2*x` and `-2*x` would lead to two instances
    of this class that compare equal.

    Arguments:
    - `ctPrimitive` a primitive transform having an expression as argument
    '''

    def __init__(self, ctPrimitive ):
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
    def symbolicExpr(self):
        '''The underlying Sympy expression'''
        return self.expression.expr

    def isRotation(self): return self.rotation

    def isIdentity(self):
        return (self.expression.arg.symbol == self.expression.expr)

    def __eq__(self, rhs):
        return (self.expression == rhs.expression)
    def __hash__(self) :
        return 7*hash(self.expression)


def symbolicArgumentsOf(coordinateTransform):
    '''
    The variables, parameters and constants the given transform depends on.

    The argument must be a `ct.models.CoordinateTransform` instance (or a
    `ct.models.PrimitiveCTransform`).

    The function returns three ordered dictionaries, with keys being
    respectively the variables, parameters and constants of the given transform
    (`kgprim.values.Variable`, `kgprim.values.Parameter`, and
    `kgprim.values.Constant`). Occurrences of pi and raw floating point values
    are never included.
    The keys are stored in the same order as they appear in the transform (e.g.
    if the transform is a rotation of r radians followed by a translation of t
    meters, r will appear before t).

    The values in the dictionaries are sets, containing all the unique
    expressions having the corresponding key as an argument. Expressions
    differing only for the sign are considered the same.
    For example, if the transform is defined as `rotx(2r) roty(3r) rotz(-2r)`,
    the set corresponding to `r` will contain `2r` and `3r`.
    '''
    varss = OrderedDict()
    pars  = OrderedDict()
    consts= OrderedDict()
    for pct in coordinateTransform.primitives :
        if isinstance(pct.amount, numeric_argument.Expression) :
            arg = pct.amount.arg
            rtexpr = UniqueExpression(pct)

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






