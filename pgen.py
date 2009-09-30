from arithgen import IntegerGen, gen_max_int_gen

pgen_opts = {
    "module" : {"children" : [(1.0, "arith_integer"), (0.0, "arith_float")],
                "mainloop" : 2000, "prog_size" : 20,
               },
    "arith_integer" : {
                "children" : [
                        (1.0, "arith_integer"),
                        (1.0, ("arith_integer", "local")),
                        (2.0, "loop_integer"),
                        (1.0, "change_global"),
                        ],
                "max_children" : 5,
                "numbers" : [gen_max_int_gen(), IntegerGen(-1000, 1000)],
                "type" : [(1.0, "thin"), (1.0, "fat")],
                "if" : 0.10,
               },
    "loop_integer" : {
                "numbers" : [IntegerGen(-10, 10)],
                "if" : 0.10,
               },
    "list_comp_small_int" : {
                "numbers" : [IntegerGen(-10, 10)],
                "type" : [(1.0, "thin"), (1.0, "fat")],
               },
    "tuple" : {},
    "iter_gen" : {
                "type" : [(1.0, "xrange"), (1.0, "range")],
                "children" : [(1.0, "list_comp_gen"), (1.0, "list_comp_list"), (1.0, "yield_func")],
               },
    "yieldfunction" : {
                "numbers" : [gen_max_int_gen(), IntegerGen(-1000, 1000)],
               },
    "change_global" : {
               },
}

from pygen.cgen import *
from arithgen import ArithGen

from utils import eval_branches, FunctionGenerator
from iterables import IterableGenerator, ListComprehensionGenerator 
from globalsgen import ChangeGlobalGenerator

class LoopIntegerGenerator(FunctionGenerator):
    def __init__(self, module, stats, opts, rng):
        self.opts = opts
        self.module = module
        self.rng = rng
        self.stats = stats

    def get_iterable(self, opts, literals):
        iter_gen = IterableGenerator(self.module, self.stats, self.opts, self.rng)
        return iter_gen.get_iterable(literals)

    def loop_integer(self, opts, args_num, globals):
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
            c = gen.arith_integer(opts, 2)
            self.module.content.insert(0, c)

            args = self.rng.sample(list(literals), 2)
            result = self.next_variable()

            call = Assignment(result, '=', [CallStatement(c, args)])
            f.content.append(call)
            literals.add(result)

        if branch == ("arith_integer", "local"):
            gen  = ArithIntegerGenerator(self.module, self.stats, self.opts, self.rng)
            c = gen.arith_integer(opts, 2, list(literals))

            f.content.append(c)

            args = self.rng.sample(list(literals), 2)
            result = self.next_variable()

            call = Assignment(result, '=', [CallStatement(c, args)])
            f.content.append(call)
            literals.add(result)
                   
        if branch == "loop_integer":
            gen  = LoopIntegerGenerator(self.module, self.stats, self.opts, self.rng)

            c = gen.loop_integer(self.opts['loop_integer'], 2, [])
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
            



    def arith_integer(self, opts, args_num, globals=[]):
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
 

class ProgGenerator(object):
    def __init__(self, opts, rng):
        self.opts = opts
        self.module = None
        self.rng = rng

    def next_variable(self):
        nr = self.arg_number
        self.arg_number += 1
        return "var%d" % (nr, )

    def generate(self):
        '''Instantiates a new module and fills it randomly'''
        self.module = Module(main = True)
        self.func_number = 1
        self.arg_number = 1
        lopts = self.opts["module"]

        self.prog_size = lopts["prog_size"]

        main = []
        self.module.main_body.append(
            ForLoop('i', ['xrange(%d)' % (lopts["mainloop"],)], main)
        )

        if "children" in lopts:
            branch = eval_branches(self.rng, lopts["children"])
            if branch == "arith_integer":
                main.append(Assignment('x', '=', ['5']))
                f = self.arith_integer(self.opts[branch], 2)
                main.append(Assignment('x', '=', [CallStatement(f, ['x','i'])]))
                main.append('print x,')

                self.module.content.insert(0, f)
            if branch == "arith_float":
                main.append(Assignment('x', '=', ['5.0']))
                main.append('print x,')

        return self.module

    def arith_integer(self, opts, args_num, globals=[]):
        '''Insert a new arithmetic function using only integers'''
        gen = ArithIntegerGenerator(self.module, self, self.opts, self.rng)
        f = gen.arith_integer(opts, args_num, globals)

        return f
        
    def loop_integer(self, opts, args_num, globals):
        '''Insert a new function with a loop containing some integer operations'''
        gen = LoopIntegerGenerator(self.module, self, self.opts, self.rng)
        f = gen.loop_integer(opts, args_num, globals)

        return f





