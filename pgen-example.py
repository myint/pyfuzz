#!/usr/bin/env python

from __future__ import print_function

import random

from pgen import pgen_opts, ProgGenerator
from pygen.cgen import CodeGenerator


if __name__ == "__main__":
    pgen = ProgGenerator(pgen_opts, random.Random())

    m = pgen.generate()

    cgen = CodeGenerator()

    print(cgen.generate(m))
