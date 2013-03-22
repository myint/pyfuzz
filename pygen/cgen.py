from . import qndispatch as dispatch


try:
    basestring
except NameError:
    basestring = str


class CodeGenException(Exception):
    pass


class CodeGenIndentException(CodeGenException):
    pass


class NotImplementedException(Exception):
    pass


class Module(object):

    """Outermost Code block representing a Python Module.

    May include a main block

    """
    def __init__(self, main=False):
        self.has_main = main
        self.main_body = []

        self.content = []


class ForLoop(object):

    def __init__(self, pointer, iterable, content=None):
        self.pointer = pointer
        self.iterable = iterable
        if content is not None:
            self.content = content
        else:
            self.content = []


class IfStatement(object):

    def __init__(self, clause, true_content=None, false_content=None):
        self.clause = clause
        if true_content is not None:
            self.true_content = true_content
        else:
            self.true_content = []

        if false_content is not None:
            self.false_content = false_content
        else:
            self.false_content = []


class Function(object):

    def __init__(self, name, args=None, content=None):
        self.name = name

        if args is not None:
            self.args = args
        else:
            self.args = []

        if content is not None:
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

    """Generic statement.

    To be overridden.

    """

    def get(self):
        raise NotImplementedException

    def fix(self):
        raise NotImplementedException


class Class(object):

    def __init__(self, name, super=None, content=None):
        self.name = name
        if super:
            self.super = super
        else:
            self.super = ['object']

        if content:
            self.content = content
        else:
            self.content = []


class Method(object):

    def __init__(self, name, args=None, content=None):
        self.name = name

        self.args = []
        if args is not None:
            self.args = args

        if content is not None:
            self.content = content
        else:
            self.content = []


class FixGenerator(object):

    def __init__(self):
        pass

    def visit_block(self, block):
        fixed = []
        for stmt in block:
            if isinstance(stmt, str):
                fixed.append(stmt)
                continue

            if isinstance(stmt, list):
                fixed.append(self.visit_args(list))
                continue

            if callable(stmt):
                fixed.append(stmt())
                continue

            fixed.append(self.visit(stmt))
        return fixed

    def visit_args(self, args):
        return [self.visit_expr(arg) for arg in args]

    def visit_expr(self, expr):
        if isinstance(expr, str):
            return expr

        if isinstance(expr, list):
            return self.visit_args(expr)

        if callable(expr):
            return expr()

        return self.visit(expr)

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

    @visit.when(Class)
    def visit(self, node):
        c = Class(node.name)
        c.super = self.visit_args(node.super)
        c.content = self.visit_block(node.content)

        return c

    @visit.when(Method)
    def visit(self, node):
        m = Method(node.name)
        m.args = self.visit_args(node.args)
        m.content = self.visit_block(node.content)
        return m

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
        stmt = Assignment(
            node.target,
            node.operator,
            self.visit_block(
                node.expression))
        return stmt


class CodeGenerator(object):

    def __init__(self):
        pass

    def generate(self, node):
        code = self.visit(0, node)
        return "\n".join(code)

    def code(self, depth, line):
        code = []
        for i in range(depth):
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

    def visit_args(self, args):
        content = []
        for arg in args:
            if isinstance(arg, str):
                content.append(self.code(0, arg))
                continue

            if isinstance(arg, list):
                content.append("".join(self.visit_args(arg)))
                continue

            if callable(arg):
                content.append(self.code(0, arg()))
                continue

            content += self.visit(0, arg)
        return content

    @dispatch.on('node')
    def visit(self, depth, node):
        """Generic visit function."""
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
        iterable = " ".join(self.visit_args(node.iterable))
        line = "".join(["for ", node.pointer, " in ", iterable, ":"])
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
        if node.args:
            args = ", ".join(node.args)
        else:
            args = ""

        fun = "".join(['def ', node.name, '(', args, '):'])
        content = [self.code(depth, fun)]
        content += self.visit_block(depth, node.content)
        return content

    @visit.when(Class)
    def visit(self, depth, node):
        superclasses = ", ".join(node.super)
        c = "".join(['class ', node.name, '(', superclasses, '):'])
        content = [self.code(depth, c)]
        content += self.visit_block(depth, node.content)

        return content

    @visit.when(Method)
    def visit(self, depth, node):
        if node.args:
            args = ", ".join(["self"] + node.args)
        else:
            args = "self"

        fun = ''.join(['def ', node.name, '(', args, '):'])
        content = [self.code(depth, fun)]
        content += self.visit_block(depth, node.content)

        return content

    @visit.when(CallStatement)
    def visit(self, depth, node):
        args = ", ".join(self.visit_args(node.args))

        if isinstance(node.func, basestring):
            fun = "".join([node.func, '(', args, ')'])
        else:
            fun = "".join([node.func.name, '(', args, ')'])
        return [self.code(depth, fun)]

    @visit.when(Assignment)
    def visit(self, depth, node):
        code = [node.target, node.operator]
        if(len(node.expression) > 0):
            code += map(
                lambda x: x.strip(),
                self.visit_block(0,
                                 node.expression))
        return [self.code(depth, " ".join(code))]
