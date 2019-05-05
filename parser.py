from error import InvalidSyntaxError
from tokens import *
from lexer import Token

################
# NODES
################


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
                 stepValueNode, bodyNode):
        self.varNameTkn = varNameTkn
        self.startValueNode = startValueNode
        self.endValueNode = endValueNode
        self.stepValueNode = stepValueNode
        self.bodyNode = bodyNode

        self.startPos = varNameTkn.startPos
        self.endPos = bodyNode.endPos


class WhileNode:
    def __init__(self, condNode, bodyNode):
        self.condNode = condNode
        self.bodyNode = bodyNode

        self.startPos = condNode.startPos
        self.endPos = bodyNode.endPos


class FuncDefNode:
    def __init__(self, varNameTkn, argNameTkns, bodyNode):
        self.varNameTkn = varNameTkn
        self.argNameTkns = argNameTkns
        self.bodyNode = bodyNode

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


class BlockNode:
    def __init__(self, exprNodes):
        self.exprNodes = exprNodes

        if len(exprNodes) > 0:
            self.startPos = exprNodes[0].startPos
            self.endPos = exprNodes[-1].endPos
        else:
            self.startPos = None
            self.endPos = None


class DispNode:
    def __init__(self, bodyNode):
        self.bodyNode = bodyNode

        self.startPos = bodyNode.startPos
        self.endPos = bodyNode.endPos


class InputNode:
    def __init__(self, inputTkn):
        self.startPos = inputTkn.startPos
        self.endPos = inputTkn.endPos


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
        res = self.program()
        if not res.err and self.tkn.type != TT_EOF:
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected ';'"
            ))
        return res
    
    def dispExpr(self):
        res = ParseResult()

        if not self.tkn.matches(TT_KEYWORD, "disp"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'disp'"
            ))
        res.registerAdvancement()
        self.advance()

        body = res.register(self.block())
        if res.err:
            return res
        
        return res.success(DispNode(body))
    
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

        startValue = res.register(self.block())
        if res.err:
            return res

        if not self.tkn.matches(TT_KEYWORD, "to"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'to'"
            ))
        res.registerAdvancement()
        self.advance()

        endValue = res.register(self.block())
        if res.err:
            return res

        if self.tkn.matches(TT_KEYWORD, "step"):
            res.registerAdvancement()
            self.advance()

            stepValue = res.register(self.block())
            if res.err:
                return res
            if not self.tkn.matches(TT_KEYWORD, "then"):
                return res.failure(InvalidSyntaxError(
                    self.tkn.startPos, self.tkn.endPos,
                    "Expected 'then'"
                ))
        else:
            stepValue = None
            if not self.tkn.matches(TT_KEYWORD, "then"):
                return res.failure(InvalidSyntaxError(
                    self.tkn.startPos, self.tkn.endPos,
                    "Expected 'step' or then'"
                ))

        res.registerAdvancement()
        self.advance()

        body = res.register(self.block())
        if res.err:
            return res

        return res.success(ForNode(
            varName, startValue, endValue, stepValue, body
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

        cond = res.register(self.block())
        if res.err:
            return res

        if not self.tkn.matches(TT_KEYWORD, "then"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'then'"
            ))
        res.registerAdvancement()
        self.advance()

        body = res.register(self.block())
        if res.err:
            return res

        return res.success(WhileNode(cond, body))

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
        cond = res.register(self.block())
        if res.err:
            return res

        if not self.tkn.matches(TT_KEYWORD, "then"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'then'"
            ))
        res.registerAdvancement()
        self.advance()

        expr = res.register(self.block())
        if res.err:
            return res
        cases.append((cond, expr))

        while self.tkn.matches(TT_KEYWORD, "elif"):
            res.registerAdvancement()
            self.advance()

            cond = res.register(self.block())
            if res.err:
                return res

            if not self.tkn.matches(TT_KEYWORD, "then"):
                return res.failure(InvalidSyntaxError(
                    self.tkn.startPos, self.tkn.endPos,
                    "Expected 'then'"
                ))
            res.registerAdvancement()
            self.advance()

            expr = res.register(self.block())
            if res.err:
                return res
            cases.append((cond, expr))

        if self.tkn.matches(TT_KEYWORD, "else"):
            res.registerAdvancement()
            self.advance()

            elseCase = res.register(self.block())
            if res.err:
                return res

        return res.success(IfNode(cases, elseCase))

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
            return res.success(VarAccessNode(tkn))
        elif tkn.type == TT_LPAREN:
            res.registerAdvancement()
            self.advance()
            expr = res.register(self.block())
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
        elif tkn.matches(TT_KEYWORD, "if"):
            ifExpr = res.register(self.ifExpr())
            if res.err:
                return res
            return res.success(ifExpr)
        elif tkn.matches(TT_KEYWORD, "for"):
            forExpr = res.register(self.forExpr())
            if res.err:
                return res
            return res.success(forExpr)
        elif tkn.matches(TT_KEYWORD, "while"):
            whileExpr = res.register(self.whileExpr())
            if res.err:
                return res
            return res.success(whileExpr)
        elif tkn.matches(TT_KEYWORD, "fun"):
            funcDef = res.register(self.funcDef())
            if res.err:
                return res
            return res.success(funcDef)
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

        return res.failure(InvalidSyntaxError(
            tkn.startPos, tkn.endPos,
            "Expected keyword, int, float, identifier, '+', '-' or '('"
        ))

    def call(self):
        res = ParseResult()
        atom = res.register(self.atom())
        if res.err:
            return res

        if self.tkn.type == TT_LPAREN:
            res.registerAdvancement()
            self.advance()
            argNodes = []

            if self.tkn.type == TT_RPAREN:
                res.registerAdvancement()
                self.advance()
            else:
                argNodes.append(res.register(self.block()))
                if res.err:
                    return res

                while self.tkn.type == TT_COMMA:
                    res.registerAdvancement()
                    self.advance()

                    argNodes.append(res.register(self.block()))
                    if res.err:
                        return res

                if self.tkn.type != TT_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.tkn.startPos, self.tkn.endPos,
                        "Expected ')'"
                    ))
                res.registerAdvancement()
                self.advance()

            return res.success(CallNode(atom, argNodes))
        return res.success(atom)

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

        if self.tkn.type == TT_IDENTIFIER and self.nextTkn.type == TT_EQ:
            varName = self.tkn
            res.registerAdvancement()
            self.advance()
            res.registerAdvancement()
            self.advance()
            expr = res.register(self.block())
            if res.err:
                return res
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

    def funcDef(self):
        res = ParseResult()

        if not self.tkn.matches(TT_KEYWORD, "fun"):
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected 'fun'"
            ))
        res.registerAdvancement()
        self.advance()

        if self.tkn.type == TT_IDENTIFIER:
            varNameTkn = self.tkn
            res.registerAdvancement()
            self.advance()
            if self.tkn.type != TT_LPAREN:
                print("YOLO")
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

        if self.tkn.type != TT_ARROW:
            return res.failure(InvalidSyntaxError(
                self.tkn.startPos, self.tkn.endPos,
                "Expected '->'"
            ))
        res.registerAdvancement()
        self.advance()

        nodeToReturn = res.register(self.block())
        if res.err:
            return res

        return res.success(FuncDefNode(varNameTkn, argNameTkns, nodeToReturn))
    
    def block(self):
        res = ParseResult()

        if self.tkn.type == TT_LBRACKET:
            res.registerAdvancement()
            self.advance()

            if self.tkn.type == TT_RBRACKET:
                res.registerAdvancement()
                self.advance()

                return res.success(BlockNode([]))

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
        
        expr = res.register(self.expr())
        if res.err:
            return res
        
        return res.success(expr)
    
    def program(self):
        res = ParseResult()
        
        exprs = [res.register(self.block())]
        if res.err:
            return res
        
        while self.tkn.type == TT_SEMICOLON:
            res.registerAdvancement()
            self.advance()
            
            if self.tkn.type in (TT_RBRACKET, TT_EOF):
                break

            exprs.append(res.register(self.block()))
            if res.err:
                return res
        
        return res.success(BlockNode(exprs))