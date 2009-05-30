from pygen.cgen import *


def _main():
    gen = CodeGenerator()
    
    mod = Module(main = True)
    mod.main_body.append("x = 5")
    mod.main_body.append(ForLoop('i', 'xrange(20)', 
            [IfStatement("i > x", ['x += 2'], ['x -= 3'])
             
             
             ]))
    
    gen.generate(mod)
    
    print gen.get_code()

if __name__ == '__main__':
    _main()