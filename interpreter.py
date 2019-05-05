from error import RTError
import tokens as tok

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
# VALUES
################


class Value:
    def __init__(self):
        self.setPos()
        self.setContext()

    def setPos(self, startPos=None, endPos=None):
        self.startPos = startPos
        self.endPos = endPos
        return self

    def setContext(self, context=None):
        self.context = context
        return self

    def addedTo(self, other):
        return None, self.illegalOperation(other)

    def subbedBy(self, other):
        return None, self.illegalOperation(other)

    def multedBy(self, other):
        return None, self.illegalOperation(other)

    def divedBy(self, other):
        return None, self.illegalOperation(other)

    def powedBy(self, other):
        return None, self.illegalOperation(other)

    def isEqual(self, other):
        return None, self.illegalOperation(other)

    def isNotEqual(self, other):
        return None, self.illegalOperation(other)

    def isLessThan(self, other):
        return None, self.illegalOperation(other)

    def isGreaterThan(self, other):
        return None, self.illegalOperation(other)

    def isLessThanOrEqual(self, other):
        return None, self.illegalOperation(other)

    def isGreaterThanOrEqual(self, other):
        return None, self.illegalOperation(other)

    def isTrue(self):
        return None, self.illegalOperation()

    def isFalse(self):
        return None, self.illegalOperation()

    def boolAnd(self, other):
        return None, self.illegalOperation(other)

    def boolOr(self, other):
        return None, self.illegalOperation(other)

    def boolNot(self):
        return None, self.illegalOperation()

    def execute(self, args):
        return None, self.illegalOperation()

    def illegalOperation(self, other=None):
        if other is None:
            other = self
        return RTError(
            self.startPos, other.endPos,
            "Illegal operation",
            self.context
        )

    def copy(self):
        raise Exception("No copy method defined")


class Number(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def addedTo(self, other):
        if isinstance(other, Number):
            return Number(
                self.value + other.value
            ).setContext(self.context), None
        if isinstance(other, String):
            return Number(
                self.value + len(other.value)
            ).setContext(self.context), None
        return None, self.illegalOperation(other)

    def subbedBy(self, other):
        if isinstance(other, Number):
            return Number(
                self.value - other.value
            ).setContext(self.context), None
        return None, self.illegalOperation(other)

    def multedBy(self, other):
        if isinstance(other, Number):
            return Number(
                self.value * other.value
            ).setContext(self.context), None
        if isinstance(other, String) and isinstance(self.value, int):
            return String(
                other.value * self.value
            ).setContext(self.context), None
        return None, self.illegalOperation(other)

    def divedBy(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.startPos, other.endPos,
                    "Division by zero",
                    self.context
                )
            return Number(
                self.value / other.value
            ).setContext(self.context), None
        return None, self.illegalOperation(other)

    def moddedBy(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.startPos, other.endPos,
                    "Modulo by zero",
                    self.context
                )
            return Number(
                self.value % other.value
            ).setContext(self.context), None
        return None, self.illegalOperation(other)

    def powedBy(self, other):
        if isinstance(other, Number):
            return Number(
                self.value ** other.value
            ).setContext(self.context), None
        return None, self.illegalOperation(other)

    def isEqual(self, other):
        if isinstance(other, Number):
            return Number(
                1 if self.value == other.value else 0
            ).setContext(self.context), None
        if isinstance(other, String) and isinstance(self.value, int):
            return Number(
                1 if self.value == len(other.value) else 0
            ).setContext(self.context), None
        return None, self.illegalOperation(other)

    def isNotEqual(self, other):
        if isinstance(other, Number):
            return Number(
                1 if self.value != other.value else 0
            ).setContext(self.context), None
        if isinstance(other, String) and isinstance(self.value, int):
            return Number(
                1 if self.value != len(other.value) else 0
            ).setContext(self.context), None
        return None, self.illegalOperation(other)

    def isLessThan(self, other):
        if isinstance(other, Number):
            return Number(
                1 if self.value < other.value else 0
            ).setContext(self.context), None
        if isinstance(other, String) and isinstance(self.value, int):
            return Number(
                1 if self.value < len(other.value) else 0
            ).setContext(self.context), None
        return None, self.illegalOperation(other)

    def isGreaterThan(self, other):
        if isinstance(other, Number):
            return Number(
                1 if self.value > other.value else 0
            ).setContext(self.context), None
        if isinstance(other, String) and isinstance(self.value, int):
            return Number(
                1 if self.value > len(other.value) else 0
            ).setContext(self.context), None
        return None, self.illegalOperation(other)

    def isLessThanOrEqual(self, other):
        if isinstance(other, Number):
            return Number(
                1 if self.value <= other.value else 0
            ).setContext(self.context), None
        if isinstance(other, String) and isinstance(self.value, int):
            return Number(
                1 if self.value <= len(other.value) else 0
            ).setContext(self.context), None
        return None, self.illegalOperation(other)

    def isGreaterThanOrEqual(self, other):
        if isinstance(other, Number):
            return Number(
                1 if self.value >= other.value else 0
            ).setContext(self.context), None
        if isinstance(other, String) and isinstance(self.value, int):
            return Number(
                1 if self.value >= len(other.value) else 0
            ).setContext(self.context), None
        return None, self.illegalOperation(other)

    def isTrue(self):
        return self.value != 0

    def isFalse(self):
        return self.value == 0

    def boolAnd(self, other):
        if isinstance(other, Number):
            return Number(
                1 if self.value != 0 and other.value != 0 else 0
            ).setContext(self.context), None
        return None, self.illegalOperation(other)

    def boolOr(self, other):
        if isinstance(other, Number):
            return Number(
                1 if self.value != 0 or other.value != 0 else 0
            ).setContext(self.context), None
        return None, self.illegalOperation(other)

    def boolNot(self):
        return Number(
            1 if self.value == 0 else 0
        ).setContext(self.context), None

    def copy(self):
        copy = Number(self.value)
        copy.setPos(self.startPos, self.endPos)
        copy.setContext(self.context)
        return copy

    def __repr__(self):
        return str(self.value)


class String(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def addedTo(self, other):
        if isinstance(other, String):
            return String(
                self.value + other.value
            ).setContext(self.context), None
        if isinstance(other, Number):
            return Number(
                len(self.value) + other.value
            ).setContext(self.context), None
        return None, self.illegalOperation(other)

    def subbedBy(self, other):
        if isinstance(other, Number) and isinstance(other.value, int):
            return String(
                self.value[:-other.value] if other.value > 0 else self.value
            ).setContext(self.context), None
        return None, self.illegalOperation(other)

    def multedBy(self, other):
        if isinstance(other, Number) and isinstance(other.value, int):
            return String(
                self.value * other.value
            ).setContext(self.context), None
        return None, self.illegalOperation(other)

    def moddedBy(self, other):
        if isinstance(other, Number) and isinstance(other.value, int):
            if other.value >= len(self.value) or other.value < -len(self.value):
                return None, RTError(
                    other.startPos, other.endPos,
                    "Index out of range",
                    self.context
                )
            return String(
                self.value[other.value]
            ).setContext(self.context), None
        return None, self.illegalOperation(other)

    def isEqual(self, other):
        if isinstance(other, String):
            return Number(
                1 if self.value == other.value else 0
            ).setContext(self.context), None
        if isinstance(other, Number) and isinstance(other.value, int):
            return Number(
                1 if len(self.value) == other.value else 0
            ).setContext(self.context), None
        return None, self.illegalOperation(other)

    def isNotEqual(self, other):
        if isinstance(other, String):
            return Number(
                1 if self.value != other.value else 0
            ).setContext(self.context), None
        if isinstance(other, Number) and isinstance(other.value, int):
            return Number(
                1 if len(self.value) != other.value else 0
            ).setContext(self.context), None
        return None, self.illegalOperation(other)

    def isLessThan(self, other):
        if isinstance(other, String):
            return Number(
                1 if self.value < other.value else 0
            ).setContext(self.context), None
        if isinstance(other, Number) and isinstance(other.value, int):
            return Number(
                1 if len(self.value) < other.value else 0
            ).setContext(self.context), None
        return None, self.illegalOperation(other)

    def isGreaterThan(self, other):
        if isinstance(other, String):
            return Number(
                1 if self.value > other.value else 0
            ).setContext(self.context), None
        if isinstance(other, Number) and isinstance(other.value, int):
            return Number(
                1 if len(self.value) > other.value else 0
            ).setContext(self.context), None
        return None, self.illegalOperation(other)

    def isLessThanOrEqual(self, other):
        if isinstance(other, String):
            return Number(
                1 if self.value <= other.value else 0
            ).setContext(self.context), None
        if isinstance(other, Number) and isinstance(other.value, int):
            return Number(
                1 if len(self.value) <= other.value else 0
            ).setContext(self.context), None
        return None, self.illegalOperation(other)

    def isGreaterThanOrEqual(self, other):
        if isinstance(other, String):
            return Number(
                1 if self.value >= other.value else 0
            ).setContext(self.context), None
        if isinstance(other, Number) and isinstance(other.value, int):
            return Number(
                1 if len(self.value) >= other.value else 0
            ).setContext(self.context), None
        return None, self.illegalOperation(other)

    def copy(self):
        copy = String(self.value)
        copy.setPos(self.startPos, self.endPos)
        copy.setContext(self.context)
        return copy
    
    def __repr__(self):
        return self.value


class Function(Value):
    def __init__(self, name, bodyNode, argNames):
        super().__init__()
        self.name = name or "<anonymous>"
        self.bodyNode = bodyNode
        self.argNames = argNames

    def execute(self, args, context):
        res = RTResult()
        interpreter = Interpreter()
        newContext = Context(self.name, context, self.startPos)
        newContext.symbolTable = SymbolTable(context.symbolTable)

        if len(args) > len(self.argNames):
            dif = len(args) - len(self.argNames)
            return res.failure(RTError(
                self.startPos, self.endPos,
                f"{dif} too many args passed into {self.name}",
                context
            ))
        if len(args) < len(self.argNames):
            dif = len(self.argNames) - len(args)
            return res.failure(RTError(
                self.startPos, self.endPos,
                f"{dif} too few args passed into {self.name}",
                context
            ))

        for i, argValue in enumerate(args):
            argName = self.argNames[i]
            argValue.setContext(newContext)
            newContext.symbolTable.set(argName, argValue)

        value = res.register(interpreter.visit(self.bodyNode, newContext))
        if res.err:
            return res

        return res.success(value)

    def copy(self):
        copy = Function(self.name, self.bodyNode, self.argNames)
        copy.setContext(self.context)
        copy.setPos(self.startPos, self.endPos)
        return copy

    def __repr__(self):
        return f"<function {self.name}>"


################
# CONTEXT
################


class Context:
    def __init__(self, displayName, parent=None, parentEntryPos=None):
        self.displayName = displayName
        self.parent = parent
        self.parentEntryPos = parentEntryPos
        self.symbolTable = None


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

    def __repr__(self):
        res = repr(self.symbols)
        if self.parent:
            res += "\n" + repr(self.parent)
        return res


################
# INTERPRETER
################


class Interpreter:
    def visit(self, node, context):
        methodName = f"visit{type(node).__name__}"
        method = getattr(self, methodName, self.noVisitMethod)
        return method(node, context)

    def noVisitMethod(self, node, context):
        raise Exception(f"No visit{type(node).__name__} method defined")
    
    def visitNoneType(self, node, context):
        return RTResult().success(None)

    def visitNumberNode(self, node, context):
        return RTResult().success(
            Number(node.tkn.value).setContext(context).setPos(
                node.startPos, node.endPos
            )
        )

    def visitStringNode(self, node, context):
        return RTResult().success(
            String(node.tkn.value).setContext(context).setPos(
                node.startPos, node.endPos
            )
        )

    def visitVarAccessNode(self, node, context):
        res = RTResult()
        varName = node.varNameTkn.value
        value = context.symbolTable.get(varName)
        if value is None:
            return res.failure(RTError(
                node.startPos, node.endPos,
                f"{varName} is not defined",
                context
            ))
        value = value.copy().setPos(node.startPos, node.endPos)

        return res.success(value)

    def visitVarAssignNode(self, node, context):
        res = RTResult()
        varName = node.varNameTkn.value
        value = res.register(self.visit(node.valueNode, context))
        if res.err:
            return res

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
        elif node.opTkn.matches(tok.TT_KEYWORD, "not"):
            result, err = val.boolNot()

        if err:
            return res.failure(err)
        return res.success(result.setPos(node.startPos, node.endPos))

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

        return res.success(None)

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

        return res.success(None)

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

        return res.success(None)

    def visitFuncDefNode(self, node, context):
        res = RTResult()

        funcName = node.varNameTkn.value if node.varNameTkn else None
        bodyNode = node.bodyNode
        argNames = [argName.value for argName in node.argNameTkns]
        funcValue = Function(
            funcName, bodyNode, argNames
        ).setContext(context).setPos(node.startPos, node.endPos)

        if node.varNameTkn:
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

        returnValue = res.register(valueToCall.execute(args, context))
        if res.err:
            return res

        return res.success(returnValue)
    
    def visitBlockNode(self, node, context):
        res = RTResult()

        exprValue = None
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

        print(exprValue)
        return res.success(exprValue)
    
    def visitInputNode(self, node, context):
        res = RTResult()
        val = input("> ")
        if not val.replace(".", "", 1).isdigit():
            return res.success(String(val))
        if "." in val:
            return res.success(Number(float(val)))
        return res.success(Number(int(val)))
