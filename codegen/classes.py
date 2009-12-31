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
            (1.0, self.generate_polymorphic),
        ]

    def get_iterable(self, literals):
        iter_gen = iterables.IterableGenerator(self.module, self.stats, self.opts, self.rng)
        return iter_gen.get_iterable(literals)


    def generate_inline(self, literals):
        branch = eval_branches(self.rng, self.branches)
        return branch(literals)

    def generate_class_function(self):
        c = self.create_class()
        self.module.content.insert(0, c)

        args = self.generate_arguments(2)
        m = self.create_method(args)

        c.content.append(m)
        return c, m


    def generate_monomorphic(self, literals):
        """Generates a monomorphic callsite"""
        c, m = self.generate_class_function()

        result = []

        class_var = self.next_variable()
        result.append(Assignment(class_var, '=', [CallStatement(c, [])]))

        loop_var = self.next_variable()
        iter = self.get_iterable(literals)
 
        l = ForLoop(loop_var, iter)
        result.append(l)
        
        loop_literals = list(literals) + [loop_var]


        args = [self.rng.choice(loop_literals) for i in m.args]
        if self.rng.random() < 0.5:
            func = class_var + '.' + m.name
        else: # Sometimes copy the function into a variable
            func = self.next_variable()
            l.content.append(Assignment(func, '=', [class_var + '.' + m.name]))

        l.content.append(CallStatement(func, args))

        return result


    def generate_polymorphic(self, literals, use_duck_typing=True):
        """Generate a polymorphic callsite"""
        c, m = self.generate_class_function()
        c_super, m_super = self.generate_class_function()
        m_super.name = m.name

        # test duck typing and class polymorphism
        if not use_duck_typing or self.rng.random() < 0.5:
            c.super = [c_super.name]
            if self.rng.random() < 0.5:
                c.content.remove(m)

        loop_var = self.next_variable()
        iter = self.get_iterable(literals)

        class_var = self.next_variable()
        clause = self.rng.choice(list(literals)) + " < " + self.rng.choice(list(literals))
        i = IfStatement(clause,
            [Assignment(class_var, '=', [CallStatement(c, [])])],
            [Assignment(class_var, '=', [CallStatement(c_super, [])])]
        )
        result = [i]

        l = ForLoop(loop_var, iter)
        result.append(l)
        loop_literals = list(literals) + [loop_var]

        if self.rng.random() < 0.5:
            func = class_var + '.' + m.name
        else: # Sometimes copy the function into a variable
            func = self.next_variable()
            l.content.append(Assignment(func, '=', [class_var + '.' + m.name]))

        args = [self.rng.choice(loop_literals) for i in m.args]
        l.content.append(CallStatement(func, args))
        return result


