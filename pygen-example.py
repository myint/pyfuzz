from __future__ import print_function

import sys
import subprocess
import time
import pickle
import os
import random
from optparse import OptionParser

from pygen.cgen import CodeGenerator, FixGenerator
from pgen import pgen_opts, ProgGenerator


def _main():
    default_binary = sys.executable

    parser = OptionParser()
    parser.add_option(
        "-b",
        "--base",
        type="string",
        dest="base",
        default=default_binary,
        help="Base python binary. Default: " +
        default_binary)
    parser.add_option(
        "-B", "--base-args", type="string", dest="baseargs", default="",
        help="Additional arguments for base binary")
    parser.add_option(
        "-t",
        "--test",
        type="string",
        dest="test",
        help="Python binary to test.")
    parser.add_option(
        "-T", "--test-args", type="string", dest="testargs", default="",
        help="Additional arguments for base binary")

    parser.add_option(
        "--break",
        action="store_true",
        dest="break_on_error",
        default=False,
        help="Break on test error")
    parser.add_option(
        "-p",
        "--pickle",
        action="store_true",
        dest="pickle",
        default=False,
        help="Output pickled AST.")
    parser.add_option(
        "-i",
        type="int",
        dest="iterations",
        default=100000,
        help="Number of test iterations.")
    parser.add_option(
        "-s",
        "--seed",
        type="int",
        dest="seed",
        default=None,
        help="Seed value for random number generator")
    parser.add_option(
        "--codepath",
        type="string",
        dest="codepath",
        default=".",
        help="Path to store code files.")

    (options, args) = parser.parse_args()

    if not options.test:
        print("Please specifiy a test binary.")
        parser.print_help()
        return

    rng = random.Random()
    seed = options.seed
    if seed is None:
        seed = int(rng.random() * sys.maxsize)
    print("Using random seed", seed)
    rng.seed(seed)

    pgen = ProgGenerator(pgen_opts, rng)

    gen = CodeGenerator()
    fix = FixGenerator()
    totaltime = 0.0
    time_test = 0.0
    time_base = 0.0
    failed_a_test = False

    for i in range(options.iterations):

        failed_this_test = False
        mod = pgen.generate()
        fixed = fix.generate(mod)
        prefix = "pyfuzz-output.%d" % i
        prefix = os.path.join(options.codepath, prefix)
        with open(prefix + ".pickle", 'wb') as code_pickle:
            pickle.dump(fixed, code_pickle)

        code = gen.generate(fixed)

        code_path = prefix + ".py"
        with open(code_path, "w") as code_file:
            code_file.write(code)

        clock_test = time.time()
        test_command = [options.test] + options.testargs.split() + [code_path]
        p_test = subprocess.Popen(test_command,
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_test, stderr_test = p_test.communicate()
        clock_test = time.time() - clock_test
        time_test += clock_test
        totaltime += clock_test

        if p_test.returncode < 0:
            print("------- Encountered crash: Test -------")
            print(code)
            print("---------------------------------------")
            print("Run %s to reproduce" % " ".join(test_command))
            failed_this_test = True
            if options.break_on_error:
                return

        clock_base = time.time()
        base_command = [options.base] + options.baseargs.split() + [code_path]
        p_base = subprocess.Popen(base_command,
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_base, stderr_base = p_base.communicate()
        clock_base = time.time() - clock_base
        time_base += clock_base
        totaltime += clock_base

        if p_base.returncode < 0:
            print("------- Encountered crash: Base -------")
            print(code)
            print("---------------------------------------")
            print("Run %s to reproduce" % " ".join(base_command))
            failed_this_test = True
            if options.break_on_error:
                return

        if stdout_base != stdout_test:
            print("------- Encountered different result --------")
            print("Test %s" % (stdout_test, ))
            print("---------------------------------------")
            print("Base %s" % (stdout_base, ))
            print("---------------------------------------")
            print(code)
            print("---------------------------------------")
            failed_this_test = True
            if options.break_on_error:
                return

        failed_a_test |= failed_this_test
        if not failed_this_test:
            print("Iteration %s: PASS" % (i + 1,))
        if (i+1) % 10 == 0:
            print("%f Functions per Second" % (i/totaltime,))
            print(
                "Test: %f calls/sec | Base: %f calls/sec" %
                (i/time_test, i/time_base))

    if failed_a_test:
        print("Some tests failed; consult diagnostic output above.")
    else:
        print("All tests successful!")


if __name__ == '__main__':
    _main()
