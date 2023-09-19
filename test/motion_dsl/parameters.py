import unittest
import random, math

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
