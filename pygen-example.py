from pygen.cgen import *


from pgen import *

import sys
import subprocess
import time

import random

from optparse import OptionParser

def _main():
    default_binary = sys.executable

    parser = OptionParser()
    parser.add_option("-b", "--base", type="string", dest="base", default=default_binary, help="Base python binary. Default: "+default_binary)
    parser.add_option("-B", "--base-args", type="string", dest="baseargs", default="",
                        help="Additional arguments for base binary")
    parser.add_option("-t", "--test", type="string", dest="test", help="Python binary to test.")
    parser.add_option("-T", "--test-args", type="string", dest="testargs", default="",
                        help="Additional arguments for base binary")

    parser.add_option("--break", action="store_true", dest="break_on_error", default=False, help="Break on test error")

    parser.add_option("-i", type="int", dest="iterations", default=100000, help="Number of test iterations.")
    parser.add_option("-s", "--seed", type="int", dest="seed", default=None, help="Seed value for random number generator")

    (options, args) = parser.parse_args()

    if not options.test:
        print "Please specifiy a test binary."
        parser.print_help()
        return

    rng = random.Random()
    
    pgen = ProgGenerator(pgen_opts, rng)
    
    gen = CodeGenerator()
    fix = FixGenerator() 
    totaltime = 0.0
    time_test = 0.0
    time_base = 0.0
    
    for i in xrange(options.iterations):
        
        clock = time.time()
        mod = pgen.generate()
        fixed = fix.generate(mod)
        
        code = gen.generate(fixed)
 
        with open("code.py", "w") as code_file:
            code_file.write(code)
        
        clock_test = time.time()    
        p_test = subprocess.Popen([options.test] + options.testargs.split() + ['code.py'],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_test, stderr_test = p_test.communicate()
        clock_test = time.time() - clock_test
        time_test += clock_test
        totaltime += clock_test
        
        clock_base = time.time()
        p_base = subprocess.Popen([options.base] + options.baseargs.split() + ['code.py'],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_base, stderr_base = p_base.communicate()
        clock_base = time.time() - clock_base
        time_base += clock_base
        totaltime += clock_base
        
        if p_test.returncode == -11:
            print "------- Encountered crash: Test -------"
            print code
            print "---------------------------------------"
            if options.break_on_error:
                return


        if p_base.returncode == -11:
            print "------- Encountered crash: Base -------"
            print code
            print "---------------------------------------"
            if options.break_on_error:
                return

           
#        if clock_test < clock_base/2.0:
#            print "------- Fast test -------"
#            print "Test", clock_test
#            print "Base", clock_base
##            print code
#
#        if clock_test > clock_base*2.0:
#            print "------- Fast base -------"
#            print "Test", clock_test
#            print "Base", clock_base
##            print code

        if stdout_base != stdout_test:
            print "------- Encountered different result --------"
            print "Test %s" % (stdout_test, )
            print "---------------------------------------"
            print "Base %s" % (stdout_base, )
            print "---------------------------------------"
            print code
            print "---------------------------------------"
            if options.break_on_error:
                return


        
#        if clock > 10.0:
#            print code
        
        if (i+1) % 10 == 0:
            print "%f Functions per Second" % ((i+1)/totaltime,)
            print "Test: %f calls/sec | Base: %f calls/sec" % ((i+1)/time_test, (i+1)/time_base)
            
        
        
        

if __name__ == '__main__':
    _main()
