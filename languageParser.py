from error import InvalidSyntaxError
from tokens import *
from languageLexer import Token
import languageInterpreter as li

################
# NODES
################


class NoneValueNode:
    def __init__(self, tkn):
        self.tkn = tkn
        self.startPos = tkn.startPos
        self.endPos = tkn.endPos
    
    def __repr__(self):
        return f"{self.tkn}"


class NumberNode:
    def __init__(self, tkn):
        self.tkn = tkn
        self.startPos = tkn.startPos
        self.endPos = tkn.endPos

    def __repr__(self):
        return f"{self.tkn}"


class StringNode:
    def __init__(self, tkn):
        self.tkn = tkn
        self.startPos = tkn.startPos
        self.endPos = tkn.endPos
    
    def __repr__(self):
        return self.tkn


class ListNode:
    def __init__(self, exprNodes):
        self.exprNodes = exprNodes

        if len(exprNodes) > 0:
            self.startPos = exprNodes[0].startPos
            self.endPos = exprNodes[-1].endPos
        else:
            self.startPos = None
            self.endPos = None


class VarAccessNode:
    def __init__(self, varNameTkn):
        self.varNameTkn = varNameTkn
        self.startPos = varNameTkn.startPos
        self.endPos = varNameTkn.endPos


class VarAssignNode:
    def __init__(self, varNameTkn, valueNode):
        self.varNameTkn = varNameTkn
        self.valueNode = valueNode
        self.startPos = varNameTkn.startPos
        self.endPos = valueNode.endPos


class ListModifNode:
    def __init__(self, varNameTkn, idxNodes, valueNode):
        self.varNameTkn = varNameTkn
        self.idxNodes = idxNodes
        self.valueNode = valueNode
        self.startPos = varNameTkn.startPos
        self.endPos = valueNode.endPos


class BinOpNode:
    def __init__(self, lNode, opTkn, rNode):
        self.lNode = lNode
        self.opTkn = opTkn
        self.rNode = rNode
        self.startPos = lNode.startPos
        self.endPos = rNode.endPos

    def __repr__(self):
        return f"({self.lNode}, {self.opTkn}, {self.rNode})"


class UnaryOpNode:
    def __init__(self, opTkn, node):
        self.opTkn = opTkn
        self.node = node
        self.startPos = opTkn.startPos
        self.endPos = node.endPos

    def __repr__(self):
        return f"({self.opTkn}, {self.node})"


class IfNode:
    def __init__(self, cases, elseCase):
        self.cases = cases
        self.elseCase = elseCase

        self.startPos = cases[0][0].startPos
        self.endPos = elseCase.endPos if elseCase else cases[-1][1].endPos


class ForNode:
    def __init__(self, varNameTkn, startValueNode, endValueNode,
                 stepValueNode, bodyNode, elseNode):
        self.varNameTkn = varNameTkn
        self.startValueNode = startValueNode
        self.endValueNode = endValueNode
        self.stepValueNode = stepValueNode
        self.bodyNode = bodyNode
        self.elseNode = elseNode

        self.startPos = varNameTkn.startPos
        self.endPos = elseNode.endPos if elseNode else bodyNode.endPos

class ForEachNode:
    def __init__(self, varNameTkn, listNode, bodyNode, elseNode):
        self.varNameTkn = varNameTkn
        self.listNode = listNode
        self.bodyNode = bodyNode
        self.elseNode = elseNode
        
        self.startPos = varNameTkn.startPos
        self.endPos = elseNode.endPos if elseNode else bodyNode.endPos


class WhileNode:
    def __init__(self, condNode, bodyNode, elseNode):
        self.condNode = condNode
        self.bodyNode = bodyNode
        self.elseNode = elseNode

        self.startPos = condNode.startPos
        self.endPos = elseNode.endPos if elseNode else bodyNode.endPos


class BreakNode:
    def __init__(self, tkn):
        self.startPos = tkn.startPos
        self.endPos = tkn.endPos


class FuncDefNode:
    def __init__(self, varNameTkn, argNameTkns, bodyNode, canMod, isBuiltin):
        self.varNameTkn = varNameTkn
        self.argNameTkns = argNameTkns
        self.bodyNode = bodyNode
        self.canMod = canMod
        self.isBuiltin = isBuiltin

        if varNameTkn:
            self.startPos = varNameTkn.startPos
        elif len(argNameTkns) > 0:
            self.startPos = argNameTkns[0].startPos
        else:
            self.startPos = bodyNode.startPos

        self.endPos = bodyNode.endPos


class CallNode:
    def __init__(self, nodeToCall, argNodes):
        self.nodeToCall = nodeToCall
        self.argNodes = argNodes

        self.startPos = nodeToCall.startPos

        if len(argNodes) > 0:
            self.endPos = argNodes[-1].endPos
        else:
            self.endPos = nodeToCall.endPos


class ReturnNode:
    def __init__(self, exprNode):
        self.exprNode = exprNode

        self.startPos = exprNode.startPos
        self.endPos = exprNode.endPos


class BlockNode:
    def __init__(self, exprNodes, bracketPos=None):
        self.exprNodes = exprNodes

        if len(exprNodes) > 0:
            self.startPos = exprNodes[0].startPos
            self.endPos = exprNodes[-1].endPos
        else:
            self.startPos = bracketPos
            self.endPos = bracketPos


class DispNode:
    def __init__(self, bodyNode, newLine):
        self.bodyNode = bodyNode
        self.newLine = newLine

        self.startPos = bodyNode.startPos
        self.endPos = bodyNode.endPos


class InputNode:
    def __init__(self, inputTkn):
        self.startPos = inputTkn.startPos
        self.endPos = inputTkn.endPos


class GetchNode:
    def __init__(self, getchTkn):
        self.startPos = getchTkn.startPos
        self.endPos = getchTkn.endPos


class KbhitNode:
    def __init__(self, kbhitTkn):
        self.startPos = kbhitTkn.startPos
        self.endPos = kbhitTkn.endPos


class RandNode:
    def __init__(self, randTkn):
        self.startPos = randTkn.startPos
        self.endPos = randTkn.endPos


class IntCastNode:
    def __init__(self, exprNode):
        self.exprNode = exprNode

        self.startPos = exprNode.startPos
        self.endPos = exprNode.endPos


class FloatCastNode:
    def __init__(self, exprNode):
        self.exprNode = exprNode

        self.startPos = exprNode.startPos
        self.endPos = exprNode.endPos


class StrCastNode:
    def __init__(self, exprNode):
        self.exprNode = exprNode

        self.startPos = exprNode.startPos
        self.endPos = exprNode.endPos


class IncludeNode:
    def __init__(self, fileNode, moduleName):
        self.fileNode = fileNode
        self.moduleName = moduleName
        
        self.startPos = fileNode.startPos
        self.endPos = fileNode.endPos


class AccessNode:
    def __init__(self, moduleNode, varNameTkn):
        self.moduleNode = moduleNode
        self.varNameTkn = varNameTkn
        
        self.startPos = moduleNode.startPos
        self.endPos = varNameTkn.endPos


class TypeNode:
    def __init__(self, valueNode):
        self.valueNode = valueNode
        
        self.startPos = valueNode.startPos
        self.endPos = valueNode.endPos


class ClassNode:
    def __init__(self, varNameTkn, parentTkn, bodyNode):
        self.varNameTkn = varNameTkn
        self.bodyNode = bodyNode
        self.parentTkn = parentTkn

        self.startPos = varNameTkn.startPos
        self.endPos = bodyNode.endPos


class ReadNode:
    def __init__(self, fileNameNode, byteMode=False):
        self.fileNameNode = fileNameNode
        self.byteMode = byteMode
        
        self.startPos = fileNameNode.startPos
        self.endPos = fileNameNode.endPos


class WriteNode:
    def __init__(self, fileNameNode, fileContentNode, byteMode=False):
        self.fileNameNode = fileNameNode
        self.fileContentNode = fileContentNode
        self.byteMode = byteMode
        
        self.startPos = fileNameNode.startPos
        self.endPos = fileContentNode.endPos


class ClsNode:
    def __init__(self, tkn):
        self.startPos = tkn.startPos
        self.endPos = tkn.endPos


class TimeNode:
    def __init__(self, tkn):
        self.startPos = tkn.startPos
        self.endPos = tkn.endPos


class CLINode:
    def __init__(self, cmdNode):
        self.cmdNode = cmdNode
        
        self.startPos = cmdNode.startPos
        self.endPos = cmdNode.endPos


class OSNode:
    def __init__(self, tkn):
        self.startPos = tkn.startPos
        self.endPos = tkn.endPos


class TryCatchNode:
    def __init__(self, tryNode, catchNode):
        self.tryNode = tryNode
        self.catchNode = catchNode

        self.startPos = tryNode.startPos
        self.endPos = catchNode.endPos


################
# PARSE RESULT
################


class ParseResult:
    def __init__(self):
        self.err = None
        self.node = None
        self.advanceCount = 0

    def registerAdvancement(self):
        self.advanceCount += 1

    def register(self, res):
        self.advanceCount += res.advanceCount
        if res.err:
            self.err = res.err
        return res.node

    def success(self, node):
        self.node = node
        return self

    def failure(self, err):
        if not self.err or self.advanceCount == 0:
            self.err = err
        return self


################
# PARSER
################


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tknIdx = -1
        self.tkn = None
        self.nextTkn = None
        self.advance()

    def advance(self):
        self.tknIdx += 1
        if self.tknIdx < len(self.tokens):
            self.tkn = self.tokens[self.tknIdx]
        else:
            self.tkn = Token(TT_EOF)
        if self.tknIdx + 1 < len(self.tokens):
            self.nextTkn = self.tokens[self.tknIdx + 1]
        else:
            self.nextTkn = Token(TT_EOF)
        return self.tkn

    def parse(self):
        res = ParseResult()
        if self.tkn.type == TT_EOF:
            return res.success(NoneValueNode(Token(None)))
        prog = res.register(self.program())
        if res.err:
            return res
        elif self.tkn.type != TT_EOF:
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected ';'"
            ))
        return res.success(prog)
    
    def randExpr(self):
        res = ParseResult()
        if not self.tkn.matches(TT_KEYWORD, "rand"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'rand'"
            ))
        tkn = self.tkn
        res.registerAdvancement()
        self.advance()
        return res.success(RandNode(tkn))
    
    def intCast(self):
        res = ParseResult()
        if not self.tkn.matches(TT_KEYWORD, "int"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'int'"
            ))
        res.registerAdvancement()
        self.advance()
        valueExpr = res.register(self.expr())
        if res.err:
            return res
        return res.success(IntCastNode(valueExpr))
    
    def floatCast(self):
        res = ParseResult()
        if not self.tkn.matches(TT_KEYWORD, "float"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'float'"
            ))
        res.registerAdvancement()
        self.advance()
        valueExpr = res.register(self.expr())
        if res.err:
            return res
        return res.success(FloatCastNode(valueExpr))
    
    def strCast(self):
        res = ParseResult()
        if not self.tkn.matches(TT_KEYWORD, "str"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'str'"
            ))
        res.registerAdvancement()
        self.advance()
        valueExpr = res.register(self.expr())
        if res.err:
            return res
        return res.success(StrCastNode(valueExpr))
    
    def dispExpr(self):
        res = ParseResult()

        if not self.tkn.matches(TT_KEYWORD, "disp"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'disp'"
            ))
        res.registerAdvancement()
        self.advance()

        body = res.register(self.expr())
        if res.err:
            return res
        
        if self.tkn.type == TT_COLON:
            res.registerAdvancement()
            self.advance()
            return res.success(DispNode(body, False))
        
        return res.success(DispNode(body, True))
    
    def inputExpr(self):
        res = ParseResult()

        if not self.tkn.matches(TT_KEYWORD, "input"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'input'"
            ))
        tkn = self.tkn
        res.registerAdvancement()
        self.advance()
        
        return res.success(InputNode(tkn))
    
    def getchExpr(self):
        res = ParseResult()

        if not self.tkn.matches(TT_KEYWORD, "getch"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'getch'"
            ))
        tkn = self.tkn
        res.registerAdvancement()
        self.advance()
        
        return res.success(GetchNode(tkn))
    
    def kbhitExpr(self):
        res = ParseResult()

        if not self.tkn.matches(TT_KEYWORD, "kbhit"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'kbhit'"
            ))
        tkn = self.tkn
        res.registerAdvancement()
        self.advance()
        
        return res.success(KbhitNode(tkn))

    def forExpr(self):
        res = ParseResult()

        if not self.tkn.matches(TT_KEYWORD, "for"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'for'"
            ))
        res.registerAdvancement()
        self.advance()

        if self.tkn.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected identifier"
            ))
        varName = self.tkn
        res.registerAdvancement()
        self.advance()

        if self.tkn.type != TT_EQ:
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected '='"
            ))
        res.registerAdvancement()
        self.advance()

        startValue = res.register(self.expr())
        if res.err:
            return res

        if not self.tkn.matches(TT_KEYWORD, "to"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'to'"
            ))
        res.registerAdvancement()
        self.advance()

        endValue = res.register(self.expr())
        if res.err:
            return res

        if self.tkn.matches(TT_KEYWORD, "step"):
            res.registerAdvancement()
            self.advance()

            stepValue = res.register(self.expr())
            if res.err:
                return res
        else:
            stepValue = None

        if self.tkn.matches(TT_KEYWORD, "do"):
            res.registerAdvancement()
            self.advance()

        body = res.register(self.expr())
        if res.err:
            return res
        
        if self.tkn.matches(TT_KEYWORD, "else"):
            res.registerAdvancement()
            self.advance()
            elseNode = res.register(self.expr())
            if res.err:
                return res
        else:
            elseNode = None

        return res.success(ForNode(
            varName, startValue, endValue, stepValue, body, elseNode
        ))
    
    def forEachExpr(self):
        res = ParseResult()

        if not self.tkn.matches(TT_KEYWORD, "for"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'for'"
            ))
        res.registerAdvancement()
        self.advance()

        if not self.tkn.matches(TT_KEYWORD, "each"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'each'"
            ))
        res.registerAdvancement()
        self.advance()

        if self.tkn.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected identifier"
            ))
        varName = self.tkn
        res.registerAdvancement()
        self.advance()

        if not self.tkn.matches(TT_KEYWORD, "in"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'in'"
            ))
        res.registerAdvancement()
        self.advance()

        listExpr = res.register(self.expr())
        if res.err:
            return res

        if self.tkn.matches(TT_KEYWORD, "do"):
            res.registerAdvancement()
            self.advance()

        body = res.register(self.expr())
        if res.err:
            return res
        
        if self.tkn.matches(TT_KEYWORD, "else"):
            res.registerAdvancement()
            self.advance()
            elseNode = res.register(self.expr())
            if res.err:
                return res
        else:
            elseNode = None

        return res.success(ForEachNode(
            varName, listExpr, body, elseNode
        ))

    def whileExpr(self):
        res = ParseResult()

        if not self.tkn.matches(TT_KEYWORD, "while"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'while'"
            ))
        res.registerAdvancement()
        self.advance()

        cond = res.register(self.expr())
        if res.err:
            return res

        if self.tkn.matches(TT_KEYWORD, "do"):
            res.registerAdvancement()
            self.advance()

        body = res.register(self.expr())
        if res.err:
            return res
        
        if self.tkn.matches(TT_KEYWORD, "else"):
            res.registerAdvancement()
            self.advance()
            elseNode = res.register(self.expr())
            if res.err:
                return res
        else:
            elseNode = None

        return res.success(WhileNode(cond, body, elseNode))
    
    def breakExpr(self):
        res = ParseResult()
        
        if not self.tkn.matches(TT_KEYWORD, "break"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'break'"
            ))
        tkn = self.tkn
        res.registerAdvancement()
        self.advance()
        
        return res.success(BreakNode(tkn))

    def ifExpr(self):
        res = ParseResult()
        cases = []
        elseCase = None

        if not self.tkn.matches(TT_KEYWORD, "if"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'if'"
            ))
        res.registerAdvancement()
        self.advance()
        cond = res.register(self.expr())
        if res.err:
            return res

        if self.tkn.matches(TT_KEYWORD, "then"):
            res.registerAdvancement()
            self.advance()

        expr = res.register(self.expr())
        if res.err:
            return res
        cases.append((cond, expr))

        while self.tkn.matches(TT_KEYWORD, "elif"):
            res.registerAdvancement()
            self.advance()

            cond = res.register(self.expr())
            if res.err:
                return res

            if self.tkn.matches(TT_KEYWORD, "then"):
                res.registerAdvancement()
                self.advance()

            expr = res.register(self.expr())
            if res.err:
                return res
            cases.append((cond, expr))

        if self.tkn.matches(TT_KEYWORD, "else"):
            res.registerAdvancement()
            self.advance()

            elseCase = res.register(self.expr())
            if res.err:
                return res

        return res.success(IfNode(cases, elseCase))
    
    def listExpr(self):
        res = ParseResult()
        
        if self.tkn.type != TT_LSQBRACKET:
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected '['"
            ))
        res.registerAdvancement()
        self.advance()
        
        if self.tkn.type == TT_RSQBRACKET:
            res.registerAdvancement()
            self.advance()
            return res.success(ListNode([]))
        
        exprs = [res.register(self.expr())]
        if res.err:
            return res
        
        while self.tkn.type == TT_COMMA:
            res.registerAdvancement()
            self.advance()
            exprs.append(res.register(self.expr()))
            if res.err:
                return res
        
        if self.tkn.type != TT_RSQBRACKET:
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected ']'"
            ))
        res.registerAdvancement()
        self.advance()
        
        return res.success(ListNode(exprs))
    
    def typeExpr(self):
        res = ParseResult()
        
        if not self.tkn.matches(TT_KEYWORD, "type"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'type'"
            ))
        res.registerAdvancement()
        self.advance()
        
        valueNode = res.register(self.expr())
        if res.err:
            return res
        
        return res.success(TypeNode(valueNode))
    
    def includeExpr(self):
        res = ParseResult()
        
        if not self.tkn.matches(TT_KEYWORD, "include"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'include'"
            ))
        res.registerAdvancement()
        self.advance()
        
        fileNode = res.register(self.expr())
        if res.err:
            return res
        
        if self.tkn.matches(TT_KEYWORD, "as"):
            res.registerAdvancement()
            self.advance()
            if self.tkn.type != TT_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.tkn.startPos, self.tkn.endPos,
                    "Expected identifier"
                ))
            moduleName = self.tkn.value
            res.registerAdvancement()
            self.advance()
        else:
            moduleName = None
        
        return res.success(IncludeNode(fileNode, moduleName))
    
    def classExpr(self):
        res = ParseResult()
        
        if not self.tkn.matches(TT_KEYWORD, "class"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'class'"
            ))
        res.registerAdvancement()
        self.advance()
        
        if self.tkn.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected identifier"
            ))
        varNameTkn = self.tkn
        res.registerAdvancement()
        self.advance()
        
        if self.tkn.type == TT_LPAREN:
            res.registerAdvancement()
            self.advance()
            if self.tkn.type != TT_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.tkn.startPos, self.tkn.endPos,
                    "Expected identifier"
                ))
            parentTkn = self.tkn
            res.registerAdvancement()
            self.advance()
            if self.tkn.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.tkn.startPos, self.tkn.endPos,
                    "Expected ')'"
                ))
            res.registerAdvancement()
            self.advance()
        else:
            parentTkn = None
        
        bodyNode = res.register(self.expr())
        if res.err:
            return res
        
        return res.success(ClassNode(varNameTkn, parentTkn, bodyNode))
    
    def readExpr(self, byteMode=False):
        res = ParseResult()
        
        if not (self.tkn.matches(TT_KEYWORD, "read") or self.tkn.matches(TT_KEYWORD, "readb")):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'read' or 'readb'"
            ))
        res.registerAdvancement()
        self.advance()
        
        fileNameNode = res.register(self.expr())
        if res.err:
            return res
        return res.success(ReadNode(fileNameNode, byteMode))
    
    def writeExpr(self, byteMode=False):
        res = ParseResult()
        
        if not (self.tkn.matches(TT_KEYWORD, "write") or self.tkn.matches(TT_KEYWORD, "writeb")):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'write' or 'writeb'"
            ))
        res.registerAdvancement()
        self.advance()
        
        fileNameNode = res.register(self.expr())
        if res.err:
            return res
        
        if self.tkn.type != TT_COMMA:
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected ','"
            ))
        res.registerAdvancement()
        self.advance()
        
        fileContentNode = res.register(self.expr())
        if res.err:
            return res
        return res.success(WriteNode(fileNameNode, fileContentNode, byteMode))
    
    def clsExpr(self):
        res = ParseResult()
        
        tkn = self.tkn
        if not self.tkn.matches(TT_KEYWORD, "cls"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'cls'"
            ))
        res.registerAdvancement()
        self.advance()
        
        return res.success(ClsNode(tkn))
    
    def timeExpr(self):
        res = ParseResult()
        
        tkn = self.tkn
        if not self.tkn.matches(TT_KEYWORD, "time"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'time'"
            ))
        res.registerAdvancement()
        self.advance()
        
        return res.success(TimeNode(tkn))
    
    def cliExpr(self):
        res = ParseResult()
        
        if not self.tkn.matches(TT_KEYWORD, "cli"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'cli'"
            ))
        res.registerAdvancement()
        self.advance()
        
        cmdNode = res.register(self.expr())
        if res.err:
            return res
        
        return res.success(CLINode(cmdNode))
    
    def osExpr(self):
        res = ParseResult()
        
        tkn = self.tkn
        if not self.tkn.matches(TT_KEYWORD, "os"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'os'"
            ))
        res.registerAdvancement()
        self.advance()
        
        return res.success(OSNode(tkn))
    
    def funcDef(self):
        res = ParseResult()

        if not self.tkn.matches(TT_KEYWORD, "fn"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'fn'"
            ))
        res.registerAdvancement()
        self.advance()
        
        if self.tkn.matches(TT_KEYWORD, "mut"):
            res.registerAdvancement()
            self.advance()
            canMod = True
        else:
            canMod = False
        
        if self.tkn.matches(TT_KEYWORD, "builtin"):
            res.registerAdvancement()
            self.advance()
            isBuiltin = True
        else:
            isBuiltin = False

        if self.tkn.type == TT_IDENTIFIER:
            varNameTkn = self.tkn
            res.registerAdvancement()
            self.advance()
            if self.tkn.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.tkn.startPos, self.tkn.endPos,
                    "Expected '('"
                ))
        else:
            varNameTkn = None
            if self.tkn.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.tkn.startPos, self.tkn.endPos,
                    "Expected identifier or '('"
                ))
        res.registerAdvancement()
        self.advance()

        argNameTkns = []

        if self.tkn.type == TT_IDENTIFIER:
            argNameTkns.append(self.tkn)
            res.registerAdvancement()
            self.advance()

            while self.tkn.type == TT_COMMA:
                res.registerAdvancement()
                self.advance()
                if self.tkn.type != TT_IDENTIFIER:
                    return res.failure(InvalidSyntaxError(
                        self.tkn.startPos, self.tkn.endPos,
                        "Expected identifier"
                    ))
                argNameTkns.append(self.tkn)
                res.registerAdvancement()
                self.advance()
            if self.tkn.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.tkn.startPos, self.tkn.endPos,
                    "Expected ',' or ')'"
                ))
        else:
            if self.tkn.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.tkn.startPos, self.tkn.endPos,
                    "Expected identifier or ')'"
                ))
        res.registerAdvancement()
        self.advance()

        nodeToReturn = res.register(self.expr())
        if res.err:
            return res

        return res.success(FuncDefNode(varNameTkn, argNameTkns, nodeToReturn, canMod, isBuiltin))
    
    def returnExpr(self):
        res = ParseResult()

        if not self.tkn.matches(TT_KEYWORD, "return"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'return'"
            ))
        res.registerAdvancement()
        self.advance()

        exprNode = res.register(self.expr())
        if res.err:
            return res
        
        return res.success(ReturnNode(exprNode))
    
    def tryCatchExpr(self):
        res = ParseResult()
        
        if not self.tkn.matches(TT_KEYWORD, "try"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'try'"
            ))
        res.registerAdvancement()
        self.advance()

        tryNode = res.register(self.expr())
        if res.err:
            return res
        
        if not self.tkn.matches(TT_KEYWORD, "catch"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'catch'"
            ))
        res.registerAdvancement()
        self.advance()

        catchNode = res.register(self.expr())
        if res.err:
            return res
        
        return res.success(TryCatchNode(tryNode, catchNode))
    
    def atom(self):
        res = ParseResult()
        tkn = self.tkn

        if tkn.type in (TT_INT, TT_FLOAT):
            res.registerAdvancement()
            self.advance()
            return res.success(NumberNode(tkn))
        elif tkn.type == TT_STRING:
            res.registerAdvancement()
            self.advance()
            return res.success(StringNode(tkn))
        elif tkn.type == TT_IDENTIFIER:
            res.registerAdvancement()
            self.advance()
            node = VarAccessNode(tkn)
            if self.tkn.type == TT_INC:
                node = VarAssignNode(tkn, BinOpNode(
                    node, Token(TT_PLUS, None, self.tkn.startPos, self.tkn.endPos),
                    NumberNode(Token(TT_INT, 1, self.tkn.startPos, self.tkn.endPos))
                ))
                res.registerAdvancement()
                self.advance()
            elif self.tkn.type == TT_DEC:
                node = VarAssignNode(tkn, BinOpNode(
                    node, Token(TT_MINUS, None, self.tkn.startPos, self.tkn.endPos),
                    NumberNode(Token(TT_INT, 1, self.tkn.startPos, self.tkn.endPos))
                ))
                res.registerAdvancement()
                self.advance()
            return res.success(node)
        elif tkn.type == TT_LPAREN:
            res.registerAdvancement()
            self.advance()
            expr = res.register(self.expr())
            if res.err:
                return res
            if self.tkn.type == TT_RPAREN:
                res.registerAdvancement()
                self.advance()
                return res.success(expr)
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected ')'"
            ))
        elif tkn.type == TT_LBRACKET:
            res.registerAdvancement()
            self.advance()

            if self.tkn.type == TT_RBRACKET:
                res.registerAdvancement()
                self.advance()

                return res.success(BlockNode([], tkn.startPos))

            exprs = res.register(self.program())
            if res.err:
                return res
            
            if self.tkn.type != TT_RBRACKET:
                return res.failure(InvalidSyntaxError(
                    self.tkn.startPos, self.tkn.endPos,
                    "Expected '}'"
                ))
            res.registerAdvancement()
            self.advance()
            
            return res.success(exprs)
        elif tkn.type == TT_LSQBRACKET:
            lst = res.register(self.listExpr())
            if res.err:
                return res
            return res.success(lst)
        elif tkn.matches(TT_KEYWORD, "class"):
            classExpr = res.register(self.classExpr())
            if res.err:
                return res
            return res.success(classExpr)
        elif tkn.matches(TT_KEYWORD, "include"):
            includeExpr = res.register(self.includeExpr())
            if res.err:
                return res
            return res.success(includeExpr)
        elif tkn.matches(TT_KEYWORD, "type"):
            typeExpr = res.register(self.typeExpr())
            if res.err:
                return res
            return res.success(typeExpr)
        elif tkn.matches(TT_KEYWORD, "if"):
            ifExpr = res.register(self.ifExpr())
            if res.err:
                return res
            return res.success(ifExpr)
        elif tkn.matches(TT_KEYWORD, "for"):
            if self.nextTkn.matches(TT_KEYWORD, "each"):
                forEachExpr = res.register(self.forEachExpr())
                if res.err:
                    return res
                return res.success(forEachExpr)
            forExpr = res.register(self.forExpr())
            if res.err:
                return res
            return res.success(forExpr)
        elif tkn.matches(TT_KEYWORD, "while"):
            whileExpr = res.register(self.whileExpr())
            if res.err:
                return res
            return res.success(whileExpr)
        elif tkn.matches(TT_KEYWORD, "break"):
            breakExpr = res.register(self.breakExpr())
            if res.err:
                return res
            return res.success(breakExpr)
        elif tkn.matches(TT_KEYWORD, "fn"):
            funcDef = res.register(self.funcDef())
            if res.err:
                return res
            return res.success(funcDef)
        elif tkn.matches(TT_KEYWORD, "return"):
            returnExpr = res.register(self.returnExpr())
            if res.err:
                return res
            return res.success(returnExpr)
        elif tkn.matches(TT_KEYWORD, "disp"):
            dispExpr = res.register(self.dispExpr())
            if res.err:
                return res
            return res.success(dispExpr)
        elif tkn.matches(TT_KEYWORD, "input"):
            inputExpr = res.register(self.inputExpr())
            if res.err:
                return res
            return res.success(inputExpr)
        elif tkn.matches(TT_KEYWORD, "getch"):
            getchExpr = res.register(self.getchExpr())
            if res.err:
                return res
            return res.success(getchExpr)
        elif tkn.matches(TT_KEYWORD, "kbhit"):
            kbhitExpr = res.register(self.kbhitExpr())
            if res.err:
                return res
            return res.success(kbhitExpr)
        elif tkn.matches(TT_KEYWORD, "rand"):
            randExpr = res.register(self.randExpr())
            if res.err:
                return res
            return res.success(randExpr)
        elif tkn.matches(TT_KEYWORD, "int"):
            intExpr = res.register(self.intCast())
            if res.err:
                return res
            return res.success(intExpr)
        elif tkn.matches(TT_KEYWORD, "float"):
            floatExpr = res.register(self.floatCast())
            if res.err:
                return res
            return res.success(floatExpr)
        elif tkn.matches(TT_KEYWORD, "str"):
            strExpr = res.register(self.strCast())
            if res.err:
                return res
            return res.success(strExpr)
        elif tkn.matches(TT_KEYWORD, "read"):
            readExpr = res.register(self.readExpr())
            if res.err:
                return res
            return res.success(readExpr)
        elif tkn.matches(TT_KEYWORD, "write"):
            writeExpr = res.register(self.writeExpr())
            if res.err:
                return res
            return res.success(writeExpr)
        elif tkn.matches(TT_KEYWORD, "readb"):
            readExpr = res.register(self.readExpr(True))
            if res.err:
                return res
            return res.success(readExpr)
        elif tkn.matches(TT_KEYWORD, "writeb"):
            writeExpr = res.register(self.writeExpr(True))
            if res.err:
                return res
            return res.success(writeExpr)
        elif tkn.matches(TT_KEYWORD, "cls"):
            clsExpr = res.register(self.clsExpr())
            if res.err:
                return res
            return res.success(clsExpr)
        elif tkn.matches(TT_KEYWORD, "time"):
            timeExpr = res.register(self.timeExpr())
            if res.err:
                return res
            return res.success(timeExpr)
        elif tkn.matches(TT_KEYWORD, "cli"):
            cliExpr = res.register(self.cliExpr())
            if res.err:
                return res
            return res.success(cliExpr)
        elif tkn.matches(TT_KEYWORD, "os"):
            osExpr = res.register(self.osExpr())
            if res.err:
                return res
            return res.success(osExpr)
        elif tkn.matches(TT_KEYWORD, "try"):
            tryCatchExpr = res.register(self.tryCatchExpr())
            if res.err:
                return res
            return res.success(tryCatchExpr)

        return res.failure(InvalidSyntaxError(
            tkn.startPos, tkn.endPos,
            "Expected keyword, value, identifier, operator or '('"
        ))

    def call(self):
        res = ParseResult()
        atom = res.register(self.access())
        if res.err:
            return res

        if isinstance(atom, VarAccessNode):
            varNameTkn = atom.varNameTkn
        else:
            varNameTkn = None
        idxNodes = []
        while self.tkn.type == TT_LPAREN:
            res.registerAdvancement()
            self.advance()
            argNodes = []

            if self.tkn.type == TT_RPAREN:
                res.registerAdvancement()
                self.advance()
            else:
                expr = res.register(self.expr())
                if res.err:
                    return res
                argNodes.append(expr)
                idxNodes.append(expr)

                while self.tkn.type == TT_COMMA:
                    res.registerAdvancement()
                    self.advance()

                    expr = res.register(self.expr())
                    if res.err:
                        return res
                    argNodes.append(expr)
                    idxNodes.append(expr)

                if self.tkn.type != TT_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.tkn.startPos, self.tkn.endPos,
                        "Expected ')'"
                    ))
                res.registerAdvancement()
                self.advance()

            atom = CallNode(atom, argNodes)
        if len(idxNodes) > 0 and varNameTkn is not None and self.tkn.type == TT_EQ:
            res.registerAdvancement()
            self.advance()
            
            value = res.register(self.expr())
            if res.err:
                return res
            return res.success(ListModifNode(varNameTkn, idxNodes, value))
        return res.success(atom)
    
    def access(self):
        res = ParseResult()
        
        accessNode = res.register(self.atom())
        if res.err:
            return res
        
        while self.tkn.type == TT_DOT:
            res.registerAdvancement()
            self.advance()
            
            if self.tkn.type != TT_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.tkn.startPos, self.tkn.endPos,
                    "Expected identifier"
                ))
            accessNode = AccessNode(accessNode, self.tkn)
            res.registerAdvancement()
            self.advance()
        
        return res.success(accessNode)

    def power(self):
        return self.binOp(self.call, (TT_POW,), self.factor)

    def factor(self):
        res = ParseResult()
        tkn = self.tkn

        if tkn.type in (TT_PLUS, TT_MINUS):
            res.registerAdvancement()
            self.advance()
            factor = res.register(self.factor())
            if res.err:
                return res
            return res.success(UnaryOpNode(tkn, factor))

        return self.power()

    def term(self):
        return self.binOp(self.factor, (TT_MUL, TT_DIV, TT_MOD))

    def arithExpr(self):
        return self.binOp(self.term, (TT_PLUS, TT_MINUS))

    def compExpr(self):
        res = ParseResult()
        if self.tkn.matches(TT_KEYWORD, "not"):
            opTkn = self.tkn
            res.registerAdvancement()
            self.advance()
            node = res.register(self.compExpr())
            if res.err:
                return res
            return res.success(UnaryOpNode(opTkn, node))
        node = res.register(self.binOp(
            self.arithExpr, (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE)
        ))
        if res.err:
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected valid expression or ';'"
            ))
        return res.success(node)

    def expr(self):
        res = ParseResult()

        if self.tkn.type == TT_IDENTIFIER and self.nextTkn.type in (TT_EQ, TT_DEFEQ, TT_PLUSEQ, TT_MINUSEQ, TT_MULEQ, TT_DIVEQ, TT_MODEQ, TT_POWEQ):
            varName = self.tkn
            if varName.value in li.BUILTINS:
                return res.failure(InvalidSyntaxError(
                    varName.startPos, varName.endPos,
                    "Cannot redefine builtin variable"
                ))
            res.registerAdvancement()
            self.advance()
            tkn = self.tkn
            res.registerAdvancement()
            self.advance()
            expr = res.register(self.expr())
            if res.err:
                return res
            if tkn.type == TT_DEFEQ:
                expr = IfNode([(BinOpNode(
                    VarAccessNode(varName),
                    Token(TT_EE, None, tkn.startPos, tkn.endPos),
                    NoneValueNode(tkn)
                ), expr)], VarAccessNode(varName))
            elif tkn.type == TT_PLUSEQ:
                expr = BinOpNode(VarAccessNode(varName), Token(TT_PLUS, None, tkn.startPos, tkn.endPos), expr)
            elif tkn.type == TT_MINUSEQ:
                expr = BinOpNode(VarAccessNode(varName), Token(TT_MINUS, None, tkn.startPos, tkn.endPos), expr)
            elif tkn.type == TT_MULEQ:
                expr = BinOpNode(VarAccessNode(varName), Token(TT_MUL, None, tkn.startPos, tkn.endPos), expr)
            elif tkn.type == TT_DIVEQ:
                expr = BinOpNode(VarAccessNode(varName), Token(TT_DIV, None, tkn.startPos, tkn.endPos), expr)
            elif tkn.type == TT_MODEQ:
                expr = BinOpNode(VarAccessNode(varName), Token(TT_MOD, None, tkn.startPos, tkn.endPos), expr)
            elif tkn.type == TT_POWEQ:
                expr = BinOpNode(VarAccessNode(varName), Token(TT_POW, None, tkn.startPos, tkn.endPos), expr)
            return res.success(VarAssignNode(varName, expr))

        node = res.register(self.binOp(
            self.compExpr, ((TT_KEYWORD, "and"), (TT_KEYWORD, "or"))
        ))
        if res.err:
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected valid expression"
            ))
        return res.success(node)

    def binOp(self, lFun, ops, rFun=None):
        if rFun is None:
            rFun = lFun

        res = ParseResult()
        left = res.register(lFun())

        while self.tkn.type in ops or (self.tkn.type, self.tkn.value) in ops:
            opTkn = self.tkn
            res.registerAdvancement()
            self.advance()
            right = res.register(rFun())
            if res.err:
                return res
            left = BinOpNode(left, opTkn, right)

        return res.success(left)

    def program(self):
        res = ParseResult()
        
        exprs = [res.register(self.expr())]
        if res.err:
            return res
        
        while self.tkn.type not in (TT_RBRACKET, TT_EOF):
            if self.tkn.type == TT_SEMICOLON:
                res.registerAdvancement()
                self.advance()
            
            if self.tkn.type in (TT_RBRACKET, TT_EOF):
                break

            exprs.append(res.register(self.expr()))
            if res.err:
                return res
        
        return res.success(BlockNode(exprs))
