from random import random
import os
import sys
import pathlib

from error import RTError
import tokens as tok
from values import NoneValue, Number, String, Function, List, Module
import languageParser as lp
from languageLexer import Token, DIGITS
import language

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
            if self.dev:
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
            return res.failure(RTError(
                node.startPos, node.endPos,
                "Cyclic include chain detected",
                context
            ))
        
        moduleContext = Context(moduleName)
        moduleContext.symbolTable = SymbolTable()
        with open(fn) as f:
            result, err = language.run(fn, f.read(), f"{node.startPos.module} -> {fn}", moduleContext)
        if err:
            return res.failure(err)
        
        if moduleName not in BUILTINS:
            context.symbolTable.set(moduleName,
                Module(moduleContext).setContext(context).setPos(node.startPos, node.endPos)
            )
        return res.success(result)
    
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
        return res.success(List(value))
    
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
            subListValue = subListValue.value[idx.value]
        
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

        startValue = res.register(self.visit(node.startValueNode, context))
        if res.err:
            return res

        endValue = res.register(self.visit(node.endValueNode, context))
        if res.err:
            return res

        if node.stepValueNode:
            stepValue = res.register(self.visit(node.stepValueNode, context))
            if res.err:
                return res
        else:
            stepValue = Number(1)

        for i in range(startValue.value, endValue.value, stepValue.value):
            context.symbolTable.set(node.varNameTkn.value, Number(i))

            res.register(self.visit(node.bodyNode, context))
            if res.err:
                return res

        return res.success(NoneValue().setContext(context).setPos(node.startPos, node.endPos))
    
    def visitForEachNode(self, node, context):
        res = RTResult()

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

            res.register(self.visit(node.bodyNode, context))
            if res.err:
                return res

        return res.success(NoneValue().setContext(context).setPos(node.startPos, node.endPos))

    def visitWhileNode(self, node, context):
        res = RTResult()

        while True:
            cond = res.register(self.visit(node.condNode, context))
            if res.err:
                return res

            if cond.isFalse():
                break

            res.register(self.visit(node.bodyNode, context))
            if res.err:
                return res

        return res.success(NoneValue().setContext(context).setPos(node.startPos, node.endPos))

    def visitFuncDefNode(self, node, context):
        res = RTResult()

        funcName = node.varNameTkn.value if node.varNameTkn else None
        bodyNode = node.bodyNode
        argNames = [argName.value for argName in node.argNameTkns]
        funcValue = Function(
            funcName, bodyNode, argNames
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

        returnValue = res.register(valueToCall.execute(args, context, self.dev))
        if res.err:
            return res

        return res.success(returnValue)
    
    def visitBlockNode(self, node, context):
        res = RTResult()

        exprValue = NoneValue().setContext(context).setPos(node.startPos, node.endPos)
        for exprNode in node.exprNodes:
            exprValue = res.register(self.visit(exprNode, context))
            if res.err:
                return res
            
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
        val = input()
        if not self.isNum(val.replace(".", "", 1)) or len(val) == 0:
            return res.success(String(val))
        if "." in val:
            return res.success(Number(float(val)))
        return res.success(Number(int(val)))
    
    def visitRandNode(self, node, context):
        res = RTResult()
        return res.success(Number(random()))
    
    def visitIntCastNode(self, node, context):
        res = RTResult()
        expr = res.register(self.visit(node.exprNode, context))
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
        return res.success(String(str(expr.value)))
