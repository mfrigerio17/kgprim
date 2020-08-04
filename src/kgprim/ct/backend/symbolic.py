import logging
import numpy
import sympy as sym

import kgprim.values as numeric_argument
import kgprim.ct.metadata as metadata

logger = logging.getLogger(__name__)


class SymbolicMixin:
    def sin(self, arg):
        return sym.sin(arg)

    def cos(self, arg):
        return sym.cos(arg)

    def identity(self):
        return sym.eye( self.matrixSize )

    def matrix_repr(self, ct):
        mx = self.identity()
        for p in ct.primitives :
            if isinstance(p.amount, float) :
                mx = mx @ self.matrix[p.kind](p.axis, p.polarity, p.amount)
            else:
                if not isinstance(p.amount, numeric_argument.Expression) :
                    raise RuntimeError("Unknown type for the 'amount' attribute of a primitive transform of '{0}'".format(str(ct)))
                mx = mx @ self.matrix[p.kind](p.axis, p.polarity, p.amount.expr)
        return MyMx(ct, mx)




class MyMx:
    def __init__(self, ctr, mx):
        self.mx  = mx
        self.ctr = ctr
        varss, pars, consts = metadata.symbolicArgumentsOf(ctr)
        self.variables = varss
        self.parameters= pars
        self.constants = consts

        self.setParametersValue( {p : (p.defaultValue or 0) for p in self.parameters } )

    def setParametersValue(self, values):
        if len(values.keys()) != len(self.parameters) :
            logger.warn("The count of given values does not match the count of parameters")
        subs = { par.symbol : values[par] for par in values.keys() }
        self.mxNoParams = self.mx.subs( subs )
        self.eval = sym.lambdify([v.symbol for v in self.variables if v is not None], self.mxNoParams, 'numpy')

    def setVariablesValue(self, **kwargs):
        if 'valueslist' in kwargs:
            values = kwargs['valueslist']
            if len(values) != len(self.variables) :
                logger.warning("The length of the values list does not match the variables list")
            return self.eval( *values )
        elif 'valuesdict' in kwargs:
            values = kwargs['valuesdict']
            if values.keys() != self.variables.keys() :
                logger.warning("The given values do not account for all the variables of this matrix")
            replacements = { var.symbol : values[var] for var in values }
            return sym.matrix2numpy(self.mxNoParams.evalf( subs=replacements ), dtype=numpy.float64)
        else:
            logger.warning("Unrecognized parameter, skipping")

    # The following make sure that this type behaves similarly to the 'mx'
    # member, which is a Sympy matrix. Note however that this class is not meant
    # for algebra, which should be redirected explicitly to the mx member.
    def __getattr__(self, name):
        return getattr(self.mx, name)
    def __getitem__(self, key):  # this one is for subscripts [i,j]
        return self.mx[key]

#     def __matmul__(self, other): # we don't do this, as the point of this class is not to do algebra


    def __str__(self):
        return self.mx.__str__()
