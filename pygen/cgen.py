import dispatch

class CodeGenException(Exception):
    pass

class CodeGenIdentException(CodeGenException):
    pass

class Module(object):
    '''Outermost Code block representing a Python Module. May include a main block'''
    def __init__(self, main = False):
        self.has_main = main
        self.main_body = []
        
        self.content = []
        

class ForLoop(object):
    def __init__(self, pointer, iterable, content):
        self.pointer = pointer
        self.iterable = iterable
        self.content = content
        
        
class CodeGenerator(object):
    
    def __init__(self):
        self.code_lines = []

    def get_code(self):
        return "\n".join(self.code_lines)
    
    def generate(self, node):
        self.code_lines = []
        self.visit(0, node)
        
    def code(self, depth, line):
        code = []
        for i in xrange(depth):
            code.append('    ')
        code.append(line)
        
        self.code_lines.append("".join(code))
    
    def visit_block(self, depth, block):
        if len(block) == 0:
            self.code(depth+1, 'pass')
            return
        
        for node in block:
            self.visit(depth+1, node)

#    def visit_list(self, depth, node):
#        for line in node:
#            self.code(depth, line)

    
    @dispatch.on('node')
    def visit(self, depth, node):
        '''Generic visit function'''
        pass
        
       
    @visit.when(Module)
    def visit(self, depth, node):
        if depth != 0:
            raise CodeGenIdentException()
    
        if node.has_main:
            self.code(depth, 'if __name__ == "__main__":')
            self.visit_block(depth, node.main_body)
            

    @visit.when(ForLoop)
    def visit(self, depth, node):
        line = "".join(["for ", node.pointer, " in ", node.iterable, ":"])
        self.code(depth, line)
        self.visit_block(depth, node.content)










    
