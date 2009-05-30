import unittest

from cgen import *

class TestModule(unittest.TestCase):

    def setUp(self):
        self.gen = CodeGenerator()

    def testEmptyModule(self):
        p = Module()
        self.gen.generate(p)
        
        self.assertEqual(self.gen.get_code(), '')
        
    def testEmptyMainModule(self):
        p = Module(main=True)
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

    def testEmptyForLoop(self):
        n = ForLoop("i", "xrange(10)", [])
        self.gen.generate(n)
        
        code = self.gen.get_code()
        self.assert_("for i" in code)
        self.assert_("xrange(10):" in code)
        self.assert_("    pass" in code)

    
    def testStringForLoop(self):
        n = ForLoop("i", "xrange(10)", ['pass'])
        self.gen.generate(n)
        
        code = self.gen.get_code()
        self.assert_("for i" in code)
        self.assert_("xrange(10):" in code)
        self.assert_("    pass" in code)

class TestIfStatement(unittest.TestCase):
    def setUp(self):
        self.gen = CodeGenerator()

    def testEmptyIfStatement(self):
        n = IfStatement("i", [])
        self.gen.generate(n)
        
        code = self.gen.get_code()
        self.assert_("if i:" in code)
        self.assert_("pass" in code)

        n = IfStatement("i", [], [])
        self.gen.generate(n)
        
        code = self.gen.get_code()
        self.assert_("if i:" in code)
        self.assert_("pass" in code)
        self.assert_("else:" in code)

class TestFunction(unittest.TestCase):
    def setUp(self):
        self.gen = CodeGenerator()

    def testEmptyFunction(self):
        n = Function("test")
        self.gen.generate(n)
        
        code = self.gen.get_code()
        self.assert_("def test" in code)
        self.assert_("pass" in code)

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
    
    