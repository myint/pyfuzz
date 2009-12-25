import unittest

from pygen.cgen import *
from classes import ClassGenerator

class Stats(object):
    arg_number = 0
    prog_size = 100

class TestClassesGenerator(unittest.TestCase):

    def codegen(self, l):
        result = []
        for line in l:
            result.append(self.cgen.generate(line))

        return '\n'.join(result)

    def setUp(self):
        self.opts = {'iter_gen' : {'type' : [(1.0, "xrange")], 'children' : []}}
        self.module = {}
        self.stats = Stats()

        self.gen = ClassGenerator(self.module, self.stats, self.opts)

        self.c = Class('C1')
        self.m = Method('M', ['a','b'])
        self.c.content.append(self.m)

        self.cgen = CodeGenerator()

    def testMonomorphic(self):
        result = self.gen.generate_monomorphic(self.c, self.m, ['1','1'])
        result.insert(0, self.c)

        code = self.codegen(result)

        self.assert_('for' in code)
        self.assert_('.M(' in code)
        self.assert_('C1()' in code)

