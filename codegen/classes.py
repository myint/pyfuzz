from pygen.cgen import Assignment, CallStatement, IfStatement, ForLoop
from .arithgen import ArithGen, gen_max_int_gen

from utils import eval_branches, FunctionGenerator


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
            (1.0, self.generate_duck),
        ]

    def get_iterable(self, literals):
        from . import iterables
        iter_gen = iterables.IterableGenerator(
            self.module,
            self.stats,
            self.opts,
            self.rng)
        return iter_gen.get_iterable(literals)

    def make_class_function(self):
        c = self.create_class()
        self.module.content.insert(0, c)

        args = self.generate_arguments(2)
        m = self.create_method(args)

        c.content.append(m)
        return c, m

    def make_loop(self, literals, class_var, m):
        loop_var = self.next_variable()
        iter = self.get_iterable(literals)

        l = ForLoop(loop_var, iter)

        loop_literals = list(literals) + [loop_var]

        args = [self.rng.choice(loop_literals) for i in m.args]
        if self.rng.random() < 0.5:
            func = class_var + '.' + m.name
        else:  # Sometimes copy the function into a variable
            func = self.next_variable()
            l.content.append(Assignment(func, '=', [class_var + '.' + m.name]))

        l.content.append(CallStatement(func, args))

        return l

    def make_fill(self, m):
        filled = [(1.0, self.fill_zero),
                  (1.0, self.fill_some_arith)]

        branch = eval_branches(self.rng, filled)
        branch(m)

    def fill_zero(self, m):
        m.content.append('return 0')

    def fill_some_arith(self, m):
        def low_numbers():
            return str(self.rng.randint(-1, 1))

        numbers = [gen_max_int_gen().set_rng(self.rng), low_numbers]
        exp = ArithGen(5, self.rng).generate(m.args + numbers)

        m.content.extend([
            Assignment('result', '=', [exp]),
            'return result',
        ])

    def generate_inline(self, literals):
        branch = eval_branches(self.rng, self.branches)
        return branch(literals)

    def generate_monomorphic(self, literals):
        """Generates a monomorphic callsite."""
        c, m = self.make_class_function()

        self.make_fill(m)

        result = []

        class_var = self.next_variable()
        result.append(Assignment(class_var, '=', [CallStatement(c, [])]))

        l = self.make_loop(literals, class_var, m)
        result.append(l)
        return result

    def generate_polymorphic(self, literals):
        """Generate a polymorphic callsite."""
        c, m = self.make_class_function()
        c_super, m_super = self.make_class_function()
        m_super.name = m.name

        c.super = [c_super.name]

        self.make_fill(m)
        self.make_fill(m_super)

        class_var = self.next_variable()
        clause = self.rng.choice(
            list(
                literals)) + " < " + self.rng.choice(
                    list(
                        literals))
        i = IfStatement(clause,
                        [Assignment(class_var, '=', [CallStatement(c, [])])],
                        [Assignment(
                         class_var,
                         '=',
                         [CallStatement(c_super,
                                        [])])]
                        )
        result = [i]

        l = self.make_loop(literals, class_var, m)
        result.append(l)

        return result

    def generate_duck(self, literals):
        """Generate a duck typing callsite."""
        c, m = self.make_class_function()
        c_super, m_super = self.make_class_function()
        m_super.name = m.name

        self.make_fill(m)
        self.make_fill(m_super)

        class_var = self.next_variable()
        clause = self.rng.choice(
            list(
                literals)) + " < " + self.rng.choice(
                    list(
                        literals))
        i = IfStatement(clause,
                        [Assignment(class_var, '=', [CallStatement(c, [])])],
                        [Assignment(
                         class_var,
                         '=',
                         [CallStatement(c_super,
                                        [])])]
                        )
        result = [i]

        l = self.make_loop(literals, class_var, m)
        result.append(l)

        return result
