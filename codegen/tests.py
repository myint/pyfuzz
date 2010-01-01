import unittest

from pygen.cgen import *
from classes import ClassGenerator

class TStats(object):
    def __init__(self):
        self.arg_number = 0
        self.func_number = 0
        self.prog_size = 0

class TModule(object):
    def __init__(self):
        self.content = []

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

        self.gen = ClassGenerator(self.module, self.stats, self.opts)

        self.fgen = FixGenerator()
        self.cgen = CodeGenerator()

    def testMonomorphic(self):
        result = self.gen.generate_monomorphic(['0', '1'])
        result.extend(self.module.content)

        code = self.codegen(result)

        self.assert_('for' in code)
        self.assert_('.func' in code)
        self.assert_('= class' in code)

    def testPolymorphic(self):
        result = self.gen.generate_polymorphic(['0', '1'])
        result.extend(self.module.content)

        code = self.codegen(result)

        self.assert_('for' in code)
        self.assert_('.func' in code) # method call
        self.assert_('= class' in code) # object instantiation
        self.assert_('(class' in code) # inheritance

    def testDuck(self):
        result = self.gen.generate_duck(['0', '1'])
        result.extend(self.module.content)

        code = self.codegen(result)

        self.assert_('for' in code)
        self.assert_('.func' in code) # method call
        self.assert_('= class' in code) # object instantiation

