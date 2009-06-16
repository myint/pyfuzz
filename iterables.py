
from pygen.cgen import *
from arithgen import ArithGen

from utils import eval_branches, FunctionGenerator

class IterableGenerator(object):
    def __init__(self, module, stats, opts, rng):
        self.opts = opts
        self.module = module
        self.rng = rng
        self.stats = stats

    def get_iterable(self, literals):
        opts = self.opts["iter_gen"]

        types = list(opts["type"]) # iterables that dont require size
        if self.stats.prog_size > 0:
            types = types + opts["children"]

        branch = eval_branches(self.rng, types)

        if branch == "range":
            return "range(%d)" % (self.rng.randint(1,50))

        if branch == "xrange":
            return "xrange(%d)" % (self.rng.randint(1,50))


        if branch == "list_comp_gen":
            self.stats.prog_size -= 1

            gen = ListComprehensionGenerator(self.module, self.stats, self.opts, self.rng)
            return gen.get_generator(self.opts["list_comp_small_int"], literals)

        if branch == "list_comp_list":
            self.stats.prog_size -= 1

            gen = ListComprehensionGenerator(self.module, self.stats, self.opts, self.rng)
            return gen.get_list(self.opts["list_comp_small_int"], literals)

class ListComprehensionGenerator(FunctionGenerator):
    def __init__(self, module, stats, opts, rng):
        self.opts = opts
        self.module = module
        self.rng = rng
        self.stats = stats

    def get_expression(self, opts, literals):
        literals = list(literals) + [n.set_rng(self.rng) for n in opts["numbers"]] + ["i"]
        branch = eval_branches(self.rng, opts["type"])

        iterable = IterableGenerator(self.module, self.stats, self.opts, self.rng).get_iterable(literals)

        if branch == "fat":
            exp = ArithGen(10, self.rng).generate(literals)
        if branch == "thin":
            exp = ArithGen(1, self.rng).generate(literals)
        return "%s for i in %s" % (exp, iterable)

    def get_generator(self, opts, literals):
        return "(%s)" % (self.get_expression(opts, literals), )
    def get_list(self, opts, literals):
        return "[%s]" % (self.get_expression(opts, literals), )

