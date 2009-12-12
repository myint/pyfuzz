from pygen.cgen import *
from arithgen import ArithGen

class FunWithIf(object):

    def __init__(self, literals):
        pass


    def gen(self):
        pass


class FunWithFunctions(object):
    def __init__(self, variables, literals, rng):
        self.variables = variables
        self.literals = literals

        self.rng = rng
        if self.rng == None:
            import random
            self.rng = random.Random()

    def gen(self, funcs, prefix, nr):
        newfuncs = []

        allfuncs = [f for f in funcs]

        for i in xrange(nr):
            f = Function(prefix + str(i), self.variables,
                         [CallStatement(self.rng.choice(allfuncs), self.variables),
                          CallStatement(self.rng.choice(allfuncs), self.variables),
                          CallStatement(self.rng.choice(allfuncs), self.variables),
#                          CallStatement(self.rng.choice(allfuncs), self.variables),
                         ]
                        )
            newfuncs.append(f)
            allfuncs.append(f)

        return newfuncs



class FunWithArith(object):

    inplace_ops = ['+=', '-='] # '/=', '*='

    def __init__(self, variables, literals, rng):
        self.variables = variables
        self.literals = literals

        self.rng = rng
        if self.rng == None:
            import random
            self.rng = random.Random()

    def gen_content(self, nr, binops):
        content = []

        agen = ArithGen(binops, self.rng)

        for i in xrange(nr):
            line = [self.rng.choice(self.variables), self.rng.choice(self.inplace_ops)]
            line.append(agen.generate(self.literals))

            content.append(" ".join(line))

        content.append("return %s" % (self.rng.choice(self.variables),))
        return content


    def gen(self, name, nr, binops):
        f = Function("name", self.variables, self.gen_content(nr, binops))
        return f
