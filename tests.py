import unittest

from pgen import *
from utils import FunctionGenerator


class TestUtilFunctions(unittest.TestCase):

    def testEvalBranches(self):
        class Random(object):

            def random(self):
                return 0.9

        rng = Random()

        result = eval_branches(rng, [(0.5, 0), (1.0, 1)])
        self.assertEqual(result, 1)


class TestFunctionGenerator(unittest.TestCase):

    def setUp(self):
        pass

    def testCreateFunction(self):
        class TestModule(object):
            pass

        module = TestModule()
        module.func_number = 0

        fgen = FunctionGenerator()
        fgen.stats = module

        f = fgen.create_function(["args"])
        self.assertEqual(module.func_number, 1)
        self.assert_(f.name == "func0")
        self.assert_("args" in f.args)

    def testGenerateArguments(self):
        class TestModule(object):
            pass

        module = TestModule()
        module.arg_number = 0

        fgen = FunctionGenerator()
        fgen.stats = module

        args = fgen.generate_arguments(5)

        self.assertEqual(len(args), 5)
        self.assert_("arg0" in args)
        self.assert_("arg4" in args)

        self.assertEqual(module.arg_number, 5)

    def testNextVariable(self):
        class TestModule(object):
            pass

        module = TestModule()
        module.arg_number = 0

        fgen = FunctionGenerator()
        fgen.stats = module

        var = fgen.next_variable()
        self.assertEqual("var0", var)
        self.assertEqual(module.arg_number, 1)


if __name__ == "__main__":
    unittest.main()
