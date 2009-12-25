from pygen.cgen import *
from arithgen import ArithGen
import iterables

from utils import eval_branches, FunctionGenerator

import pgen

import random


class ClassGenerator(FunctionGenerator):
    def __init__(self, module, stats, opts, rng=None):
        self.opts = opts
        self.module = module
        self.rng = rng
        if not rng:
            self.rng = random.Random()
        self.stats = stats

        self.branches = [
            (1.0, self.generate_monomorphic),
#            (),
        ]

    def get_iterable(self, literals):
        iter_gen = iterables.IterableGenerator(self.module, self.stats, self.opts, self.rng)
        return iter_gen.get_iterable(literals)


    def generate_inline(self, literals):
        c = self.create_class()
        self.module.content.insert(0, c)

        args = self.generate_arguments(2)
        m = self.create_method(args)

        c.content.append(m)

        branch = eval_branches(self.rng, self.branches)
        return branch(c, m, literals)
        


    def generate_monomorphic(self, c, m, literals):
        result = []

        class_var = self.next_variable()
        result.append(Assignment(class_var, '=', [CallStatement(c, [])]))

        loop_var = self.next_variable()
        iter = self.get_iterable(literals)
 
        l = ForLoop(loop_var, iter)
        result.append(l)
        
        loop_literals = list(literals) + [loop_var]

        args = [self.rng.choice(loop_literals) for i in m.args]
        l.content.append(CallStatement(class_var + '.' + m.name, args))

        return result




