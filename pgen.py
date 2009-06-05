from arithgen import IntegerGen, gen_max_int_gen

pgen_opts = {
    "module" : {"children" : [(1.0, "arith_integer"), (0.0, "arith_float")],
                "mainloop" : 2000, "prog_size" : 10,
               },
    "arith_integer" : {
                "children" : [(1.0, "arith_integer"), (1.0, ("arith_integer", "local")), (1.0, "loop_integer")],
                "max_children" : 5,
                "numbers" : [gen_max_int_gen(), IntegerGen(-1000, 1000)],
                "type" : [(1.0, "thin"), (1.0, "fat")],
               },
    "loop_integer" : {
                "numbers" : [IntegerGen(-10, 10)],
               },
    "tuple" : {},

}

from pygen.cgen import *
from arithgen import ArithGen

class ProgGenerator(object):
    def __init__(self, opts, rng):
        self.opts = opts
        self.module = None
        self.rng = rng

    def eval_branches(self, branches):
        total = sum((x[0] for x in branches))
        val = self.rng.random() * total

        for chance, result in branches:
            if val < chance:
                return result
            else:
                val -= chance

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
            ForLoop('i', 'xrange(%d)' % (lopts["mainloop"],), main)
        )

        if "children" in lopts:
            branch = self.eval_branches(lopts["children"])
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
        args = ["arg" + str(i) for i in xrange(self.arg_number, self.arg_number + args_num)]
        self.arg_number += args_num
        
        f = Function("func%d" % (self.func_number,), args, [])
        self.func_number += 1

        literals = set(args) | set(globals)

        children = min(self.rng.randint(0, opts["max_children"]), self.prog_size)
        if children > 0:
            self.prog_size -= children
            for i in xrange(children):
                branch = self.eval_branches(opts["children"])
                if branch == "arith_integer":
                    c = self.arith_integer(opts, 2)
                    self.module.content.insert(0, c)

                    args = self.rng.sample(list(literals), 2)
                    result = self.next_variable()

                    call = Assignment(result, '=', [CallStatement(c, args)])
                    f.content.append(call)
                    literals.add(result)


                if branch == ("arith_integer", "local"):
                    c = self.arith_integer(opts, 2, list(literals))
                    f.content.append(c)

                    args = self.rng.sample(list(literals), 2)
                    result = self.next_variable()

                    call = Assignment(result, '=', [CallStatement(c, args)])
                    f.content.append(call)
                    literals.add(result)
                    
                if branch == "loop_integer":
                    c = self.loop_integer(self.opts['loop_integer'], 2, [])
                    self.module.content.insert(0, c)

                    args = self.rng.sample(list(literals), 2)
                    result = self.next_variable()

                    call = Assignment(result, '=', [CallStatement(c, args)])
                    f.content.append(call)
                    literals.add(result)


        numbers = [n.set_rng(self.rng) for n in opts["numbers"]]
        branch_type = self.eval_branches(opts["type"])
        if branch_type == "thin":
            gen = ArithGen(2, self.rng)
            for i in xrange(self.rng.randint(10,25)):
                result = self.next_variable()

                exp = gen.generate(list(literals) + numbers)
                f.content.append(Assignment(result, '=', [exp]))
                literals.add(result)
                
        if branch_type == "fat":
            gen = ArithGen(20, self.rng)
            for i in xrange(self.rng.randint(0,5)):
                result = self.next_variable()

                exp = gen.generate(list(literals) + numbers)
                f.content.append(Assignment(result, '=', [exp]))
                literals.add(result)
      
        exp = ArithGen(10, self.rng).generate(list(literals) + numbers)
        f.content.append(Assignment('result', '=', [exp]))
        f.content.append('return result')

        return f
        
    def loop_integer(self, opts, args_num, globals):
        '''Insert a new function with a loop containing some integer operations'''
        args = ["arg" + str(i) for i in xrange(self.arg_number, self.arg_number + args_num)]
        self.arg_number += args_num

        literals = set(args) | set(globals)
        numbers = [n.set_rng(self.rng) for n in opts["numbers"]]
        
        f = Function("func%d" % (self.func_number,), args, [])
        self.func_number += 1

        result = self.next_variable()
        literals.add(result)

        loop_var = self.next_variable()
        literals.add(loop_var)
        iter = "xrange(50)"
        l = ForLoop(loop_var, iter)
        exp = ArithGen(1, self.rng).generate(list(literals) + numbers)
        l.content.append(Assignment(result, '+=', [exp]))
        
        f.content.append(Assignment(result, '=', ['0']))
        f.content.append(l)
        f.content.append("return " + result)

        return f





