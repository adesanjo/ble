from random import random
from copy import deepcopy
import os
import sys
import pathlib
import time

if os.name == "nt":
    import msvcrt  # pylint: disable=import-error
else:
    import atexit
    import termios
    from select import select

from error import RTError
import tokens as tok
from values import NoneValue, Number, String, Function, ReturnValue, List, Module, Class, BreakValue
import languageParser as lp
from languageLexer import Token, DIGITS
import language

################
# GETCH & KBHIT
################


class KBHit:
    
    def __init__(self):
        '''Creates a KBHit object that you can call to do various keyboard things.
        '''

        if os.name == "nt" or sys.platform == "ios":
            pass
        
        else:
    
            # Save the terminal settings
            self.fd = sys.stdin.fileno()
            self.new_term = termios.tcgetattr(self.fd)
            self.old_term = termios.tcgetattr(self.fd)
    
            # New terminal setting unbuffered
            self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
            self.set_getch_term()
    
            # Support normal-terminal reset at exit
            atexit.register(self.set_normal_term)
    
    
    def set_getch_term(self):
        ''' Resets to normal terminal.  On Windows this is a no-op.
        '''
        
        if os.name == "nt" or sys.platform == "ios":
            pass
        
        else:
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)
    
    
    def set_normal_term(self):
        ''' Resets to normal terminal.  On Windows this is a no-op.
        '''
        
        if os.name == "nt" or sys.platform == "ios":
            pass
        
        else:
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)


    def getch(self):
        ''' Returns a keyboard character after kbhit() has been called.
        '''
        if sys.platform == "ios":
            res = input()
        elif os.name == "nt":
            res = msvcrt.getch().decode('utf-8')
        else:
            res = sys.stdin.read(1)
            termios.tcflush(self.fd, termios.TCIFLUSH)
        return res
                        

    def kbhit(self):
        ''' Returns True if keyboard character was hit, False otherwise.
        '''
        if sys.platform == "ios":
            return False
        elif os.name == "nt":
            return msvcrt.kbhit()
        else:
            dr,_,_ = select([sys.stdin], [], [], 0)
            return dr != []


KB = KBHit()


################
# RUNTIME RESULT
################


class RTResult:
    def __init__(self):
        self.value = None
        self.err = None

    def register(self, res):
        if res.err:
            self.err = res.err
        return res.value

    def success(self, value):
        self.value = value
        return self

    def failure(self, err):
        self.err = err
        return self


################
# CONTEXT
################


class Context:
    def __init__(self, displayName, parent=None, parentEntryPos=None):
        self.displayName = displayName
        self.parent = parent
        self.parentEntryPos = parentEntryPos
        self.symbolTable = None
    
    def depth(self):
        if self.parent == None:
            return 1
        return 1 + self.parent.depth()
    
    def copy(self):
        res = Context(self.displayName, self.parent.copy() if self.parent else None, self.parentEntryPos.copy() if self.parentEntryPos else None)
        res.symbolTable = self.symbolTable.copy()
        return res
    
    def __repr__(self):
        return repr(self.symbolTable)


################
# SYMBOL TABLE
################


class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def get(self, name):
        value = self.symbols.get(name, None)
        if value is None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]
    
    def clear(self):
        self.symbols.clear()
    
    def copy(self):
        res = SymbolTable(self.parent.copy() if self.parent else None)
        res.symbols = deepcopy(self.symbols)
        return res

    def __repr__(self):
        res = repr(self.symbols)
        if self.parent:
            res += "\n" + repr(self.parent)
        return res


################
# INTERPRETER
################


BUILTINS = [
    "true",
    "false",
    "none",
    "module",
    "argv"
]


class Interpreter:
    def __init__(self, dev):
        self.dev = dev
    
    def visit(self, node, context):
        methodName = f"visit{type(node).__name__}"
        method = getattr(self, methodName, self.noVisitMethod)
        return method(node, context)

    def noVisitMethod(self, node, context):
        raise Exception(f"No visit{type(node).__name__} method defined")
    
    def visitClassNode(self, node, context):
        res = RTResult()
        
        className = node.varNameTkn.value
        if node.parentTkn:
            parent = context.symbolTable.get(node.parentTkn.value)
            if not isinstance(parent, Class):
                return res.failure(RTError(
                    node.parentTkn.startPos, node.parentTkn.endPos,
                    "Class parent must be a defined class",
                    context
                ))
            newContext = Context(className, parent.context, parent.startPos)
            newContext.symbolTable = SymbolTable(parent.context.symbolTable)
        else:
            parent = None
            newContext = Context(className)
            newContext.symbolTable = SymbolTable()
        
        bodyNode = node.bodyNode
        
        classValue = Class(
            className, parent, bodyNode, newContext
        ).setContext(context).setPos(node.startPos, node.endPos)
        classValue.initContext()

        if className not in BUILTINS:
            context.symbolTable.set(className, classValue)
        
        return res.success(classValue)
    
    def visitIncludeNode(self, node, context):
        res = RTResult()
        
        dir = os.path.normpath(os.path.dirname(node.startPos.fn))
        fStr = res.register(self.visit(node.fileNode, context))
        if res.err:
            return res
        if not isinstance(fStr, String):
            return res.failure(RTError(
                node.startPos, node.endPos,
                "Expected string after expression evaluation",
                context
            ))
        fn = os.path.normpath(dir + "/" + fStr.value + ".ble")
        if node.moduleName:
            moduleName = node.moduleName
        else:
            moduleName = os.path.basename(fStr.value)
        if not os.path.isfile(fn):
            if sys.platform == "ios":
                libDir = "lib/"
            elif self.dev:
                libDir = str(pathlib.Path.home()) + "/Documents/projects/ble/lib/"
            else:
                libDir = str(pathlib.Path.home()) + "/ble/ble-master/lib/"
            fn = os.path.normpath(libDir + fStr.value + ".ble")
            if not os.path.isfile(fn):
                return res.failure(RTError(
                    node.startPos, node.endPos,
                    f"File '{fn}' not found",
                    context
                ))
        
        if fn in node.startPos.module.split(" -> "):
            module = context.symbolTable.get(moduleName)
            if moduleName not in BUILTINS:
                context.symbolTable.set(moduleName,module)
            return res.success(moduleName)
        
        moduleContext = Context(moduleName, context, node.startPos)
        moduleContext.symbolTable = SymbolTable(context.symbolTable)
        module = Module(moduleContext).setContext(context).setPos(node.startPos, node.endPos)
        if moduleName not in BUILTINS:
            context.symbolTable.set(moduleName,module)
        with open(fn) as f:
            _, err = language.run(fn, f.read(), f"{node.startPos.module} -> {fn}", moduleContext)
        if err:
            return res.failure(err)
        moduleContext.parent = None
        moduleContext.parentEntryPos = None
        moduleContext.symbolTable.parent = None
        return res.success(module)
    
    def visitAccessNode(self, node, context):
        res = RTResult()
        
        module = res.register(self.visit(node.moduleNode, context))
        if res.err:
            return res
        value, err = module.access(node.varNameTkn)
        if err:
            return res.failure(err)
        
        return res.success(value)
    
    def visitTypeNode(self, node, context):
        res = RTResult()
        
        value = res.register(self.visit(node.valueNode, context))
        if res.err:
            return res
        
        if isinstance(value, Number) and isinstance(value.value, int):
            return res.success(String("int"))
        if isinstance(value, Number) and isinstance(value.value, float):
            return res.success(String("float"))
        if isinstance(value, String):
            return res.success(String("string"))
        if isinstance(value, List):
            return res.success(String("list"))
        if isinstance(value, Function):
            return res.success(String("function"))
        if isinstance(value, NoneValue):
            return res.success(String("none"))
        if isinstance(value, Module):
            return res.success(String("module"))
        if isinstance(value, Class):
            return res.success(String("class"))
        
        raise Exception("Type recognition not implemented")
    
    def visitNumberNode(self, node, context):
        return RTResult().success(
            Number(node.tkn.value).setContext(context).setPos(
                node.startPos, node.endPos
            )
        )
    
    def visitNoneValueNode(self, node, context):
        return RTResult().success(
            NoneValue().setContext(context).setPos(
                node.startPos, node.endPos
            )
        )

    def visitStringNode(self, node, context):
        return RTResult().success(
            String(node.tkn.value).setContext(context).setPos(
                node.startPos, node.endPos
            )
        )
    
    def visitListNode(self, node, context):
        res = RTResult()
        value = []
        for exprNode in node.exprNodes:
            value.append(res.register(self.visit(exprNode, context)))
            if res.err:
                return res
        return res.success(
            List(value).setContext(context).setPos(
                node.startPos, node.endPos
            )
        )
    
    def visitVarAccessNode(self, node, context):
        res = RTResult()
        varName = node.varNameTkn.value
        if varName in BUILTINS:
            if varName == "true":
                value = Number(1).setContext(context).setPos(
                    node.startPos, node.endPos
                )
            elif varName == "false":
                value = Number(0).setContext(context).setPos(
                    node.startPos, node.endPos
                )
            elif varName == "none":
                value = NoneValue().setContext(context).setPos(
                    node.startPos, node.endPos
                )
            elif varName == "module":
                value = String(node.startPos.module).setContext(context).setPos(
                    node.startPos, node.endPos
                )
            elif varName == "argv":
                value = List([String(arg) for arg in sys.argv[1:]]).setContext(context).setPos(
                    node.startPos, node.endPos
                )
            else:
                value = None
        else:
            value = context.symbolTable.get(varName)
        if value is None:
            return res.failure(RTError(
                node.startPos, node.endPos,
                f"{varName} is not defined",
                context
            ))
        value.setPos(node.startPos, node.endPos)

        return res.success(value)

    def visitVarAssignNode(self, node, context):
        res = RTResult()
        varName = node.varNameTkn.value
        value = res.register(self.visit(node.valueNode, context))
        if res.err:
            return res

        if varName not in BUILTINS:
            context.symbolTable.set(varName, value)
        return res.success(value)
    
    def visitBinOpNode(self, node, context):
        res = RTResult()

        left = res.register(self.visit(node.lNode, context))
        if res.err:
            return res
        
        if node.opTkn.matches(tok.TT_KEYWORD, "and") and left.isFalse():
            return res.success(Number(0).setContext(left.context).setPos(node.startPos, node.endPos))
        if node.opTkn.matches(tok.TT_KEYWORD, "or") and left.isTrue():
            return res.success(Number(1).setContext(left.context).setPos(node.startPos, node.endPos))
        
        right = res.register(self.visit(node.rNode, context))
        if res.err:
            return res

        err = None
        if node.opTkn.type == tok.TT_PLUS:
            result, err = left.addedTo(right)
        elif node.opTkn.type == tok.TT_MINUS:
            result, err = left.subbedBy(right)
        elif node.opTkn.type == tok.TT_MUL:
            result, err = left.multedBy(right)
        elif node.opTkn.type == tok.TT_DIV:
            result, err = left.divedBy(right)
        elif node.opTkn.type == tok.TT_MOD:
            result, err = left.moddedBy(right)
        elif node.opTkn.type == tok.TT_POW:
            result, err = left.powedBy(right)
        elif node.opTkn.type == tok.TT_EE:
            result, err = left.isEqual(right)
        elif node.opTkn.type == tok.TT_NE:
            result, err = left.isNotEqual(right)
        elif node.opTkn.type == tok.TT_LT:
            result, err = left.isLessThan(right)
        elif node.opTkn.type == tok.TT_GT:
            result, err = left.isGreaterThan(right)
        elif node.opTkn.type == tok.TT_LTE:
            result, err = left.isLessThanOrEqual(right)
        elif node.opTkn.type == tok.TT_GTE:
            result, err = left.isGreaterThanOrEqual(right)
        elif node.opTkn.matches(tok.TT_KEYWORD, "and"):
            result, err = left.boolAnd(right)
        elif node.opTkn.matches(tok.TT_KEYWORD, "or"):
            result, err = left.boolOr(right)

        if err:
            return res.failure(err)
        return res.success(result.setPos(node.startPos, node.endPos))

    def visitUnaryOpNode(self, node, context):
        res = RTResult()

        val = res.register(self.visit(node.node, context))
        if res.err:
            return res

        result = val
        err = None
        if node.opTkn.type == tok.TT_MINUS:
            result, err = Number(0).setContext(context).setPos(
                node.opTkn.startPos, node.opTkn.endPos).subbedBy(val)
        elif node.opTkn.type == tok.TT_PLUS:
            result, err = Number(0).setContext(context).setPos(
                node.opTkn.startPos, node.opTkn.endPos).addedTo(val)
        elif node.opTkn.matches(tok.TT_KEYWORD, "not"):
            result, err = val.boolNot()

        if err:
            return res.failure(err)
        return res.success(result.setPos(node.startPos, node.endPos))
    
    def visitListModifNode(self, node, context):
        res = RTResult()
        
        varName = node.varNameTkn.value
        listValue = context.symbolTable.get(varName)
        if listValue is None:
            return res.failure(RTError(
                node.varNameTkn.startPos, node.varNameTkn.endPos,
                f"{varName} is not defined",
                context
            ))
        listValue.setContext(context).setPos(node.startPos, node.endPos)
        subListValue = listValue
        subList = None
        
        value = res.register(self.visit(node.valueNode, context))
        if res.err:
            return res
        
        idxs = [res.register(self.visit(node.idxNode, context)) for node.idxNode in node.idxNodes]
        if res.err:
            return res
        for idx in idxs:
            if not (isinstance(idx, Number) and isinstance(idx.value, int)):
                return res.failure(RTError(
                    node.idxNode.startPos, node.idxNode.endPos,
                    "Index must be an int",
                    context
                ))
            if idx.value >= len(subListValue.value) or idx.value < -len(subListValue.value):
                return res.failure(RTError(
                    node.idxNode.startPos, node.idxNode.endPos,
                    "Index out of range",
                    context
                ))
            subList = subListValue
            subListValue = subListValue.value[idx.value]
        
        if subList:
            subList.value[idx.value] = value.copy()
        else:
            subListValue.value = value.value
        context.symbolTable.set(varName, listValue)
        return res.success(listValue)

    def visitIfNode(self, node, context):
        res = RTResult()

        for cond, expr in node.cases:
            condValue = res.register(self.visit(cond, context))
            if res.err:
                return res

            if condValue.isTrue():
                exprValue = res.register(self.visit(expr, context))
                if res.err:
                    return res
                return res.success(exprValue)

        if node.elseCase:
            elseValue = res.register(self.visit(node.elseCase, context))
            if res.err:
                return res
            return res.success(elseValue)

        return res.success(NoneValue().setContext(context).setPos(node.startPos, node.endPos))

    def visitForNode(self, node, context):
        res = RTResult()
        
        result = NoneValue().setContext(context).setPos(node.startPos, node.endPos)

        startValue = res.register(self.visit(node.startValueNode, context))
        if res.err:
            return res
        if not isinstance(startValue, Number) or not isinstance(startValue.value, int):
            return res.failure(RTError(
                node.startPos, node.endPos,
                "Expected int",
                context
            ))

        endValue = res.register(self.visit(node.endValueNode, context))
        if res.err:
            return res
        if not isinstance(endValue, Number) or not isinstance(endValue.value, int):
            return res.failure(RTError(
                node.startPos, node.endPos,
                "Expected int",
                context
            ))

        if node.stepValueNode:
            stepValue = res.register(self.visit(node.stepValueNode, context))
            if res.err:
                return res
        else:
            stepValue = Number(1)
        if not isinstance(stepValue, Number) or not isinstance(stepValue.value, int):
            return res.failure(RTError(
                node.startPos, node.endPos,
                "Expected int",
                context
            ))

        for i in range(startValue.value, endValue.value, stepValue.value):
            context.symbolTable.set(node.varNameTkn.value, Number(i))

            result = res.register(self.visit(node.bodyNode, context))
            if res.err:
                return res
            if isinstance(result, (ReturnValue, BreakValue)):
                break
        
        if isinstance(result, BreakValue):
            result = NoneValue().setContext(result.context).setPos(
                result.startPos, result.endPos
            )
        elif node.elseNode:
            result = res.register(self.visit(node.elseNode, context))
            if res.err:
                return res

        return res.success(result)
    
    def visitForEachNode(self, node, context):
        res = RTResult()
        
        result = NoneValue().setContext(context).setPos(node.startPos, node.endPos)

        listExpr = res.register(self.visit(node.listNode, context))
        if res.err:
            return res
        if not isinstance(listExpr, List) and not isinstance(listExpr, String):
            return res.failure(RTError(
                node.startPos, node.endPos,
                "Expected list or string in for each",
                context
            ))

        for elem in listExpr.value:
            if isinstance(elem, str):
                elem = String(elem)
            context.symbolTable.set(node.varNameTkn.value, elem)

            result = res.register(self.visit(node.bodyNode, context))
            if res.err:
                return res
            if isinstance(result, (ReturnValue, BreakValue)):
                break
        
        if isinstance(result, BreakValue):
            result = NoneValue().setContext(result.context).setPos(
                result.startPos, result.endPos
            )
        elif node.elseNode:
            result = res.register(self.visit(node.elseNode, context))
            if res.err:
                return res

        return res.success(result)

    def visitWhileNode(self, node, context):
        res = RTResult()
        
        result = NoneValue().setContext(context).setPos(node.startPos, node.endPos)

        while True:
            cond = res.register(self.visit(node.condNode, context))
            if res.err:
                return res

            if cond.isFalse():
                break

            result = res.register(self.visit(node.bodyNode, context))
            if res.err:
                return res
            if isinstance(result, (ReturnValue, BreakValue)):
                break
        
        if isinstance(result, BreakValue):
            result = NoneValue().setContext(result.context).setPos(
                result.startPos, result.endPos
            )
        elif node.elseNode:
            result = res.register(self.visit(node.elseNode, context))
            if res.err:
                return res

        return res.success(result)
    
    def visitBreakNode(self, node, context):
        return RTResult().success(
            BreakValue().setContext(context).setPos(
                node.startPos, node.endPos
            )
        )

    def visitFuncDefNode(self, node, context):
        res = RTResult()

        funcName = node.varNameTkn.value if node.varNameTkn else None
        bodyNode = node.bodyNode
        argNames = [argName.value for argName in node.argNameTkns]
        canMod = node.canMod
        isBuiltin = node.isBuiltin
        funcValue = Function(
            funcName, bodyNode, argNames, canMod, isBuiltin
        ).setContext(context).setPos(node.startPos, node.endPos)

        if node.varNameTkn and funcName not in BUILTINS:
            context.symbolTable.set(funcName, funcValue)

        return res.success(funcValue)

    def visitCallNode(self, node, context):
        res = RTResult()
        args = []

        valueToCall = res.register(self.visit(node.nodeToCall, context))
        if res.err:
            return res

        valueToCall.setPos(node.startPos, node.endPos)

        for argNode in node.argNodes:
            args.append(res.register(self.visit(argNode, context)))
            if res.err:
                return res
        
        callContext = context if valueToCall.context is None else valueToCall.context

        returnValue = res.register(valueToCall.execute(args, callContext, self.dev))
        if res.err:
            return res

        return res.success(returnValue)
    
    def visitReturnNode(self, node, context):
        res = RTResult()
        value = res.register(self.visit(node.exprNode, context))
        if res.err:
            return res
        return res.success(
            ReturnValue(value).setContext(context).setPos(
                node.startPos, node.endPos
            )
        )
    
    def visitBlockNode(self, node, context):
        res = RTResult()

        exprValue = NoneValue().setContext(context).setPos(node.startPos, node.endPos)
        for exprNode in node.exprNodes:
            exprValue = res.register(self.visit(exprNode, context))
            if res.err:
                return res
            if isinstance(exprValue, ReturnValue) or isinstance(exprValue, BreakValue):
                break
            
        return res.success(exprValue)
    
    def visitDispNode(self, node, context):
        res = RTResult()

        exprValue = res.register(self.visit(node.bodyNode, context))
        if res.err:
            return res

        print(exprValue, end="\n" if node.newLine else "")
        return res.success(exprValue)
    
    def isNum(self, s):
        for c in s:
            if c not in DIGITS:
                return False
        return True
    
    def visitInputNode(self, node, context):
        res = RTResult()
        KB.set_normal_term()
        val = input()
        KB.set_getch_term()
        if not self.isNum(val.replace(".", "", 1)) or len(val) == 0:
            return res.success(String(val).setContext(context).setPos(node.startPos, node.endPos))
        if "." in val:
            return res.success(Number(float(val)).setContext(context).setPos(node.startPos, node.endPos))
        return res.success(Number(int(val)).setContext(context).setPos(node.startPos, node.endPos))
    
    def visitGetchNode(self, node, context):
        return RTResult().success(String(KB.getch()).setContext(context).setPos(node.startPos, node.endPos))
    
    def visitKbhitNode(self, node, context):
       return RTResult().success(Number(1 if KB.kbhit() else 0).setContext(context).setPos(node.startPos, node.endPos))
    
    def visitRandNode(self, node, context):
        res = RTResult()
        return res.success(Number(random()))
    
    def visitIntCastNode(self, node, context):
        res = RTResult()
        expr = res.register(self.visit(node.exprNode, context))
        if res.err:
            return res
        canCast = True
        if not isinstance(expr, Number):
            canCast = False
        if isinstance(expr, String) and self.isNum(expr.value) and len(expr.value) > 0:
            canCast = True
        if not canCast:
            return res.failure(RTError(
                node.startPos, node.endPos,
                "Cannot cast to integer",
                context
            ))
        return res.success(Number(int(expr.value)))
    
    def visitFloatCastNode(self, node, context):
        res = RTResult()
        expr = res.register(self.visit(node.exprNode, context))
        if res.err:
            return res
        canCast = True
        if not isinstance(expr, Number):
            canCast = False
        if isinstance(expr, String) and self.isNum(expr.value.replace(".", "", 1)) and len(expr.value) > 0:
            canCast = True
        if not canCast:
            return res.failure(RTError(
                node.startPos, node.endPos,
                "Cannot cast to float",
                context
            ))
        return res.success(Number(float(expr.value)))
    
    def visitStrCastNode(self, node, context):
        res = RTResult()
        expr = res.register(self.visit(node.exprNode, context))
        if res.err:
            return res
        return res.success(String(str(expr.value)))
    
    def visitReadNode(self, node, context):
        res = RTResult()
        
        fileName = res.register(self.visit(node.fileNameNode, context))
        if res.err:
            return res
        if not isinstance(fileName, String):
            return res.failure(RTError(
                node.fileNameNode.startPos, node.fileNameNode.endPos,
                "File name must be a string",
                context
            ))
        
        dir = os.path.normpath(os.path.dirname(node.startPos.fn))
        fn = os.path.normpath(dir + "/" + fileName.value)
        if not os.path.isfile(fn):
            return res.failure(RTError(
                node.fileNameNode.startPos, node.fileNameNode.endPos,
                f"File {fileName} not found",
                context
            ))
        
        if node.byteMode:
            with open(fn, "rb") as f:
                result = List([Number(i) for i in list(f.read())])
        else:
            try:
                with open(fn, "r") as f:
                    result = String(f.read())
            except UnicodeDecodeError:
                return res.failure(RTError(
                    node.fileNameNode.startPos, node.fileNameNode.endPos,
                    f"File {fileName} could not be read as text",
                    context
                ))
        
        return res.success(result)
    
    def visitWriteNode(self, node, context):
        res = RTResult()
        
        fileName = res.register(self.visit(node.fileNameNode, context))
        if res.err:
            return res
        if not isinstance(fileName, String):
            return res.failure(RTError(
                node.fileNameNode.startPos, node.fileNameNode.endPos,
                "File name must be a string",
                context
            ))
        
        dir = os.path.normpath(os.path.dirname(node.startPos.fn))
        fn = os.path.normpath(dir + "/" + fileName.value)
        
        fileContent = res.register(self.visit(node.fileContentNode, context))
        if res.err:
            return res
        
        if node.byteMode:
            if not (isinstance(fileContent, List) and all(isinstance(num, Number) and num.value in range(256) for num in fileContent.value)):
                return res.failure(RTError(
                    node.fileContentNode.startPos, node.fileContentNode.endPos,
                    "File content must be a list of integers from 0 to 255",
                    context
                ))
            try:
                with open(fn, "wb") as f:
                    f.write(bytes([num.value for num in fileContent.value]))
            except FileNotFoundError:
                return res.failure(RTError(
                    node.fileContentNode.startPos, node.fileContentNode.endPos,
                    f"File {fileName} could not be created. No such directory",
                    context
                ))
        else:
            if not isinstance(fileContent, String):
                return res.failure(RTError(
                    node.fileContentNode.startPos, node.fileNameNode.endPos,
                    "File content must be a string",
                    context
                ))
            try:
                with open(fn, "w") as f:
                    f.write(fileContent.value)
            except FileNotFoundError:
                return res.failure(RTError(
                    node.fileContentNode.startPos, node.fileNameNode.endPos,
                    f"File {fileName} could not be created. No such directory",
                    context
                ))
        
        return res.success(fileContent)
    
    def visitClsNode(self, node, context):
        os.system("cls" if os.name == "nt" else "clear")
        return RTResult().success(NoneValue().setContext(context).setPos(node.startPos, node.endPos))
    
    def visitTimeNode(self, node, context):
        t = round(time.time() * 1000000)
        return RTResult().success(
            Number(t).setContext(context).setPos(node.startPos, node.endPos)
        )
    
    def visitCLINode(self, node, context):
        res = RTResult()
        cmd = res.register(self.visit(node.cmdNode, context))
        if res.err:
            return res
        if not isinstance(cmd, String):
            return res.failure(RTError(
                node.startPos, node.endPos,
                "CLI command must be a string value",
                context
            ))
        os.system(cmd.value)
        return res.success(
            NoneValue().setContext(context).setPos(node.startPos, node.endPos)
        )
    
    def visitOSNode(self, node, context):
        return RTResult().success(
            String(sys.platform).setContext(context).setPos(node.startPos, node.endPos)
        )
