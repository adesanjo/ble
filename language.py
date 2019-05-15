from languageInterpreter import SymbolTable, Number, Interpreter, Context
from languageLexer import Lexer
from languageParser import Parser
import error

"""
Best Language Ever
extension: .ble
"""

################
# RUN
################

globalSymbolTable = SymbolTable()


def run(fn, text, module="<main>", context=None, dev=False):
    try:
        lexer = Lexer(fn, text, module)
        tokens, err = lexer.makeTokens()
        if err is not None:
            return None, err

        parser = Parser(tokens)
        ast = parser.parse()
        if ast.err:
            return None, ast.err

        interpreter = Interpreter(dev)
        if context is None:
            context = Context("<program>")
            context.symbolTable = globalSymbolTable
        res = interpreter.visit(ast.node, context)

        return res.value, res.err
    except KeyboardInterrupt:
        return None, " Keyboard Interrupt"
