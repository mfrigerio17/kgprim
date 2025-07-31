import unittest
import random, math

import kgprim.values as numeric_argument
import motiondsl.motiondsl as motiondsl

class ParametersTests(unittest.TestCase):
    def _very_first_argument(self, snippet):
        poseSpec = motiondsl.snippetToPoseSpec(snippet)
        return poseSpec.motion.sequences[0].steps[0].amount.argument

    def test_param_name(self):
        pname = "aparameter"
        param = self._very_first_argument(f"fA -> fB : rotx(p:{pname})")
        self.assertEqual(pname, param.name)

    def test_no_default_value(self):
        param = self._very_first_argument(f"fA -> fB : rotx(p:param1)")
        self.assertIsNone(param.defaultValue)

    def test_param_default_value(self):
        pvalue = random.random()
        ndigits = 4
        factor = pow(10,ndigits)
        defvalue = math.trunc(pvalue*factor) / factor
        param = self._very_first_argument(f"fA -> fB : rotx(p:param1[{defvalue:.{ndigits}}])")
        self.assertEqual(defvalue, param.defaultValue)

    def test_param_and_subsequent_reference(self):
        poseSpec = motiondsl.snippetToPoseSpec("fA->fB : rotx(p:param1[0.1]) roty(p:param1)")
        steps = poseSpec.motion.sequences[0].steps
        self.assertEqual( steps[0].amount.argument, steps[1].amount.argument )

    def test_param_unique_default_value(self):
        '''All the instances that refer to the same logical parameter, are
        expected to have the same default value. The value must be the first
        default value given in the input model.'''

        expectedDefValue = 0.143
        model = '''
Model aTest
Convention = currentFrame
fA->fB : rotx(p:p1) roty(p:p1[{pval:.3}])
fB->fC : rotz(p:p1[0]) trx(p:p1)
'''.format(pval = expectedDefValue)

        posesSpecs = motiondsl.toPosesSpecification( motiondsl.dsl.modelFromText(model) )
        allParameters = []
        for pose in posesSpecs.poses:
            for s in pose.motion.sequences:
                for st in s.steps:
                    amount = st.amount
                    if isinstance(amount, numeric_argument.Expression):
                        arg = amount.arg
                        if isinstance(arg, numeric_argument.Parameter):
                            allParameters.append(arg)
        self.assertEqual(len(allParameters), 4)
        for p in allParameters:
            self.assertEqual(expectedDefValue, p.defaultValue)

