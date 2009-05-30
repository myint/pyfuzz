import dispatch

class CodeGenException(Exception):
    pass

class CodeGenIndentException(CodeGenException):
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
        
        
class IfStatement(object):
    def __init__(self, clause, true_content = [], false_content = []):
        self.clause = clause
        self.true_content = true_content
        self.false_content = false_content

class Function(object):
    def __init__(self, name, args=[], content=[]):
        self.name = name
        self.args = args
        self.content = content
        
class CallStatement(object):
    def __init__(self, func, args=[]):
        self.func = func
        self.args = args
        
class Statement(object):
    pass

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
        if isinstance(line, list):
            line = "".join(line)
        code.append(line)
        
        self.code_lines.append("".join(code))
    
    def visit_block(self, depth, block):
        if len(block) == 0:
            self.code(depth+1, 'pass')
            return
        
        for node in block:
            if isinstance(node, str):
                self.code(depth+1, node)
                continue
            if callable(node):
                self.code(depth+1, node())
                continue
            
            self.visit(depth+1, node)

#    def visit_list(self, depth, node):
#        for line in node:
#            self.code(depth, line)

    
    @dispatch.on('node')
    def visit(self, depth, node):
        '''Generic visit function'''
        pass
        
       
    @visit.when(Statement)
    def visit(self, depth, node):
        self.code(depth, node.get())
       
    @visit.when(Module)
    def visit(self, depth, node):
        if depth != 0:
            raise CodeGenIndentException()
    
        for n in node.content:
            if isinstance(n, str):
                self.code(depth, n)
                continue
            self.visit(depth, n)
    
        if node.has_main:
            self.code(depth, 'if __name__ == "__main__":')
            self.visit_block(depth, node.main_body)
            

    @visit.when(ForLoop)
    def visit(self, depth, node):
        line = "".join(["for ", node.pointer, " in ", node.iterable, ":"])
        self.code(depth, line)
        self.visit_block(depth, node.content)


    @visit.when(IfStatement)
    def visit(self, depth, node):
        self.code(depth, ["if ", node.clause, ":"])
        self.visit_block(depth, node.true_content)
        self.code(depth, "else:")
        self.visit_block(depth, node.false_content)
        

    @visit.when(Function)
    def visit(self, depth, node):
        args = ", ".join(node.args)
        fun = "".join(['def ', node.name, '(', args, '):'])
        self.code(depth, fun)
        self.visit_block(depth, node.content)


    @visit.when(CallStatement)
    def visit(self, depth, node):
        args = ", ".join(node.args)
        fun = "".join([node.func.name, '(', args, ')'])
        self.code(depth, fun)
        
        


    
