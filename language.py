from languageInterpreter import SymbolTable, Number, Interpreter, Context
from languageLexer import Lexer
from languageParser import Parser

"""
Best Language Ever
extension: .ble
"""

################
# RUN
################

globalSymbolTable = SymbolTable()
globalSymbolTable.set("true", Number(1))
globalSymbolTable.set("false", Number(0))


def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, err = lexer.makeTokens()
    if err is not None:
        return None, err

    parser = Parser(tokens)
    ast = parser.parse()
    if ast.err:
        return None, ast.err

    interpreter = Interpreter()
    context = Context("<program>")
    context.symbolTable = globalSymbolTable
    res = interpreter.visit(ast.node, context)

    return res.value, res.err
