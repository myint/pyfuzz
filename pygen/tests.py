import unittest

from cgen import *

class TestModule(unittest.TestCase):

    def setUp(self):
        self.gen = CodeGenerator()
        self.fix = FixGenerator()

    def testEmptyModule(self):
        p = Module()
        p = self.fix.visit(p)
        self.gen.generate(p)
        
        self.assertEqual(self.gen.get_code(), '')
        
    def testEmptyMainModule(self):
        p = Module(main=True)
        p = self.fix.generate(p)
        self.gen.generate(p)
        
        code = self.gen.get_code()
        self.assert_('__main__' in code)
        self.assert_('    pass' in code)
        
    def testContent(self):
        p = Module()
        p.content.append("a")
        
        self.gen.generate(p)
        self.assert_('a' in self.gen.get_code())

class TestForLoop(unittest.TestCase):
    def setUp(self):
        self.gen = CodeGenerator()
        self.fix = FixGenerator()

    def testEmptyForLoop(self):
        n = ForLoop("i", "xrange(10)", [])
        n = self.fix.generate(n)
        self.gen.generate(n)
        
        code = self.gen.get_code()
        self.assert_("for i" in code)
        self.assert_("xrange(10):" in code)
        self.assert_("    pass" in code)

    
    def testStringForLoop(self):
        n = ForLoop("i", "xrange(10)", ['pass'])
        n = self.fix.generate(n)
        self.gen.generate(n)
        
        code = self.gen.get_code()
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
        self.gen.generate(n)
        
        code = self.gen.get_code()
        self.assert_("if i:" in code)
        self.assert_("pass" in code)

        n = IfStatement("i", [], [])
        n = self.fix.generate(n)
        self.gen.generate(n)
        
        code = self.gen.get_code()
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
        self.gen.generate(n)
        
        code = self.gen.get_code()
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

        self.gen.generate(n)
        code = self.gen.get_code()

        self.assert_("def test" in code)
        self.assert_("pass" not in code)
        
        self.assert_("TestStatement" in code)
        self.assert_("StringStatement" in code)
        self.assert_("CallableStatement" in code)

        # Now fix all statements
        
        n = self.fix.generate(n)
        self.gen.generate(n)
        code = self.gen.get_code()
        
        self.assert_("def test" in code)
        self.assert_("pass" not in code)
        
        self.assert_("TestStatement" in code)
        self.assert_("StringStatement" in code)
        self.assert_("CallableStatement" in code)

class TestCallStatement(unittest.TestCase):
    def setUp(self):
        self.gen = CodeGenerator()
        self.fix = FixGenerator()

    def testCallStatement(self):
        func = Function("test")
        n = CallStatement(func, ['arg1', 'arg2'])
        n = self.fix.generate(n)
        self.gen.generate(n)
        code = self.gen.get_code()
        
        self.assert_("test" in code)
        self.assert_("(arg1, arg2)" in code)


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


    
class TestCodeGenerator(unittest.TestCase):

    def setUp(self):
        self.gen = CodeGenerator()
    
    def testEmptyGenerator(self):
        self.assertEqual(self.gen.get_code(), '')
        
        try:
            self.gen.generate(None)
            self.fail()
        except:
            pass
        
    def testCodeFunction(self):
        self.gen.code(4, 'a')
        self.assertEqual(self.gen.get_code(), ('    '*4) + 'a')
        
    def testStatement(self):
        class TestStatement(Statement):
            def get(self):
                return "a"
            
        self.gen.generate(TestStatement())
        self.assert_("a" in self.gen.get_code())
        
#    def testListStrDispatch(self):
#        node = ['a' for i in xrange(4)]
#        self.gen.generate(node)
#        
#        self.assertEqual(len(self.gen.code_lines), 4)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    
    