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
    def __init__(self, pointer, iterable, content = None):
        self.pointer = pointer
        self.iterable = iterable
        if content != None:
            self.content = content
        else:
            self.content = []
        
        
class IfStatement(object):
    def __init__(self, clause, true_content = None, false_content = None):
        self.clause = clause
        if true_content != None:
            self.true_content = true_content
        else:
            self.true_content = []

        if false_content != None:
            self.false_content = false_content
        else:
            self.false_content = []

class Function(object):
    def __init__(self, name, args = None, content = None):
        self.name = name

        if args != None:
            self.args = args
        else:
            self.args = []

        if content != None:
            self.content = content
        else:
            self.content = []
        
class CallStatement(object):
    def __init__(self, func, args):
        self.func = func
        self.args = args

class Assignment(object):
    def __init__(self, target, operator, expression):
        self.target = target
        self.operator = operator
        self.expression = expression
        
class Statement(object):
    pass


class FixGenerator(object):
    def __init__(self):
        pass
    
    def visit_block(self, block):
        fixed = []
        for stmt in block:
            if isinstance(stmt, str):
                fixed.append(stmt)
                continue
            if callable(stmt):
                fixed.append(stmt())
                continue
            
            fixed.append(self.visit(stmt))
        return fixed
    
    def visit_args(self, args):
        fixed = []
        for arg in args:
            if isinstance(arg, str):
                fixed.append(arg)
                continue
            if callable(arg):
                fixed.append(arg())
                continue
         
            raise CodeGenException()
        return fixed
    
    def generate(self, node):
        return self.visit(node)
    
    @dispatch.on('node')
    def visit(self, node):
        pass
    
    @visit.when(Module)
    def visit(self, node):
        m = Module(node.has_main)
        m.content = self.visit_block(node.content)
        m.main_body = self.visit_block(node.main_body)
        
        return m

    @visit.when(Statement)
    def visit(self, node):
        return node.fix()
    
    @visit.when(CallStatement)
    def visit(self, node):
        stmt = CallStatement(node.func, 
                    self.visit_args(node.args))
        
        return stmt 

    @visit.when(Function)
    def visit(self, node):
        func = Function(node.name)
        func.args = self.visit_args(node.args)
        func.content = self.visit_block(node.content)
        
        return func

    @visit.when(IfStatement)
    def visit(self, node):
        stmt = IfStatement(node.clause)
        stmt.true_content = self.visit_block(node.true_content)
        stmt.false_content = self.visit_block(node.false_content)
        
        return stmt
        
    @visit.when(ForLoop)
    def visit(self, node):
        stmt = ForLoop(node.pointer, node.iterable, 
                       self.visit_block(node.content))
        
        return stmt
    
    @visit.when(Assignment)
    def visit(self, node):
        stmt = Assignment(node.target, node.operator, self.visit_block(node.expression))
        return stmt

class CodeGenerator(object):
    def __init__(self):
        pass
    
    def generate(self, node):
        code = self.visit(0, node)
        return "\n".join(code)
        
    def code(self, depth, line):
        code = []
        for i in xrange(depth):
            code.append('    ')
        if isinstance(line, list):
            line = "".join(line)
        code.append(line)
        
        return "".join(code)
    
    def visit_block(self, depth, block):
        if len(block) == 0:
            return [self.code(depth+1, 'pass')]

        content = []
        for node in block:
            if isinstance(node, str):
                content.append(self.code(depth+1, node))
                continue
            if callable(node):
                content.append(self.code(depth+1, node()))
                continue
            
            content += self.visit(depth+1, node)
        return content

    @dispatch.on('node')
    def visit(self, depth, node):
        '''Generic visit function'''
        return []
        
       
    @visit.when(Statement)
    def visit(self, depth, node):
        return [self.code(depth, node.get())]
       
    @visit.when(Module)
    def visit(self, depth, node):
        if depth != 0:
            raise CodeGenIndentException()
    
        content = []
        for n in node.content:
            if isinstance(n, str):
                content.append(self.code(depth, n))
                continue
            content += self.visit(depth, n)
    
        if node.has_main:
            content.append(self.code(depth, 'if __name__ == "__main__":'))
            content += self.visit_block(depth, node.main_body)
        return content

    @visit.when(ForLoop)
    def visit(self, depth, node):
        line = "".join(["for ", node.pointer, " in ", node.iterable, ":"])
        content = [self.code(depth, line)]
        content += self.visit_block(depth, node.content)
        return content


    @visit.when(IfStatement)
    def visit(self, depth, node):
        content = []
        content.append(self.code(depth, ["if ", node.clause, ":"]))
        content += self.visit_block(depth, node.true_content)
        content.append(self.code(depth, "else:"))
        content += self.visit_block(depth, node.false_content)
        return content
        

    @visit.when(Function)
    def visit(self, depth, node):
        args = ", ".join(node.args)
        fun = "".join(['def ', node.name, '(', args, '):'])
        content = [self.code(depth, fun)]
        content += self.visit_block(depth, node.content)
        return content

    @visit.when(CallStatement)
    def visit(self, depth, node):
        args = ", ".join(node.args)
        fun = "".join([node.func.name, '(', args, ')'])
        return [self.code(depth, fun)]

    @visit.when(Assignment)
    def visit(self, depth, node):
        code = [node.target, node.operator]
        if(len(node.expression) > 0):
            code += map(lambda x: x.strip(), self.visit_block(0, node.expression))
        return [self.code(depth, " ".join(code))]
