import unittest

import motiondsl.motiondsl as motiondsl

class RoundTrippingTests(unittest.TestCase):
    def _round_trip_and_compare(self, snippet):
        poseSpec = motiondsl.snippetToPoseSpec(snippet)

        snippet_reconstructed = motiondsl.poseSpecToMotionDSLSnippet(poseSpec)
        poseSpec2 = motiondsl.snippetToPoseSpec(snippet_reconstructed)

        for seq1,seq2 in zip(poseSpec.motion.sequences, poseSpec2.motion.sequences):
            self.assertEqual(seq1.steps, seq2.steps)

    def test_floatliteral(self):
        self._round_trip_and_compare("fA -> fB : rotx(0.123)")

    def test_variable(self):
        self._round_trip_and_compare("fA -> fB : roty(ry)")

    def test_parameter(self):
        self._round_trip_and_compare("fA -> fB : rotz(p:param1)")

    def test_parameter_expression(self):
        self._round_trip_and_compare("fA -> fB : rotz(p:param1) trx(2 * p:param2)")

    def test_constant(self):
        self._round_trip_and_compare("fA -> fB : trx(c:TR:-3.05)")

    def test_constant_expression(self):
        self._round_trip_and_compare("fA -> fB : trx(c:TR:1.02) try(-0.35 * c:TR)")

    def test_PI(self):
        self._round_trip_and_compare("fA -> fB : rotx(PI/2) rotz(1.5 * pi)")


if __name__ == '__main__':
    unittest.main()
