import os

KEYWORDS = ["break", "else", "if", "int", "return", "void", "while", "switch", "case", "default", "goto", "for"]
KEYWORD_SET = set(KEYWORDS)
SINGLE_SYMBOLS = set([';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '/', '=', '<'])
WHITESPACE = set([' ', '\n', '\r', '\t', '\v', '\f'])

class Scanner:
    def __init__(self, text):
        self.text = text
        self.length = len(text)
        self.index = 0
        self.line = 1

    def current_char(self):
        return self.text[self.index] if self.index < self.length else None

    def next_char(self):
        return self.text[self.index + 1] if self.index + 1 < self.length else None

    def is_letter(self, ch):
        return ch is not None and (('a' <= ch <= 'z') or ('A' <= ch <= 'Z'))

    def is_digit(self, ch):
        return ch is not None and ('0' <= ch <= '9')

    def is_identifier_char(self, ch):
        return self.is_letter(ch) or self.is_digit(ch)

    def is_token_delimiter(self, ch):
        return ch is None or ch in WHITESPACE or ch in SINGLE_SYMBOLS

    def skip_whitespace(self):
        if self.current_char() == '\n':
            self.line += 1
        self.index += 1

    def get_next_token(self):
        while self.index < self.length:
            ch = self.current_char()
            start_line = self.line

            if ch in WHITESPACE:
                self.skip_whitespace()

            elif ch == '/':
                if self.next_char() == '*':
                    self.index += 2
                    while self.index < self.length:
                        if self.text[self.index] == '*' and self.index + 1 < self.length and self.text[self.index + 1] == '/':
                            self.index += 2
                            break
                        if self.text[self.index] == '\n':
                            self.line += 1
                        self.index += 1
                else:
                    self.index += 1
                    return (start_line, "SYMBOL", '/')

            elif self.is_letter(ch):
                start = self.index
                while self.index < self.length and self.is_identifier_char(self.text[self.index]):
                    self.index += 1
                if not self.is_token_delimiter(self.current_char()):
                    self.index += 1
                    continue
                lexeme = self.text[start:self.index]
                token_type = "KEYWORD" if lexeme in KEYWORD_SET else "ID"
                return (start_line, token_type, lexeme)

            elif self.is_digit(ch):
                start = self.index
                while self.index < self.length and self.is_digit(self.text[self.index]):
                    self.index += 1
                invalid = False
                if self.index - start > 1 and self.text[start] == '0': invalid = True
                if self.current_char() is not None and self.is_identifier_char(self.current_char()): invalid = True
                
                if invalid:
                    while self.index < self.length and self.is_identifier_char(self.text[self.index]):
                        self.index += 1
                    continue
                return (start_line, "NUM", self.text[start:self.index])

            elif ch == '=':
                if self.next_char() == '=':
                    self.index += 2
                    return (start_line, "SYMBOL", '==')
                else:
                    self.index += 1
                    return (start_line, "SYMBOL", '=')

            elif ch in SINGLE_SYMBOLS:
                self.index += 1
                return (start_line, "SYMBOL", ch)

            else:
                self.index += 1

        return (self.line + 1, "EOF", "$")


GRAMMAR = {
    "Program": [["DeclarationList"]],
    "DeclarationList": [["Declaration", "DeclarationList"], ["EPSILON"]],
    "Declaration": [["DeclarationInitial", "DeclarationPrime"]],
    "DeclarationInitial": [["TypeSpecifier", "ID"]],
    "DeclarationPrime": [["FunDeclarationPrime"], ["VarDeclarationPrime"]],
    "VarDeclarationPrime": [[";"], ["[", "NUM", "]", "VarDeclArrayPrime"], ["=", "Expression", ";"]],
    "VarDeclArrayPrime": [[";"], ["=", "Expression", ";"]],
    "FunDeclarationPrime": [["(", "Params", ")", "CompoundStmt"]],
    "TypeSpecifier": [["int"], ["void"]],
    "Params": [["int", "ID", "ParamPrime", "ParamList"], ["void"]],
    "ParamList": [[",", "Param", "ParamList"], ["EPSILON"]],
    "Param": [["DeclarationInitial", "ParamPrime"]],
    "ParamPrime": [["[", "]"], ["EPSILON"]],
    "CompoundStmt": [["{", "DeclarationList", "StatementList", "}"]],
    "StatementList": [["Statement", "StatementList"], ["EPSILON"]],
    "Statement": [["if", "(", "Expression", ")", "Statement", "ElseOpt"], ["OtherStmt"]],
    "ElseOpt": [["else", "Statement"], ["EPSILON"]],
    "OtherStmt": [["ID", "IdStatementPrime"], ["SimpleExpressionZegond", ";"], ["CompoundStmt"], ["IterationStmt"], ["ReturnStmt"], ["BreakStmt"], ["GotoStmt"], ["SwitchStmt"], [";"]],
    "IdStatementPrime": [[":", "Statement"], ["B", ";"]],
    "BreakStmt": [["break", ";"]],
    "IterationStmt": [["while", "(", "Expression", ")", "Statement"]],
    "ReturnStmt": [["return", "ReturnStmtPrime"]],
    "ReturnStmtPrime": [[";"], ["Expression", ";"]],
    "Expression": [["SimpleExpressionZegond"], ["ID", "B"]],
    "B": [["=", "Expression"], ["[", "Expression", "]", "H"], ["SimpleExpressionPrime"]],
    "H": [["=", "Expression"], ["G", "D", "C"]],
    "SimpleExpressionZegond": [["AdditiveExpressionZegond", "C"]],
    "SimpleExpressionPrime": [["AdditiveExpressionPrime", "C"]],
    "C": [["Relop", "AdditiveExpression"], ["EPSILON"]],
    "Relop": [["<"], ["=="]],
    "AdditiveExpression": [["Term", "D"]],
    "AdditiveExpressionPrime": [["TermPrime", "D"]],
    "AdditiveExpressionZegond": [["TermZegond", "D"]],
    "D": [["Addop", "Term", "D"], ["EPSILON"]],
    "Addop": [["+"], ["-"]],
    "Term": [["SignedFactor", "G"]],
    "TermPrime": [["SignedFactorPrime", "G"]],
    "TermZegond": [["SignedFactorZegond", "G"]],
    "G": [["Mulop", "SignedFactor", "G"], ["EPSILON"]],
    "Mulop": [["*"], ["/"]],
    "SignedFactor": [["+", "Factor"], ["-", "Factor"], ["Factor"]],
    "SignedFactorPrime": [["FactorPrime"]],
    "SignedFactorZegond": [["+", "Factor"], ["-", "Factor"], ["FactorZegond"]],
    "Factor": [["(", "Expression", ")"], ["ID", "VarCallPrime"], ["NUM"]],
    "VarCallPrime": [["(", "Args", ")"], ["VarPrime"]],
    "VarPrime": [["[", "Expression", "]"], ["EPSILON"]],
    "FactorPrime": [["(", "Args", ")"], ["EPSILON"]],
    "FactorZegond": [["(", "Expression", ")"], ["NUM"]],
    "Args": [["ArgList"], ["EPSILON"]],
    "ArgList": [["Expression", "ArgListPrime"]],
    "ArgListPrime": [[",", "Expression", "ArgListPrime"], ["EPSILON"]],
    "GotoStmt": [["goto", "ID", ";"]],
    "SwitchStmt": [["switch", "(", "Expression", ")", "{", "CaseList", "DefaultOpt", "}"]],
    "CaseList": [["Case", "CaseList"], ["EPSILON"]],
    "Case": [["case", "Constant", ":", "StatementList"]],
    "Constant": [["NUM"]],
    "DefaultOpt": [["default", ":", "StatementList"], ["EPSILON"]]
}

TERMINALS = {"int", "void", "if", "else", "break", "while", "return", "switch", "case", "default", "goto", 
             "ID", "NUM", ";", ":", ",", "[", "]", "(", ")", "{", "}", "+", "-", "*", "/", "=", "<", "==", "$"}
NON_TERMINALS = set(GRAMMAR.keys())

def compute_first_sets():
    first = {nt: set() for nt in NON_TERMINALS}
    for t in TERMINALS: first[t] = {t}
    first["EPSILON"] = {"EPSILON"}

    changed = True
    while changed:
        changed = False
        for nt, rules in GRAMMAR.items():
            before_len = len(first[nt])
            for rule in rules:
                for symbol in rule:
                    first[nt].update(first[symbol] - {"EPSILON"})
                    if "EPSILON" not in first[symbol]:
                        break
                else:
                    first[nt].add("EPSILON")
            if len(first[nt]) > before_len:
                changed = True
    return first

def compute_follow_sets(first):
    follow = {nt: set() for nt in NON_TERMINALS}
    follow["Program"].add("$")

    changed = True
    while changed:
        changed = False
        for nt, rules in GRAMMAR.items():
            for rule in rules:
                for i, symbol in enumerate(rule):
                    if symbol in NON_TERMINALS:
                        before_len = len(follow[symbol])
                        next_first = set()
                        for next_sym in rule[i+1:]:
                            next_first.update(first[next_sym] - {"EPSILON"})
                            if "EPSILON" not in first[next_sym]:
                                break
                        else:
                            next_first.update(follow[nt])
                        
                        follow[symbol].update(next_first)
                        if len(follow[symbol]) > before_len:
                            changed = True
    return follow

def create_parsing_table(first, follow):
    table = {nt: {} for nt in NON_TERMINALS}
    for nt, rules in GRAMMAR.items():
        for rule in rules:
            first_of_rule = set()
            for symbol in rule:
                first_of_rule.update(first[symbol] - {"EPSILON"})
                if "EPSILON" not in first[symbol]:
                    break
            else:
                first_of_rule.add("EPSILON")

            for t in first_of_rule - {"EPSILON"}:
                if t not in table[nt]:
                    table[nt][t] = rule
            if "EPSILON" in first_of_rule:
                for t in follow[nt]:
                    if t not in table[nt]:
                        table[nt][t] = rule
    return table


class ParseNode:
    def __init__(self, symbol):
        self.symbol = symbol
        self.name = symbol
        self.children = []
        self.parent = None

    def add_child(self, child_node):
        child_node.parent = self
        self.children.append(child_node)


class Parser:
    def __init__(self, scanner):
        self.scanner = scanner
        self.first = compute_first_sets()
        self.follow = compute_follow_sets(self.first)
        self.table = create_parsing_table(self.first, self.follow)
        self.errors = []

    def get_grammar_symbol(self, token):
        _, t_type, lexeme = token
        if t_type == "EOF": return "$"
        if t_type == "ID": return "ID"
        if t_type == "NUM": return "NUM"
        return lexeme

    def parse(self):
        root = ParseNode("Program")
        eof_node = ParseNode("$")
        decl_node = ParseNode("DeclarationList")
        
        root.add_child(decl_node)
        root.add_child(eof_node)
        
        stack = [eof_node, decl_node]
        token = self.scanner.get_next_token()

        while stack:
            top = stack[-1]
            lookahead_sym = self.get_grammar_symbol(token)

            if top.symbol in TERMINALS or top.symbol == "$":
                if top.symbol == lookahead_sym:
                    
                    if top.symbol != "$":
                        top.name = f"({token[1]}, {token[2]}) "
                    stack.pop()
                    token = self.scanner.get_next_token()
                else:
                    if top.symbol == "$":
                        break
                    else:
                        self.errors.append(f"#{token[0]} : syntax error, missing {top.symbol}")
                        if top.parent:
                            top.parent.children.remove(top)
                        stack.pop()
            else:
                rule = self.table[top.symbol].get(lookahead_sym)
                if rule is not None:
                    stack.pop()
                    if rule == ["EPSILON"]:
                        child = ParseNode("epsilon")
                        top.add_child(child)
                    else:
                        children = []
                        for sym in rule:
                            child = ParseNode(sym)
                            children.append(child)
                            top.add_child(child)
                        for child in reversed(children):
                            stack.append(child)
                else:
                    if lookahead_sym in self.follow[top.symbol] or lookahead_sym == "$":
                        self.errors.append(f"#{token[0]} : syntax error, missing {top.symbol}")
                        if top.parent:
                            top.parent.children.remove(top)
                        stack.pop()
                    else:
                        self.errors.append(f"#{token[0]} : syntax error, illegal {lookahead_sym}")
                        token = self.scanner.get_next_token()

        return root

def get_tree_str(node, prefix="", is_last=True, is_root=True):
    if not node: return ""
    res = ""
    if is_root:
        res += f"{node.name}\n"
        child_prefix = ""
    else:
        marker = "└── " if is_last else "├── "
        res += f"{prefix}{marker}{node.name}\n"
        child_prefix = prefix + ("    " if is_last else "│   ")

    for i, child in enumerate(node.children):
        res += get_tree_str(child, child_prefix, i == (len(node.children) - 1), False)
    return res

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, 'input.txt')

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        text = ''

    scanner = Scanner(text)
    parser = Parser(scanner)
    
    parse_tree_root = parser.parse()

    tree_output = get_tree_str(parse_tree_root)
    with open(os.path.join(base_dir, 'parse_tree.txt'), 'w', encoding='utf-8') as f:
        f.write(tree_output.rstrip('\n') + '\n')

    with open(os.path.join(base_dir, 'syntax_errors.txt'), 'w', encoding='utf-8') as f:
        if not parser.errors:
            f.write("There is no syntax error.\n")
        else:
            for err in parser.errors:
                f.write(err + "\n")

if __name__ == '__main__':
    main()