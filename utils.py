from pygen.cgen import *

def eval_branches(rng, branches):
    total = sum((x[0] for x in branches))
    val = rng.random() * total

    for chance, result in branches:
        if val < chance:
            return result
        else:
            val -= chance
    return None

class FunctionGenerator(object):
    def generate_arguments(self, args_num):
        args = ["arg" + str(i) for i in xrange(self.stats.arg_number, self.stats.arg_number + args_num)]
        self.stats.arg_number += args_num
        return args

    def next_variable(self):
        nr = self.stats.arg_number
        self.stats.arg_number += 1
        return "var%d" % (nr, )

    def create_function(self, args):
        f = Function("func%d" % (self.stats.func_number,), args, [])
        self.stats.func_number += 1
        return f


