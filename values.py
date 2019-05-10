from copy import deepcopy

from error import RTError
import languageInterpreter as li

################
# VALUES
################


class Value:
    def __init__(self):
        self.value = None
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
        return Number(0).setContext(self.context), None

    def isNotEqual(self, other):
        return Number(1).setContext(self.context), None

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
        isTrue, err = self.isTrue()
        if err:
            return None, err
        return not isTrue, None

    def boolAnd(self, other):
        sTrue, sErr = self.isTrue()
        if sErr:
            return None, sErr
        if not sTrue:
            return Number(0).setContext(self.context)
        oTrue, oErr = other.isTrue()
        if oErr:
            return None, oErr
        return Number(
            1 if sTrue and oTrue else 0
        ).setContext(self.context), None

    def boolOr(self, other):
        sTrue, sErr = self.isTrue()
        if sErr:
            return None, sErr
        if sTrue:
            return Number(1).setContext(self.context)
        oTrue, oErr = other.isTrue()
        if oErr:
            return None, oErr
        return Number(
            1 if sTrue or oTrue else 0
        ).setContext(self.context), None

    def boolNot(self):
        isTrue, err = self.isTrue()
        if err:
            return None, err
        return Number(0 if isTrue else 1).setContext(self.context), None

    def execute(self, args, context):
        return li.RTResult().failure(self.illegalOperation())

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


class NoneValue(Value):
    def __init__(self):
        super().__init__()
        self.value = None
    
    def isEqual(self, other):
        if isinstance(other, NoneValue):
            return Number(1).setContext(self.context), None
        return Number(0).setContext(self.context), None
    
    def isTrue(self):
        return False, None
    
    def isNotEqual(self, other):
        if isinstance(other, NoneValue):
            return Number(0).setContext(self.context), None
        return Number(1).setContext(self.context), None
    
    def __repr__(self):
        return str(self.value)


class Number(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def addedTo(self, other):
        if isinstance(other, Number):
            return Number(
                self.value + other.value
            ).setContext(self.context), None
        if isinstance(other, String) or isinstance(other, List):
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
        return Number(0).setContext(self.context), None

    def isNotEqual(self, other):
        if isinstance(other, Number):
            return Number(
                1 if self.value != other.value else 0
            ).setContext(self.context), None
        if isinstance(other, String) and isinstance(self.value, int):
            return Number(
                1 if self.value != len(other.value) else 0
            ).setContext(self.context), None
        return Number(1).setContext(self.context), None

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
        return self.value != 0, None

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

    def isEqual(self, other):
        if isinstance(other, String):
            return Number(
                1 if self.value == other.value else 0
            ).setContext(self.context), None
        if isinstance(other, Number) and isinstance(other.value, int):
            return Number(
                1 if len(self.value) == other.value else 0
            ).setContext(self.context), None
        return Number(0).setContext(self.context), None

    def isNotEqual(self, other):
        if isinstance(other, String):
            return Number(
                1 if self.value != other.value else 0
            ).setContext(self.context), None
        if isinstance(other, Number) and isinstance(other.value, int):
            return Number(
                1 if len(self.value) != other.value else 0
            ).setContext(self.context), None
        return Number(1).setContext(self.context), None

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
    
    def isTrue(self):
        return len(self.value) > 0, None
    
    def execute(self, args, context):
        res = li.RTResult()
        if len(args) == 1:
            idx = args[0]
            if isinstance(idx, Number) and isinstance(idx.value, int):
                if idx.value >= len(self.value) or idx.value < -len(self.value):
                    return res.failure(RTError(
                        idx.startPos, idx.endPos,
                        "Index out of range",
                        self.context
                    ))
                return res.success(String(
                    self.value[idx.value]
                ).setContext(self.context))
        elif len(args) == 2:
            idxFrom = args[0]
            idxTo = args[1]
            if isinstance(idxFrom, Number) and isinstance(idxFrom.value, int) and isinstance(idxTo, Number) and isinstance(idxTo.value, int):
                return res.success(String(
                    self.value[idxFrom.value:idxTo.value]
                ).setContext(self.context))
        elif len(args) == 3:
            idxFrom = args[0]
            idxTo = args[1]
            idxStep = args[2]
            if isinstance(idxFrom, Number) and isinstance(idxFrom.value, int) and isinstance(idxTo, Number) and isinstance(idxTo.value, int) and isinstance(idxStep, Number) and isinstance(idxStep.value, int):
                if idxStep.value == 0:
                    return res.failure(RTError(
                        idxStep.startPos, idxStep.endPos,
                        "Slice step cannot be zero",
                        self.context
                    ))
                return res.success(String(
                    self.value[idxFrom.value:idxTo.value:idxStep.value]
                ).setContext(self.context))
        return res.failure(self.illegalOperation(args[-1] if len(args) > 0 else None))

    def copy(self):
        copy = String(self.value)
        copy.setPos(self.startPos, self.endPos)
        copy.setContext(self.context)
        return copy
    
    def __repr__(self):
        escapeChars = {
            "\\": "\\\\",
            "\"": "\\\"",
            "\n": "\\n",
            "\t": "\\t",
            "\r": "\\r"
        }
        value = self.value
        for escape, char in escapeChars.items():
            value = value.replace(escape, char)
        return f"\"{value}\""
    
    def __str__(self):
        return self.value


class List(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
    
    def addedTo(self, other):
        if isinstance(other, List):
            return List(
                self.value + other.value
            ).setContext(self.context), None
        if isinstance(other, Number):
            return Number(
                len(self.value) + other.value
            ).setContext(self.context), None
        return None, self.illegalOperation(other)
    
    def subbedBy(self, other):
        contains = False
        for elem in self.value:
            equal, err = elem.isEqual(other)
            if err:
                return None, err
            if equal.value != 0:
                contains = True
                break
        return Number(1 if contains else 0).setContext(self.context), None
    
    def multedBy(self, other):
        if isinstance(other, Number) and isinstance(other.value, int):
            return List(
                self.value * other.value
            ).setContext(self.context), None
        return None, self.illegalOperation(other)

    def isEqual(self, other):
        if isinstance(other, List):
            equal = True
            if len(self.value) != len(other.value):
                equal = False
            else:
                for i in range(len(self.value)):
                    notEqual, err = self.value[i].isNotEqual(other.value[i])
                    if err:
                        return None, err
                    if notEqual.value != 0:
                        equal = False
                        break
            return Number(
                1 if equal else 0
            ).setContext(self.context), None
        if isinstance(other, Number) and isinstance(other.value, int):
            return Number(
                1 if len(self.value) == other.value else 0
            ).setContext(self.context), None
        return Number(0).setContext(self.context), None

    def isNotEqual(self, other):
        if isinstance(other, List):
            return Number(
                1 if self.value != other.value else 0
            ).setContext(self.context), None
        if isinstance(other, Number) and isinstance(other.value, int):
            return Number(
                1 if len(self.value) != other.value else 0
            ).setContext(self.context), None
        return Number(1).setContext(self.context), None

    def isLessThan(self, other):
        if isinstance(other, List):
            return Number(
                1 if self.value < other.value else 0
            ).setContext(self.context), None
        if isinstance(other, Number) and isinstance(other.value, int):
            return Number(
                1 if len(self.value) < other.value else 0
            ).setContext(self.context), None
        return None, self.illegalOperation(other)

    def isGreaterThan(self, other):
        if isinstance(other, List):
            return Number(
                1 if self.value > other.value else 0
            ).setContext(self.context), None
        if isinstance(other, Number) and isinstance(other.value, int):
            return Number(
                1 if len(self.value) > other.value else 0
            ).setContext(self.context), None
        return None, self.illegalOperation(other)

    def isLessThanOrEqual(self, other):
        if isinstance(other, List):
            return Number(
                1 if self.value <= other.value else 0
            ).setContext(self.context), None
        if isinstance(other, Number) and isinstance(other.value, int):
            return Number(
                1 if len(self.value) <= other.value else 0
            ).setContext(self.context), None
        return None, self.illegalOperation(other)

    def isGreaterThanOrEqual(self, other):
        if isinstance(other, List):
            return Number(
                1 if self.value >= other.value else 0
            ).setContext(self.context), None
        if isinstance(other, Number) and isinstance(other.value, int):
            return Number(
                1 if len(self.value) >= other.value else 0
            ).setContext(self.context), None
        return None, self.illegalOperation(other)
    
    def isTrue(self):
        return len(self.value) > 0, None
    
    def execute(self, args, context):
        res = li.RTResult()
        if len(args) == 1:
            idx = args[0]
            if isinstance(idx, Number) and isinstance(idx.value, int):
                if idx.value >= len(self.value) or idx.value < -len(self.value):
                    return res.failure(RTError(
                        idx.startPos, idx.endPos,
                        "Index out of range",
                        self.context
                    ))
                return res.success(self.value[idx.value])
        elif len(args) == 2:
            idxFrom = args[0]
            idxTo = args[1]
            if isinstance(idxFrom, Number) and isinstance(idxFrom.value, int) and isinstance(idxTo, Number) and isinstance(idxTo.value, int):
                return res.success(List(
                    self.value[idxFrom.value:idxTo.value]
                ).setContext(self.context))
        elif len(args) == 3:
            idxFrom = args[0]
            idxTo = args[1]
            idxStep = args[2]
            if isinstance(idxFrom, Number) and isinstance(idxFrom.value, int) and isinstance(idxTo, Number) and isinstance(idxTo.value, int) and isinstance(idxStep, Number) and isinstance(idxStep.value, int):
                if idxStep.value == 0:
                    return res.failure(RTError(
                        idxStep.startPos, idxStep.endPos,
                        "Slice step cannot be zero",
                        self.context
                    ))
                return res.success(List(
                    self.value[idxFrom.value:idxTo.value:idxStep.value]
                ).setContext(self.context))
        return res.failure(self.illegalOperation(args[-1] if len(args) > 0 else None))
    
    def copy(self):
        copy = List(deepcopy(self.value))
        copy.setPos(self.startPos, self.endPos)
        copy.setContext(self.context)
        return copy
    
    def __repr__(self):
        return str(self.value)


class Function(Value):
    def __init__(self, name, bodyNode, argNames):
        super().__init__()
        self.name = name or "<anonymous>"
        self.bodyNode = bodyNode
        self.argNames = argNames

    def execute(self, args, context):
        res = li.RTResult()
        interpreter = li.Interpreter()
        newContext = li.Context(self.name, context, self.startPos)
        newContext.symbolTable = li.SymbolTable(context.symbolTable)

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
