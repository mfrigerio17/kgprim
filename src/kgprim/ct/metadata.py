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

    def __init__(self, coordinateTransform, customName=None):
        self.vars, self.pars, self.consts =\
                               symbolicArgumentsOf(coordinateTransform)
        self.ct = coordinateTransform
        self.parametric = (len(self.pars)>0)
        self.constant   = (len(self.vars)==0 and len(self.pars)==0)
        self._name      = customName or str(self.ct)

    @property
    def name(self): return self._name

    @property
    def is_parametric(self): return self.parametric

    @property
    def is_constant(self): return self.constant

    @property
    def is_dependent(self):
        '''Tell whether this transform depends on any Variable.'''
        return len(self.vars)>0

    @property
    def variables(self):
        '''
        Return a view of the set of Variables this transform depends on.
        The set is ordered. See the description of the keys of the dictionaries
        in `symbolicArgumentsOf()`.
        '''
        return self.vars.keys()

    @property
    def parameters(self):
        '''
        Return a view of the set of Parameters this transform depends on.
        The set is ordered. See the description of the keys of the dictionaries
        in `symbolicArgumentsOf()`.
        '''
        return self.pars.keys()

    @property
    def constants(self):
        '''
        Return a view of the set of Constants that appear in this transform.
        The set is ordered. See the description of the keys of the dictionaries
        in `symbolicArgumentsOf()`.
        '''
        return self.consts.keys()

    @property
    def variable_expressions(self):
        '''
        The dictionary with the variables and the corresponding expressions
        appearing in this transform.
        See `symbolicArgumentsOf()` for the format of the dictionary.
        '''
        return self.vars

    @property
    def parameter_expressions(self):
        '''
        The dictionary with the parameters and the corresponding expressions
        appearing in this transform.
        See `symbolicArgumentsOf()` for the format of the dictionary.
        '''
        return self.pars

    @property
    def constant_expressions(self):
        '''
        The dictionary with the constants and the corresponding expressions
        appearing in this transform.
        See `symbolicArgumentsOf()` for the format of the dictionary.
        '''
        return self.consts


class TransformsModelMetadata:
    '''
    Metadata for a whole transforms-model (that is, a set of transforms)
    '''

    def __init__(self, ctmodel, tfNamesMap=None):
        '''
        Arguments
          - `ctmodel`: the coordinate-transforms container, an instance of
            `models.CTransformsModel`
          - `tfNamesMap`: an optional dictionary with custom names for each
            transform in the given model. The dictionary is keyed with tuples
            with the left and right-frame (in this order) of the transform to
            be named.
        '''

        variables    = OrderedDict()
        parameters   = OrderedDict()
        constants    = OrderedDict()
        transforms = []
        def add(container, argument, expressions):
            if argument not in container.keys():
                container[ argument ] = expressions
            else :
                container[ argument ].update( expressions )

        names = tfNamesMap or {}
        for transf in ctmodel.transforms :
            name  = names.get( (transf.leftFrame, transf.rightFrame) ) # 'get' defaults to None
            tinfo = TransformMetadata(transf, customName=name)
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
    - `arg` a `kgprim.ct.models.PrimitiveCTransform` whose motion-step has an
      expression as argument; alternatively, a `kgprim.motions.MotionStep`
      object right away
    '''

    def __init__(self, arg ):
        try:
            src_expr = arg.amount # works for both PrimitiveCTransform and MotionStep

            # Sympy specifics here... might not be very robust...
            # Essentially we want to isolate the same Expression but without any
            # '-' in front
            # We rely on the fact that the sympy epressions coming from an input
            # geometry model are not more complicated than 'coefficient * symbol'.
            # Explicitly passing 'symbol' makes it work also when the
            # coefficient is a float rather than rational (e.g. "0.5*pi" as
            # opposed to "pi/2").

            (mult, rest) = src_expr.expr.as_coeff_mul( src_expr.arg.symbol )
            if len(rest) > 1 :
                raise RuntimeError("Could not separate the coefficient in expression {}".format(src_expr.expr))
            # we assume there is only one term other than the multiplier
            sympynew = abs(mult) * rest[0]
            expression = numeric_argument.Expression(argument=src_expr.arg, sympyExpr=sympynew)

            self.expression = expression
            self.rotation   = (arg.kind == MotionStep.Kind.Rotation)
        except AttributeError as e:
            raise ValueError("Incompatible argument type given to UniqueExpression()") from e

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

    The values in the dictionaries are also sorted containers, with all the
    unique expressions having the corresponding key as an argument. Expressions
    differing only for the sign are considered the same.
    For example, if the transform is defined as `rotx(2r) roty(3r) rotz(-2r)`,
    the container corresponding to `r` will contain `2r` and `3r`.
    '''
    varss = OrderedDict()
    pars  = OrderedDict()
    consts= OrderedDict()
    for pct in coordinateTransform.primitives :
        if isinstance(pct.amount, numeric_argument.Expression) :
            arg = pct.amount.arg
            rtexpr = UniqueExpression(pct)

        # Use ordered dictionaries with no values to emulate sorted sets.
        # Iteration over a dictionary itself (no keys() nor values() ) defaults
        # to iteration over the keys, so it would appear to be an ordered
        # sequence, with no duplicates, as I want.
            if isinstance(arg, numeric_argument.Variable) :
                if arg not in varss : varss[ arg ] = OrderedDict()
                varss.get( arg ) [rtexpr] = None
            elif isinstance(arg, numeric_argument.Parameter) :
                if arg not in pars : pars[ arg ] = OrderedDict()
                pars.get( arg ) [rtexpr] = None
            elif isinstance(arg, numeric_argument.Constant) :
                if arg not in consts : consts[ arg ] = OrderedDict()
                consts.get( arg ) [rtexpr] = None
    return varss, pars, consts






