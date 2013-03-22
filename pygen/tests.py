import unittest

from .cgen import *


class TestModule(unittest.TestCase):

    def setUp(self):
        self.gen = CodeGenerator()
        self.fix = FixGenerator()

    def testEmptyModule(self):
        p = Module()
        p = self.fix.visit(p)

        self.assertEqual(self.gen.generate(p), '')

    def testEmptyMainModule(self):
        p = Module(main=True)
        p = self.fix.generate(p)

        code = self.gen.generate(p)
        self.assert_('__main__' in code)
        self.assert_('    pass' in code)

    def testContent(self):
        p = Module()
        p.content.append("a")
        self.assert_('a' in self.gen.generate(p))

        p = self.fix.generate(p)

        self.assert_('a' in self.gen.generate(p))

    def testContentExtended(self):
        p = Module()
        p.content.append(Function("function"))

        p = self.fix.generate(p)

        self.assert_('function' in self.gen.generate(p))


class TestForLoop(unittest.TestCase):

    def setUp(self):
        self.gen = CodeGenerator()
        self.fix = FixGenerator()

    def testEmptyForLoop(self):
        n = ForLoop("i", ["xrange(10)"], [])
        n = self.fix.generate(n)

        code = self.gen.generate(n)
        self.assert_("for i" in code)
        self.assert_("xrange(10):" in code)
        self.assert_("    pass" in code)

    def testStringForLoop(self):
        n = ForLoop("i", ["xrange(10)"], ['pass'])
        n = self.fix.generate(n)

        code = self.gen.generate(n)
        self.assert_("for i" in code)
        self.assert_("xrange(10):" in code)
        self.assert_("    pass" in code)


class TestIfStatement(unittest.TestCase):

    def setUp(self):
        self.gen = CodeGenerator()
        self.fix = FixGenerator()

    def testEmptyIfStatement(self):
        n = IfStatement("i", [])
        n = self.fix.generate(n)

        code = self.gen.generate(n)
        self.assert_("if i:" in code)
        self.assert_("pass" in code)

        n = IfStatement("i", [], [])
        n = self.fix.generate(n)

        code = self.gen.generate(n)
        self.assert_("if i:" in code)
        self.assert_("pass" in code)
        self.assert_("else:" in code)


class TestFunction(unittest.TestCase):

    def setUp(self):
        self.gen = CodeGenerator()
        self.fix = FixGenerator()

    def testEmptyFunction(self):
        n = Function("test")
        n = self.fix.generate(n)

        code = self.gen.generate(n)
        self.assert_("def test" in code)
        self.assert_("pass" in code)

    def testFunction(self):
        class TestStatement(Statement):

            def get(self):
                return "TestStatement"

            def fix(self):
                return self.get()

        def CallableStatement():
            return "CallableStatement"

        n = Function("test")
        n.content.append(TestStatement())
        n.content.append("StringStatement")
        n.content.append(CallableStatement)

        code = self.gen.generate(n)

        self.assert_("def test" in code)
        self.assert_("pass" not in code)

        self.assert_("TestStatement" in code)
        self.assert_("StringStatement" in code)
        self.assert_("CallableStatement" in code)

        # Now fix all statements

        n = self.fix.generate(n)

        code = self.gen.generate(n)

        self.assert_("def test" in code)
        self.assert_("pass" not in code)

        self.assert_("TestStatement" in code)
        self.assert_("StringStatement" in code)
        self.assert_("CallableStatement" in code)


class TestClass(unittest.TestCase):

    def setUp(self):
        self.gen = CodeGenerator()
        self.fix = FixGenerator()

    def testEmptyClass(self):
        n = Class('Test')
        n = self.fix.generate(n)

        code = self.gen.generate(n)
        self.assert_("class Test" in code)
        self.assert_("(object)" in code)
        self.assert_("pass" in code)

    def testClass(self):
        n = Class('Test')
        n.content.append('x = 5')
        n = self.fix.generate(n)

        code = self.gen.generate(n)
        self.assert_("class Test" in code)
        self.assert_("(object)" in code)
        self.assert_("pass" not in code)

    def testEmptyMethod(self):
        n = Method('test')
        n = self.fix.generate(n)

        code = self.gen.generate(n)
        self.assert_("def test" in code)
        self.assert_("(self)" in code)
        self.assert_("pass" in code)

    def testEmptyMethodWithAssignment(self):
        n = Method('test')
        n.content.append('x = 5')
        n = self.fix.generate(n)

        code = self.gen.generate(n)
        self.assert_("def test" in code)
        self.assert_("(self)" in code)
        self.assert_("pass" not in code)


class TestCallStatement(unittest.TestCase):

    def setUp(self):
        self.gen = CodeGenerator()
        self.fix = FixGenerator()

    def testCallStatement(self):
        func = Function("test")
        n = CallStatement(func, ['arg1', 'arg2'])
        n = self.fix.generate(n)

        code = self.gen.generate(n)

        self.assert_("test" in code)
        self.assert_("(arg1, arg2)" in code)


class TestAssignment(unittest.TestCase):

    def setUp(self):
        self.gen = CodeGenerator()
        self.fix = FixGenerator()

    def testAssignment(self):
        def CallableStatement():
            return "CallableStatement"

        n = Assignment("target", "=", [CallableStatement])

        code = self.gen.generate(n)

        self.assert_("target = CallableStatement" in code)

        n = self.fix.generate(n)
        code = self.gen.generate(n)

        self.assert_("target = CallableStatement" in code)


class TestFixGenerator(unittest.TestCase):

    def setUp(self):
        self.gen = FixGenerator()

    def testEmptyGenerator(self):
        try:
            self.gen.generate(None)
            self.fail()
        except:
            pass

    def testStatement(self):
        class TestStatement(Statement):

            def get(self):
                return "a"

            def fix(self):
                return "a"

        fixed = self.gen.visit(TestStatement())
        self.assertEqual(fixed, "a")

    def testVisitArgs(self):
        class TestStatement(Statement):

            def get(self):
                return "a"

            def fix(self):
                return "a"

        def func():
            return "c"

        fixed = self.gen.visit_args([func, 'b', TestStatement()])
        self.assert_("a" in fixed)
        self.assert_("b" in fixed)
        self.assert_("c" in fixed)

        fixed = self.gen.visit_args([['b']])
        self.assert_(isinstance(fixed[0], list))


class TestCodeGenerator(unittest.TestCase):

    def setUp(self):
        self.gen = CodeGenerator()

    def testEmptyGenerator(self):
        try:
            self.gen.generate(None)
            self.fail()
        except:
            pass

    def testCodeFunction(self):
        self.assertEqual(self.gen.code(4, 'a'), ('    '*4) + 'a')

    def testStatement(self):
        class TestStatement(Statement):

            def get(self):
                return "a"

        self.assert_("a" in self.gen.generate(TestStatement()))

    def testVisitArgs(self):
        code = self.gen.visit_args(['b'])
        self.assert_('b' in code)

        code = self.gen.visit_args([['b']])
        self.assert_('b' in code)

        def func():
            return "c"

        code = self.gen.visit_args([func])
        self.assert_('c' in code)

if __name__ == "__main__":
    unittest.main()
