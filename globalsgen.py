from pygen.cgen import *
from arithgen import ArithGen

from utils import eval_branches, FunctionGenerator

import pgen



class ChangeGlobalGenerator(FunctionGenerator):
    def __init__(self, module, stats, opts, rng):
        self.opts = opts
        self.module = module
        self.rng = rng
        self.stats = stats


    def generate_globalon(self):
        f = self.create_function(0)
        f.content.append("global len")
        f.content.append("len = lambda x : 1")
        return f

    def generate_globaloff(self):
        f = self.create_function(0)
        f.content.append("global len")
        f.content.append("del len")
        return f
        


    def generate(self, opts, args_num, globals):
        fon = self.generate_globalon()
        foff = self.generate_globaloff()
        
        self.module.content.insert(0,fon)
        self.module.content.insert(0,foff)
        
        f = self.create_function(0)
        f.content.extend(
        [
            CallStatement(fon, []),
            "result = len(range(100))",
            CallStatement(foff, []),
            "return result"
        ]
        )
        
        return f

