
import inspect


class InvalidArgException(Exception):
    pass


class DispatchTargetException(Exception):
    pass


class Dispatcher(object):

    """General dispatcher object."""
    def __init__(self, name, argnum, args):
        self.name = name
        self.argnum = argnum
        self.args = args

        self.functions = []

    def get(self, args, kw):
        """Get function to dispatch to based on args and kw."""
        if self.name in kw:
            arg = kw[self.name]
        else:
            arg = args[self.argnum]

        for reg_arg, reg_func in self.functions:
            if isinstance(arg, reg_arg):
                return reg_func

        raise InvalidArgException(
            "No function found for type %s." %
            str(type(arg)))

    def register(self, func, arg):
        """Register a new function with the dispatcher."""
        args = inspect.getargspec(func)
        if args != self.args:
            raise DispatchTargetException(
                "Target arguments to not match with source.")

        self.functions.append((arg, func))


def on(name):
    """Dispatch on argument "name"."""
    def on_decorate(func):
        args = inspect.getargspec(func)
        argnum = args.args.index(name)

        dispatcher = Dispatcher(name, argnum, args)

        def decorator(*args, **kw):
            return dispatcher.get(args, kw)(*args, **kw)

        def when(arg):
            def when_decorate(func):
                dispatcher.register(func, arg)
                return decorator

            return when_decorate

        decorator.when = when

        return decorator

    return on_decorate
