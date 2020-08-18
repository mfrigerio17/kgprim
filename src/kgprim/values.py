'''
A set of types to represent explicitly variables, parameters and constants.

The types do not really implement any particular behaviour, but
are mere placeholders provided for modeling purposes. Instances can be used in
alternative to floats, for numerical attributes (such as the `amount` of a
`kgprim.motions.MotionStep` object).

Conceptually, the relative rate of change of a numerical attribute determines
whether it is a variable, a parameter, or a constant. It is a modelling choice
to use a class or another.

Internally, a Sympy symbol is used, which is accessible via the `symbol`
property. The `expr` property also returns the Sympy symbol; it is provided
for uniformity with the `Expression` class, where `expr` resolves to the actual
Sympy expression.
'''

import sympy as sp

class Variable:
    '''
    An explicit representation of a named variable.

    This class is implemented as a simple wrapper of a Sympy symbol.
    '''

    def __init__(self, name, symbol=None):
        self.name_ = name
        if symbol is not None :
            self.symbol_ = symbol
        else :
            self.symbol_ = sp.Symbol(name=name)
    @property
    def name(self):
        return self.name_
    @property
    def symbol(self):
        '''The Sympy symbol used internally'''
        return self.symbol_

    @property
    def expr(self):
        return self.symbol
    @property
    def constant(self):
        return False

    def __eq__(self, rhs):
        return (isinstance(rhs, Variable)
                and (self.name == rhs.name)
                and (self.symbol  == rhs.symbol))
    def __hash__(self) :
        return 47*hash(self.name) + 93*hash(self.symbol)
    def __str__(self):
        return "var:{n}".format(n=self.name)
    def __repr__(self):
        return self.__str__()


class Parameter:
    '''
    An exlicit representation of a named parameter, with an optional default
    value.

    Like `Variable`, this class is also a simple wrapper of a Sympy symbol.
    '''

    def __init__(self, name, symbol=None, defValue=None):
        self.name_   = name
        self.symbol_ = symbol or sp.Symbol(name=name)
        self.defaultValue = defValue

    @property
    def name(self):
        return self.name_

    @property
    def symbol(self):
        '''The Sympy symbol used internally'''
        return self.symbol_
    @property
    def expr(self):
        return self.symbol
    @property
    def constant(self):
        return False

    def __eq__(self, rhs):
        return (isinstance(rhs, Parameter)
                and (self.name == rhs.name)
                and (self.symbol  == rhs.symbol))
    def __hash__(self) :
        return 101*hash(self.name) + 11*hash(self.symbol)
    def __str__(self):
        return "param:{n}".format(n=self.name)
    def __repr__(self):
        return self.__str__()



class _ConstantSymbol(sp.NumberSymbol):
    # For internal use.
    # Inherit from sympy.NumberSymbol to create a generic symbol with a constant
    # value. Don't really know whether this is correct/complete, but it seems it
    # does the right thing. Not very much documentation out there about how to
    # create a custom constant symbol

    __slots__ = ['name', 'value']

    def __new__(cls, name, value):
        self = super().__new__(cls)
        self.name  = name
        self.value = sp.Float(value)
        return self

    def _as_mpf_val(self, prec):
        return self.value._as_mpf_val(prec)

    def _sympystr(self, printer):
        return printer.doprint(sp.Symbol(self.name))

    def __eq__(self, rhs):
        return (isinstance(rhs, _ConstantSymbol)
                and (self.name  == rhs.name)
                and (self.value == rhs.value))
    def __hash__(self) :
        return 113*hash(self.name) + 29*hash(self.value)


class Constant:
    '''
    A wrapper of a named symbol with a constant floating point value.
    '''

    def __init__(self, name, value):
        self._symbol= _ConstantSymbol(name, value)
        self._name  = name
        self._value = value

    @property
    def name(self):
        return self._name
    @property
    def symbol(self):
        '''The Sympy symbol used internally'''
        return self._symbol
    @property
    def expr(self):
        return self.symbol
    @property
    def value(self):
        return self._value
    @property
    def constant(self):
        return True

    def __eq__(self, rhs):
        return (isinstance(rhs, Constant)
                and (self._name  == rhs._name)
                and (self._value == rhs._value))
    def __hash__(self) :
        return 107*hash(self._name) + 13*hash(self._value)

class MyPI:
    '''
    A singleton representing the constant pi
    '''

    __inst = None

    def __init__(self):
        self.name_ = "pi"

    @property
    def name(self):
        return self.name_
    @property
    def symbol(self):
        '''The Sympy object used internally'''
        return sp.pi
    @property
    def expr(self):
        return self.symbol
    @property
    def constant(self):
        return True
    @property
    def value(self):
        return sp.pi.evalf()

    @staticmethod
    def instance():
        if MyPI.__inst is None:
            MyPI.__inst = MyPI()
        return MyPI.__inst

class Expression:
    '''
    A wrapper of simple expressions involving either a `Variable`, `Parameter`
    or `Constant`. The expression can have only one argument.

    The actual symbolic expression like '3 * var' or 'pi/2' is stored internally
    as a Sympy expression.
    '''

    def __init__(self, argument, sympyExpr=None):
        '''
        Parameters:
          - `argument`: an instance of either `Variable`, `Parameter` or
            `Constant`, which is the argument of the expression.
          - `sympyExpr` : the actual, full, Sympy expression; if None, this
             instance will represent the identity expression.
        The only free symbol in the given `sympyExpr` must be the same as
        `argument.symbol`, otherwise a `RuntimeError` is raised.
        '''
        if sympyExpr is not None :
            if len(sympyExpr.free_symbols) > 0: # ==0 only for pi or other constants
                if sympyExpr.free_symbols.pop() != argument.symbol :
                    raise RuntimeError('Inconsistent arguments')
            self.expression = sympyExpr
        else :
            self.expression = argument.expr
        self.argument = argument

    @property
    def expr(self):
        '''The underlying Sympy expression'''
        return self.expression
    @property
    def arg(self):
        '''The single argument of this expression.'''
        return self.argument

    def evalf(self):
        '''The floating point value of this expression, if it is constant'''
        if not self.constant() :
            raise RuntimeError('Cannot evaluate to float a non constant expression')
        return self.expression.evalf( subs={self.argument.symbol : self.argument.value})

    def constant(self):
        '''Whether this expression has a constant value or not'''
        return self.argument.constant

    def __neg__(self):
        return Expression(self.argument, -self.expr)

    def __mul__(self, rhs):
        return Expression(self.argument, self.expr*rhs)

    def __truediv__(self, rhs):
        return Expression(self.argument, self.expr/rhs)

    def __eq__(self, rhs):
        return (isinstance(rhs, Expression)
                and (self.arg == rhs.arg)
                and (self.expr== rhs.expr))
    def __hash__(self) :
        return 31*hash(self.arg) + 93*hash(self.expr)
    def __str__(self):
        return self.expr.__str__()
    def __repr__(self):
        return "expr:"+self.__str__()

    __rmul__ = __mul__



__evalf = {
    Expression: lambda E: E.evalf(),
    float:      lambda f: f
}

def toFloat(expr):
    return __evalf[expr.__class__](expr)
