from pygen.cgen import Assignment, CallStatement, IfStatement
from .arithgen import ArithGen

from utils import eval_branches, FunctionGenerator

import pgen


class TailRecursionGenerator(FunctionGenerator):

    """This generates some code to test tail recursion handling."""
    def __init__(self, module, stats, opts, rng):
        self.opts = opts
        self.module = module
        self.rng = rng
        self.stats = stats

    def generate_standard_tail_call(self, opts):
        if opts["numbers"]:
            numbers = []
            for i in range(4):
                gen = self.rng.choice(opts["numbers"])
                gen.set_rng(self.rng)
                numbers.append(gen())
        else:
            numbers = ["1", "2", "3", "4"]

        func = self.create_function(["acc", "rest"])

        exp = ArithGen(1, self.rng).generate(["acc", "rest"] + numbers)

        var = self.next_variable()
        func.content.append(Assignment(var, '=', [exp]))

        end = IfStatement("acc == 0",
                          ["return %s" % (var,)],
                          [Assignment(
                           "result", "=", [CallStatement(func, ["acc - 1", var])]),
                           "return result"])

        func.content.append(end)
        return func

    def generate_fcall_tail_call(self, opts):
        if opts["numbers"]:
            numbers = []
            for i in range(4):
                gen = self.rng.choice(opts["numbers"])
                gen.set_rng(self.rng)
                numbers.append(gen())
        else:
            numbers = ["1", "2", "3", "4"]

        func = self.create_function(["acc", "rest"])

        # generate an arith_integer function
        gen = pgen.ArithIntegerGenerator(
            self.module,
            self.stats,
            self.opts,
            self.rng)
        c = gen.generate(self.opts["arith_integer"], 2)
        self.module.content.insert(0, c)

        args = self.rng.sample(["acc", "rest"] + numbers, 2)
        result = self.next_variable()

        call = Assignment(result, '=', [CallStatement(c, args)])
        func.content.append(call)

        end = IfStatement("acc == 0",
                          ["return %s" % (result,)],
                          [Assignment(
                           "result", "=", [CallStatement(func, ["acc - 1", result])]),
                           "return result"])

        func.content.append(end)
        return func

    def generate_closure_tail_call(self, opts):
        if opts["numbers"]:
            numbers = []
            for i in range(4):
                gen = self.rng.choice(opts["numbers"])
                gen.set_rng(self.rng)
                numbers.append(gen())
        else:
            numbers = ["1", "2", "3", "4"]

        func = self.create_function(["acc", "rest"])

        exp = ArithGen(
            5,
            self.rng).generate(["closure[0]",
                                "acc",
                                "rest"] + numbers)

        var = self.next_variable()
        func.content.append(Assignment(var, '=', [exp]))
        func.content.append(Assignment("closure[0]", '+=', [var]))

        end = IfStatement("acc == 0",
                          ["return %s" % (var,)],
                          [Assignment(
                           "result", "=", [CallStatement(func, ["acc - 1", var])]),
                           "return result"])

        func.content.append(end)
        return func

    def generate(self, opts, args_num, globals):
        args = self.generate_arguments(args_num)
        func = self.create_function(args)

        branch = eval_branches(self.rng, opts["type"])

        if branch == "standard":
            rec = self.generate_standard_tail_call(opts)
        elif branch == "closure":
            func.content.append(Assignment("closure", "=", ["[0]"]))
            rec = self.generate_closure_tail_call(opts)
        else:
            rec = self.generate_fcall_tail_call(opts)

        func.content.append(rec)

        func.content.extend(
            [Assignment("result", "=", [CallStatement(rec, ["10", "0"])]),
             "return result"])

        self.module.content.append(func)

        return func
