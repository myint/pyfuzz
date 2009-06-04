pgen_opts = {
    "module" : {"children" : [(1.0, "arith_integer"), (0.0, "arith_float")],
                "mainloop" : 2000, "prog_size" : 10,
               },
    "arith_integer" : {
                "children" : [(1.0, "arith_integer"), (1.0, ("arith_integer", "local"))],
                "max_children" : 5,
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
        self.arg_number + 1
        return "var%d" % (nr, )

    def generate(self):
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
                    f.content.insert(0, c)

                    args = self.rng.sample(list(literals), 2)
                    result = self.next_variable()

                    call = Assignment(result, '=', [CallStatement(c, args)])
                    f.content.append(call)
                    literals.add(result)


        exp = ArithGen(10, self.rng).generate(list(literals))
        f.content.append(Assignment('result', '=', [exp]))
        f.content.append('return result')

        return f
        
        





