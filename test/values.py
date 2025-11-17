import unittest
import math, sympy, random
import kgprim.values as values


class ValuesTests(unittest.TestCase):
    def test_variable_symbol_name(self):
        name = 'whatever'
        v = values.Variable(name)
        self.assertTrue( v.symbol.name == name )

    def test_constant_value(self):
        value = random.random()
        c = values.Constant(name="c", value=value)
        self.assertTrue( c.value == value )

        e = values.Expression(c)
        self.assertTrue( e.evalf() == value )

    def test_pi_expr_value(self):
        '''Test numerical evaluation of a PI expression'''
        coeff = random.random()
        pi = values.MyPI.instance()
        e = values.Expression(pi, pi.symbol * coeff)
        err = round( e.evalf() - math.pi*coeff, 6 )
        self.assertEqual( err, 0.0 )

    def test_no_evalf(self):
        '''Variables and Parameters do not evaluate to floats'''
        v = values.Variable('v')
        p = values.Parameter(name='p', defValue=0.0) # even if it has a default value

        e = values.Expression(v)
        self.assertRaises(RuntimeError, e.evalf)

        e = values.Expression(p)
        self.assertRaises(RuntimeError, e.evalf)

    def test_expression_attributes(self):
        '''Test consistency of the attributes of a `kgprim.values.Expression`'''

        name = "v1"
        v1 = values.Variable(name)
        e1 = values.Expression(v1)

        # construct a non-trivial expression of v1
        e2 = 3 * e1;

        s1 = sympy.Symbol(name)

        # Check that the argument of the new expression is still the same
        # Variable, and then check the Sympy attributes
        self.assertTrue( e2.argument == v1 )
        self.assertTrue( e2.argument.symbol == s1 )
        self.assertTrue( e2.expr == 3*s1 )

if __name__ == '__main__':
    unittest.main()
