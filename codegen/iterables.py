from pygen.cgen import Assignment, CallStatement
from .arithgen import ArithGen, IntegerGen, gen_max_int_gen
from utils import eval_branches, FunctionGenerator

import pgen


class IterableGenerator(object):

    def __init__(self, module, stats, opts, rng):
        self.opts = opts
        self.module = module
        self.rng = rng
        self.stats = stats

    def get_iterable(self, literals):
        types = [(1.0,
                  "range")]  # iterables that dont require size
        if self.stats.prog_size > 0:
            types = types + [(
                             1.0,
                             "list_comp_gen"),
                             (1.0,
                             "list_comp_list"),
                             (1.0,
                             "yield_func")]

        branch = eval_branches(self.rng, types)

        if branch == "range":
            return ["range(%d)" % (self.rng.randint(1, 50))]

        if branch == "list_comp_gen":
            self.stats.prog_size -= 1

            gen = ListComprehensionGenerator(
                self.module,
                self.stats,
                self.opts,
                self.rng)
            return [gen.get_generator(literals)]

        if branch == "list_comp_list":
            self.stats.prog_size -= 1

            gen = ListComprehensionGenerator(
                self.module,
                self.stats,
                self.opts,
                self.rng)
            return [gen.get_list(literals)]

        if branch == "yield_func":
            self.stats.prog_size -= 1
            gen = YieldFunctionGenerator(
                self.module,
                self.stats,
                self.opts,
                self.rng)
            return [gen.generate(2, literals)]


class YieldFunctionGenerator(FunctionGenerator):

    """Returns a generator which uses yield."""
    def __init__(self, module, stats, opts, rng):
        self.opts = opts
        self.module = module
        self.rng = rng
        self.stats = stats

    def generate_child(self, func, literals):
        """Insert a function call to calculate some numbers."""
        gen = pgen.ArithIntegerGenerator(
            self.module,
            self.stats,
            self.opts,
            self.rng)
        c = gen.generate(self.opts["arith_integer"], 2)

        self.module.content.insert(0, c)

        args = self.rng.sample(literals, 2)
        result = self.next_variable()
        call = Assignment(result, '=', [CallStatement(c, args)])
        func.content.append(call)
        func.content.append("yield %s" % (result, ))

    def generate(self, args_num, pliterals):
        """Returns a CallStatement."""

        args = self.generate_arguments(args_num)
        f = self.create_function(args)
        self.module.content.insert(0, f)

        literals = list(
            args) + [
                n.set_rng(
                    self.rng) for n in [
                        gen_max_int_gen(
                        ),
                        IntegerGen(
                            -1000,
                            1000)]]

        if self.stats.prog_size > 0:
            self.generate_child(f, literals)

        for i in range(10):
            result = self.next_variable()
            exp = ArithGen(2, self.rng).generate(literals)
            literals.append(result)

            f.content.append(Assignment(result, '=', [exp]))
            f.content.append("yield %s" % (result, ))

        pargs = self.rng.sample(pliterals, args_num)
        return CallStatement(f, pargs)


class ListComprehensionGenerator(FunctionGenerator):

    """Returns a listcomprehension either as a list or a generator."""
    def __init__(self, module, stats, opts, rng):
        self.opts = opts
        self.module = module
        self.rng = rng
        self.stats = stats

    def get_expression(self, literals):
        literals = list(
            literals) + [
                n.set_rng(
                    self.rng) for n in [
                        IntegerGen(
                            -10,
                            10)]]
        branch = eval_branches(self.rng, [(1.0, "thin"), (1.0, "fat")])

        iterable = IterableGenerator(
            self.module,
            self.stats,
            self.opts,
            self.rng).get_iterable(
                literals)

        literals.append('i')
        if branch == "fat":
            exp = ArithGen(10, self.rng).generate(literals)
        if branch == "thin":
            exp = ArithGen(1, self.rng).generate(literals)
        return ["%s for i in " % (exp, ), iterable]

    def get_generator(self, literals):
        return ["(", self.get_expression(literals), ")"]

    def get_list(self, literals):
        return ["[", self.get_expression(literals), "]"]
