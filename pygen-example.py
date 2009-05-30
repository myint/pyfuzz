from pygen.cgen import *
from arithgen import ArithGen, IntegerGen
from fungen import FunWithArith, FunWithFunctions

import subprocess
import time

import random

def _main():

    rng = random.Random()
    rng.seed(1)

    agen = ArithGen(10, rng)
    variables = ['x', 'i']
    literals = ['x', 'i', IntegerGen(-1000, 1000, rng), IntegerGen(-2**31, 2**31, rng)] #IntegerGen(-2**31, 2**31)
    
    mod = Module(main = True)
    
    f = FunWithArith(variables, literals, rng).gen("test_funwitharith", 10, 10)

    mod.content.append(f)
#    mod.content.append(Function("test", ["x", "i"], [ 
#             
#            IfStatement("i > x", 
#                            [agen.gen('x += %s', literals)], 
#                            [agen.gen('x -= %s', literals)]),
#             agen.gen('x += %s', literals),
#             CallStatement(f, ["x", "i"]), 
#             "return x"
#             
#            ]))

    mod.content += FunWithFunctions(variables, literals, rng).gen([f], "func", 100)
    

    #mod.main_body.append("x = 5")
    mod.main_body.append(
        ForLoop('i', 'xrange(10)',
              ["x = 5",
#               "x = test(x, i)",
                CallStatement(mod.content[-1], variables),
               "print x"]                   
                )
        )
    
    dotest(mod)
    
def dotest(mod):
    gen = CodeGenerator()
    
    totaltime = 0.0
    time_test = 0.0
    time_base = 0.0
    
    for i in xrange(100):
        
        clock = time.time()
            
        gen.generate(mod)
        code = gen.get_code()
 
        with open("code.py", "w") as code_file:
            code_file.write(code)
        
        clock_test = time.time()    
        p_test = subprocess.Popen(['/home/ebo/projects/unladen-swallow/python', 'code.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_test, stderr_test = p_test.communicate()
        clock_test = time.time() - clock_test
        time_test += clock_test
        totaltime += clock_test
        
        clock_base = time.time()
        p_base = subprocess.Popen(['python', 'code.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_base, stderr_base = p_base.communicate()
        clock_base = time.time() - clock_base
        time_base += clock_base
        totaltime += clock_base
        
        if p_test.returncode == -11:
            print "------- Encountered crash: Test -------"
            print code

        if p_base.returncode == -11:
            print "------- Encountered crash: Base -------"
            print code
            
        if clock_test < clock_base/2.0:
            print "------- Fast test -------"
            print "Test", clock_test
            print "Base", clock_base
            print code

        if clock_test > clock_base*2.0:
            print "------- Fast base -------"
            print "Test", clock_test
            print "Base", clock_base
            print code

        
#        if clock > 10.0:
#            print code
        
        if (i+1) % 10 == 0:
            print "%f Functions per Second" % ((i+1)/totaltime,)
            print "Test: %f | Base: %f" % ((i+1)/time_test, (i+1)/time_base)
            
        
        
        

if __name__ == '__main__':
    _main()