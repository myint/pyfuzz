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
        
#    def testListStrDispatch(self):
#        node = ['a' for i in xrange(4)]
#        self.gen.generate(node)
#        
#        self.assertEqual(len(self.gen.code_lines), 4)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    
    