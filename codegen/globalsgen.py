from pygen.cgen import Assignment, CallStatement

from utils import FunctionGenerator


class ChangeGlobalGenerator(FunctionGenerator):

    """This generates some code to change a global and test if the changed
    function is executed."""
    def __init__(self, module, stats, opts, rng):
        self.opts = opts
        self.module = module
        self.rng = rng
        self.stats = stats

    def generate_globalon(self, opts):
        f = self.create_function([])

        if opts["numbers"]:
            gen = self.rng.choice(opts["numbers"])
            gen.set_rng(self.rng)
            number = gen()
        else:
            number = 1

        f.content.append("global len")
        f.content.append("len = lambda x : %s" % (number,))
        return f

    def generate_globaloff(self, opts):
        f = self.create_function([])
        f.content.append("global len")
        f.content.append("del len")
        return f

    def generate(self, opts, args_num, globals):
        fon = self.generate_globalon(opts)
        foff = self.generate_globaloff(opts)

        self.module.content.insert(0, fon)
        self.module.content.insert(0, foff)

        from . import iterables
        iter_gen = iterables.IterableGenerator(
            self.module,
            self.stats,
            self.opts,
            self.rng)

        if opts["numbers"]:
            numbers = []
            for i in range(4):
                gen = self.rng.choice(opts["numbers"])
                gen.set_rng(self.rng)
                numbers.append(gen())
        else:
            numbers = ["1", "2", "3", "4"]

        iter = iter_gen.get_iterable(numbers)

        f = self.create_function([])
        f.content.extend(
            [
                CallStatement(fon, []),
                Assignment("result", '=', [CallStatement("len", iter)]),
                CallStatement(foff, []),
                "return result"
            ]
        )

        return f
