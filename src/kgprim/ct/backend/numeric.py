import math
import numpy as np
import kgprim.values as myexpr

class NumericMixin:
    def sin(self, arg):
        return math.sin(arg)

    def cos(self, arg):
        return math.cos(arg)

    def identity(self):
        return np.identity( self.matrixSize )

    def matrix_repr(self, ct):
        mx = self.identity()
        for p in ct.primitives :
            amount = p.amount
            if isinstance(amount, myexpr.Expression) :
                try:
                    amount = amount.evalf()
                except RuntimeError as e:
                    raise RuntimeError('Could not compute numeric matrix representation: ' + e.msg())
            mx = mx @ self.matrix[p.kind](p.axis, p.polarity, amount)
        return mx
    # self.matrix comes from the MatrixRepresentationMixin

