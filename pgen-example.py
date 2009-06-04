from pgen import *
import random

pgen = ProgGenerator(pgen_opts, random.Random())

m = pgen.generate()

from pygen.cgen import CodeGenerator

cgen = CodeGenerator()

print cgen.generate(m)
