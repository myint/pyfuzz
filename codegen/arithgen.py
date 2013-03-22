class IntegerGen(object):

    def __init__(self, min_range, max_range, rng=None):
        self.rng = rng

        self.min_range = min_range
        self.max_range = max_range

    def __call__(self):
        return str(self.rng.randrange(self.min_range, self.max_range))

    def set_rng(self, rng):
        self.rng = rng
        return self


def gen_max_int_gen():
    return IntegerGen(-2**31, 2**31)


class ArithGen(object):

    bin_ops = ['+', '-', '&', '^', '|']  # , '%', '/', '//', '*'

    def __init__(self, nr_bin_ops, rng):
        self.nr_bin_ops = nr_bin_ops
        self.rng = rng
        if self.rng is None:
            import random
            self.rng = random.Random()

    def generate(self, literals=[]):
        self.bin_ops_left = self.nr_bin_ops
        return self.add_op(literals)

    def gen(self, stmt, literals):
        def gen_stmt():
            return stmt % (self.generate(literals), )

        return gen_stmt

    def add_op(self, literals):

        expr = []

        if self.bin_ops_left and self.rng.randint(0, 1):
            self.bin_ops_left -= 1
            if self.rng.randint(0, 1):
                expr.append(self.add_op(literals))
            else:
                expr.append(self.add_bracket(literals))
        else:
            l = self.rng.choice(literals)
            if isinstance(l, str):
                expr.append(l)
            else:
                expr.append(l())

        expr.append(self.rng.choice(self.bin_ops))

        if self.bin_ops_left and self.rng.randint(0, 1):
            self.bin_ops_left -= 1
            if self.rng.randint(0, 1):
                expr.append(self.add_op(literals))
            else:
                expr.append(self.add_bracket(literals))
        else:
            l = self.rng.choice(literals)
            if isinstance(l, str):
                expr.append(l)
            else:
                expr.append(l())

        return " ".join(expr)

    def add_bracket(self, literals):
        return "".join(['(', self.add_op(literals), ')'])
