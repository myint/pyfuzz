import unittest

from pygen.cgen import CodeGenerator, FixGenerator, Method
from .classes import ClassGenerator


class TStats(object):

    def __init__(self):
        self.arg_number = 0
        self.func_number = 0
        self.prog_size = 0


class TModule(object):

    def __init__(self):
        self.content = []


class TRng(object):

    def __init__(self, tc):
        self.tc = tc

    def random(self):
        return 0.0

    def randint(self, a, b):
        self.tc.assert_(a <= b)
        return a

    def choice(self, seq):
        self.tc.assert_(len(seq) > 0)
        return seq[0]


class TestClassesGenerator(unittest.TestCase):

    def codegen(self, l):
        result = []
        for line in l:
            result.append(
                self.cgen.generate(
                    self.fgen.generate(line)
                )
            )

        return '\n'.join(result)

    def setUp(self):
        self.opts = {}
        self.module = TModule()
        self.stats = TStats()

        self.gen = ClassGenerator(
            self.module,
            self.stats,
            self.opts,
            TRng(self))

        self.fgen = FixGenerator()
        self.cgen = CodeGenerator()

    def testFillSomeArith(self):
        m = Method("M", ['arg'])
        self.gen.fill_some_arith(m)

        code = self.codegen([m])
        self.assert_('def M' in code)
        self.assert_('return result' in code)
        self.assert_('result =' in code)

    def testMonomorphic(self):
        result = self.gen.generate_monomorphic(['0', '1'])
        result.extend(self.module.content)

        code = self.codegen(result)

        self.assert_('for' in code)
        self.assert_('.func' in code)
        self.assert_('= class' in code)
        self.assert_('return 0' in code)

    def testPolymorphic(self):
        result = self.gen.generate_polymorphic(['0', '1'])
        result.extend(self.module.content)

        code = self.codegen(result)

        self.assert_('for' in code)
        self.assert_('.func' in code)  # method call
        self.assert_('= class' in code)  # object instantiation
        self.assert_('(class' in code)  # inheritance

    def testDuck(self):
        result = self.gen.generate_duck(['0', '1'])
        result.extend(self.module.content)

        code = self.codegen(result)

        self.assert_('for' in code)
        self.assert_('.func' in code)  # method call
        self.assert_('= class' in code)  # object instantiation
