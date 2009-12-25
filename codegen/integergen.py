from pygen.cgen import *
from arithgen import ArithGen

from utils import eval_branches, FunctionGenerator
#from iterables import IterableGenerator, ListComprehensionGenerator
import iterables
from globalsgen import ChangeGlobalGenerator
from recursion import TailRecursionGenerator
import classes

class ArithIntegerGenerator(FunctionGenerator):
    def __init__(self, module, stats, opts, rng):
        self.opts = opts
        self.module = module
        self.rng = rng
        self.stats = stats

    def generate_statement(self, opts, f, gen, literals, numbers):
        if opts["if"] > self.rng.random():
            result = self.next_variable()

            exp1 = gen.generate(list(literals) + numbers)
            exp2 = gen.generate(list(literals) + numbers)

            clause = self.rng.choice(list(literals)) + " < " + self.rng.choice(list(literals))

            i = IfStatement(clause,
                [Assignment(result, '=', [exp1])],
                [Assignment(result, '=', [exp2])])
            f.content.append(i)

        else:
            result = self.next_variable()

            exp = gen.generate(list(literals) + numbers)
            f.content.append(Assignment(result, '=', [exp]))
            literals.add(result)

    def generate_child(self, opts, f, literals):
        branch = eval_branches(self.rng, opts["children"])
        if branch == "arith_integer":
            gen  = ArithIntegerGenerator(self.module, self.stats, self.opts, self.rng)
            c = gen.generate(opts, 2)
            self.module.content.insert(0, c)

            args = self.rng.sample(list(literals), 2)
            result = self.next_variable()

            call = Assignment(result, '=', [CallStatement(c, args)])
            f.content.append(call)
            literals.add(result)

        if branch == ("arith_integer", "local"):
            gen  = ArithIntegerGenerator(self.module, self.stats, self.opts, self.rng)
            c = gen.generate(opts, 2, list(literals))

            f.content.append(c)

            args = self.rng.sample(list(literals), 2)
            result = self.next_variable()

            call = Assignment(result, '=', [CallStatement(c, args)])
            f.content.append(call)
            literals.add(result)

        if branch == "loop_integer":
            gen  = LoopIntegerGenerator(self.module, self.stats, self.opts, self.rng)

            c = gen.generate(self.opts['loop_integer'], 2, [])
            self.module.content.insert(0, c)

            args = self.rng.sample(list(literals), 2)
            result = self.next_variable()

            call = Assignment(result, '=', [CallStatement(c, args)])
            f.content.append(call)
            literals.add(result)

        if branch == "change_global":
            gen = ChangeGlobalGenerator(self.module, self.stats, self.opts, self.rng)

            c = gen.generate(self.opts['change_global'], 0, [])
            self.module.content.insert(0, c)

            result = self.next_variable()

            call = Assignment(result, '=', [CallStatement(c, [])])
            f.content.append(call)
            literals.add(result)

        if branch == "integer_closure":
            gen = IntegerClosureGenerator(self.module, self.stats, self.opts, self.rng)
            func = gen.generate(self.opts['integer_closure'], 2, [])

            args = self.rng.sample(list(literals), 2)
            result = self.next_variable()

            call = Assignment(result, '=', [CallStatement(func, args)])
            f.content.append(call)
            literals.add(result)

        if branch == "tail_recursion":
            gen = TailRecursionGenerator(self.module, self.stats, self.opts, self.rng)
            func = gen.generate(self.opts['tail_recursion'], 2, [])

            args = self.rng.sample(list(literals), 2)
            result = self.next_variable()

            call = Assignment(result, '=', [CallStatement(func, args)])
            f.content.append(call)
            literals.add(result)

        if branch == "classes":
            gen = classes.ClassGenerator(self.module, self.stats, self.opts, self.rng)
            result = gen.generate_inline(literals)

            f.content.extend(result)

    def generate(self, opts, args_num, globals=[]):
        '''Insert a new arithmetic function using only integers'''
        args = self.generate_arguments(args_num)

        f = self.create_function(args)

        literals = set(args) | set(globals)

        children = min(self.rng.randint(0, opts["max_children"]), self.stats.prog_size)
        if children > 0:
            self.stats.prog_size -= children
            for i in xrange(children):
                self.generate_child(opts, f, literals)

        numbers = [n.set_rng(self.rng) for n in opts["numbers"]]
        branch_type = eval_branches(self.rng, opts["type"])
        if branch_type == "thin":
            gen = ArithGen(2, self.rng)
            for i in xrange(self.rng.randint(10,25)):
                self.generate_statement(opts, f, gen, literals, numbers)

        if branch_type == "fat":
            gen = ArithGen(20, self.rng)
            for i in xrange(self.rng.randint(0,5)):
                self.generate_statement(opts, f, gen, literals, numbers)

        exp = ArithGen(10, self.rng).generate(list(literals) + numbers)
        f.content.append(Assignment('result', '=', [exp]))
        f.content.append('return result')

        return f



class LoopIntegerGenerator(FunctionGenerator):
    def __init__(self, module, stats, opts, rng):
        self.opts = opts
        self.module = module
        self.rng = rng
        self.stats = stats

    def get_iterable(self, opts, literals):
        iter_gen = iterables.IterableGenerator(self.module, self.stats, self.opts, self.rng)
        return iter_gen.get_iterable(literals)

    def generate(self, opts, args_num, globals):
        '''Insert a new function with a loop containing some integer operations'''
        args = self.generate_arguments(args_num)

        literals = set(args) | set(globals)
        numbers = [n.set_rng(self.rng) for n in opts["numbers"]]

        f = self.create_function(args)

        result = self.next_variable()
        literals.add(result)

        iter = self.get_iterable(opts, literals)

        loop_var = self.next_variable()
        literals.add(loop_var)

        l = ForLoop(loop_var, iter)

        if opts["if"] > self.rng.random():
            exp1 = ArithGen(1, self.rng).generate(list(literals) + numbers)
            exp2 = ArithGen(1, self.rng).generate(list(literals) + numbers)

            clause = " ".join([self.rng.choice(list(literals)), "<", self.rng.choice(list(literals))])

            i = IfStatement(clause,
                            [Assignment(result, '+=', [exp1])],
                            [Assignment(result, '+=', [exp2])])
            l.content.append(i)

        else:
            exp = ArithGen(1, self.rng).generate(list(literals) + numbers)
            l.content.append(Assignment(result, '+=', [exp]))


        f.content.append(Assignment(result, '=', ['0']))
        f.content.append(l)
        f.content.append("return " + result)

        return f

class IntegerClosureGenerator(FunctionGenerator):
    def __init__(self, module, stats, opts, rng):
        self.opts = opts
        self.module = module
        self.rng = rng
        self.stats = stats

    def generate(self, opts, args_num, globals=[]):
        '''Insert a new arithmetic function using only integers'''
        args = self.generate_arguments(args_num)

        closure = self.create_function(args)

        gen = self.create_function([])

        if opts["numbers"]:
            number_gen = self.rng.choice(opts["numbers"])
            number_gen.set_rng(self.rng)
            number = number_gen()
        else:
            number = 0


        gen.content.extend(
            [
                "closure = [%s]" % (number, ),
                closure,
                Assignment("func", "=", [closure.name]),
                "return func",
            ]
        )

        c_var = self.next_variable()

        self.module.content.insert(0, gen)
        self.module.content.insert(1, Assignment(c_var, "=", [CallStatement(gen, [])]))

        gen_ai = ArithIntegerGenerator(self.module, self.stats, self.opts, self.rng)
        f = gen_ai.generate(self.opts["arith_integer"], args_num, [])

        self.module.content.insert(0, f)

        closure.content.append(Assignment("closure[0]", "+=", [CallStatement(f, args)]))
        closure.content.append("return closure[0]")

        return c_var



