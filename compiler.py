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
    "Program": [["#init", "DeclarationList", "#end_program"]],
    "DeclarationList": [["Declaration", "DeclarationList"], ["EPSILON"]],
    "Declaration": [["DeclarationInitial", "DeclarationPrime"]],
    "DeclarationInitial": [["TypeSpecifier", "ID", "#declare_id"]],
    "DeclarationPrime": [["FunDeclarationPrime"], ["VarDeclarationPrime"]],
    "VarDeclarationPrime": [[";", "#clean_sym"], ["[", "NUM", "#declare_array", "]", "VarDeclArrayPrime"], ["=", "Expression", "#declare_assign", ";"]],
    "VarDeclArrayPrime": [[";", "#clean_sym"], ["=", "Expression", "#declare_assign", ";"]],
    "FunDeclarationPrime": [["#declare_func", "(", "Params", ")", "CompoundStmt", "#end_func"]],
    "TypeSpecifier": [["int", "#push_int"], ["void", "#push_void"]],
    "Params": [["int", "#push_int", "ID", "#declare_param", "ParamPrime", "ParamList"], ["void"]],
    "ParamList": [[",", "Param", "ParamList"], ["EPSILON"]],
    "Param": [["DeclarationInitial", "#declare_param_initial", "ParamPrime"]],
    "ParamPrime": [["[", "]", "#param_array"], ["EPSILON", "#clean_sym"]],
    "CompoundStmt": [["{", "DeclarationList", "StatementList", "}"]],
    "StatementList": [["Statement", "StatementList"], ["EPSILON"]],
    "Statement": [["if", "(", "Expression", ")", "#save", "Statement", "ElseOpt"], ["OtherStmt"]],
    "ElseOpt": [["else", "#jpf_save", "Statement", "#jp"], ["EPSILON", "#jpf"]],
    "OtherStmt": [["ID", "IdStatementPrime"], ["SimpleExpressionZegond", ";", "#clean_sym"], ["CompoundStmt"], ["IterationStmt"], ["ReturnStmt"], ["BreakStmt"], ["GotoStmt"], ["SwitchStmt"], [";"]],
    "IdStatementPrime": [[":", "#label_decl", "Statement"], ["#pid", "B", ";", "#clean_sym"]],
    "BreakStmt": [["break", "#break", ";"]],
    "IterationStmt": [["while", "(", "#label", "Expression", ")", "#save", "Statement", "#while"]],
    "ReturnStmt": [["return", "ReturnStmtPrime"]],
    "ReturnStmtPrime": [[";", "#return_void"], ["Expression", "#return_val", ";"]],
    "Expression": [["SimpleExpressionZegond"], ["ID", "#pid", "B"]],
    "B": [["=", "Expression", "#assign"], ["[", "Expression", "]", "#array_elem", "H"], ["SimpleExpressionPrime"]],
    "H": [["=", "Expression", "#assign"], ["G", "D", "C"]],
    "SimpleExpressionZegond": [["AdditiveExpressionZegond", "C"]],
    "SimpleExpressionPrime": [["AdditiveExpressionPrime", "C"]],
    "C": [["Relop", "AdditiveExpression", "#relop"], ["EPSILON"]],
    "Relop": [["<", "#push_lt"], ["==", "#push_eq"]],
    "AdditiveExpression": [["Term", "D"]],
    "AdditiveExpressionPrime": [["TermPrime", "D"]],
    "AdditiveExpressionZegond": [["TermZegond", "D"]],
    "D": [["Addop", "Term", "#addsub", "D"], ["EPSILON"]],
    "Addop": [["+", "#push_add"], ["-", "#push_sub"]],
    "Term": [["SignedFactor", "G"]],
    "TermPrime": [["SignedFactorPrime", "G"]],
    "TermZegond": [["SignedFactorZegond", "G"]],
    "G": [["Mulop", "SignedFactor", "#multdiv", "G"], ["EPSILON"]],
    "Mulop": [["*", "#push_mult"], ["/", "#push_div"]],
    "SignedFactor": [["+", "Factor", "#pos"], ["-", "Factor", "#neg"], ["Factor"]],
    "SignedFactorPrime": [["FactorPrime"]],
    "SignedFactorZegond": [["+", "Factor", "#pos"], ["-", "Factor", "#neg"], ["FactorZegond"]],
    "Factor": [["(", "Expression", ")"], ["ID", "#pid", "VarCallPrime"], ["NUM", "#pnum"]],
    "VarCallPrime": [["(", "#start_call", "Args", ")", "#call"], ["VarPrime"]],
    "VarPrime": [["[", "Expression", "]", "#array_elem"], ["EPSILON"]],
    "FactorPrime": [["(", "#start_call", "Args", ")", "#call"], ["EPSILON"]],
    "FactorZegond": [["(", "Expression", ")"], ["NUM", "#pnum"]],
    "Args": [["ArgList"], ["EPSILON"]],
    "ArgList": [["Expression", "ArgListPrime"]],
    "ArgListPrime": [[",", "Expression", "ArgListPrime"], ["EPSILON"]],
    "GotoStmt": [["goto", "ID", "#goto", ";"]],
    "SwitchStmt": [["switch", "(", "Expression", ")", "#switch_start", "{", "CaseList", "DefaultOpt", "}", "#switch_end"]],
    "CaseList": [["Case", "CaseList"], ["EPSILON"]],
    "Case": [["case", "Constant", "#case_test", ":", "StatementList", "#case_end"]],
    "Constant": [["NUM", "#pnum"]],
    "DefaultOpt": [["default", ":", "#default_start", "StatementList"], ["EPSILON"]]
}

TERMINALS = {"int", "void", "if", "else", "break", "while", "return", "switch", "case", "default", "goto",
             "ID", "NUM", ";", ":", ",", "[", "]", "(", ")", "{", "}", "+", "-", "*", "/", "=", "<", "==", "$"}

action_symbols = set()
for rules in GRAMMAR.values():
    for rule in rules:
        for sym in rule:
            if sym.startswith("#"):
                action_symbols.add(sym)

for sym in action_symbols:
    if sym not in GRAMMAR:
        GRAMMAR[sym] = [["EPSILON"]]

NON_TERMINALS = set(GRAMMAR.keys())

def is_action(sym):
    return sym.startswith("#")

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

class CodeGen:
    def __init__(self):
        self.PB = []
        self.SS = []
        self.break_stack = []
        self.switch_stack = []
        self.labels = {}
        self.unresolved_gotos = {}
        self.temp_address = 500
        self.data_address = 100
        self.symbol_table = [{}]
        self.current_func = None
        self.last_id = ""
        self.last_num = ""
        self.last_id_line = 1
        self.last_num_line = 1
        self.current_line = 1


        self.sem_stack = []
        self.semantic_errors = []

        self._add_builtin()

    def _add_builtin(self):
        addr = self.get_data_addr(4)
        self.symbol_table[0]['output'] = {
            'name': 'output',
            'type': 'func',
            'is_builtin': True,
            'address': addr,
            'params': [self.get_data_addr(4)],
            'sem_param_types': ['int'],
            'ret_type': 'void',
            'ret_val': self.get_data_addr(4),
            'ret_addr': self.get_data_addr(4),
            'start_pc': -1
        }

    def get_data_addr(self, size=4):
        addr = self.data_address
        self.data_address += size
        return addr

    def get_temp(self):
        addr = self.temp_address
        self.temp_address += 4
        return addr

    def generate(self, op, arg1="", arg2="", res=""):
        self.PB.append([op, arg1, arg2, res])

    def lookup(self, name):
        for scope in reversed(self.symbol_table):
            if name in scope:
                return scope[name]
        return None

    def lookup_by_addr(self, addr):
        for scope in reversed(self.symbol_table):
            for sym in scope.values():
                if sym.get('address') == addr:
                    return sym
        return None


    def semantic_error(self, line, message):
        self.semantic_errors.append(f"#{line} : Semantic Error! {message}")

    def semantic_type(self, sym):
        if sym is None:
            return "unknown"
        t = sym.get('type')
        if t in ('array', 'array_ptr'):
            return 'array'
        if t == 'func':
            return 'func'
        return t if t is not None else 'unknown'

    def sem_value(self, type_, line=None, sym=None):
        return {
            'type': type_ if type_ is not None else 'unknown',
            'line': self.current_line if line is None else line,
            'sym': sym,
        }

    def sem_pop(self):
        if not self.sem_stack:
            return self.sem_value('unknown')
        return self.sem_stack.pop()

    def check_int_operand(self, value):
        t = value.get('type', 'unknown')
        if t not in ('int', 'unknown'):
            self.semantic_error(
                value.get('line', self.current_line),
                f"Type mismatch in operands, Got {t} instead of int."
            )
            return False
        return True

    def finalize_plain_declaration(self, sym):
        if not isinstance(sym, dict) or not sym.get('pending_decl'):
            return
        if sym.get('decl_type') == 'void':
            self.semantic_error(
                sym.get('decl_line', self.current_line),
                f"Illegal type of void for '{sym.get('name', '')}'."
            )
        sym['pending_decl'] = False


    def init(self):

        pass

    def end_program(self):
        sym = self.lookup('main')
        if sym:
            self.generate("ASSIGN", f"#{len(self.PB) + 2}", sym['ret_addr'])
            self.generate("JP", sym['start_pc'])
            self.generate("ASSIGN", "#0", "0")

    def declare_id(self):
        type_ = self.SS.pop()
        name = self.last_id
        addr = self.get_data_addr(4)
        sym = {
            'name': name, 'type': type_, 'address': addr,
            'decl_type': type_, 'decl_line': self.last_id_line,
            'pending_decl': True
        }
        self.symbol_table[-1][name] = sym
        self.SS.append(sym)

    def clean_sym(self):
        if self.SS:
            top = self.SS[-1]
            if isinstance(top, dict):
                self.finalize_plain_declaration(top)
            self.SS.pop()


        if self.sem_stack and self.sem_stack[-1] != "CALL_MARKER":
            self.sem_stack.pop()

    def declare_array(self):
        size = int(self.last_num)
        sym = self.SS.pop()
        if sym.get('decl_type') == 'void':
            self.semantic_error(
                sym.get('decl_line', self.current_line),
                f"Illegal type of void for '{sym.get('name', '')}'."
            )
        sym['type'] = 'array'
        sym['size'] = size
        sym['pending_decl'] = False
        self.get_data_addr((size - 1) * 4)
        self.SS.append(sym)

    def declare_assign(self):
        val = self.SS.pop()
        sym = self.SS.pop()

        invalid_void = sym.get('decl_type') == 'void'
        if invalid_void:
            self.semantic_error(
                sym.get('decl_line', self.current_line),
                f"Illegal type of void for '{sym.get('name', '')}'."
            )
        sym['pending_decl'] = False

        rhs = self.sem_pop()
        lhs_type = self.semantic_type(sym)
        rhs_type = rhs.get('type', 'unknown')
        if (not invalid_void and lhs_type not in ('unknown', 'func') and
                rhs_type != 'unknown' and lhs_type != rhs_type):
            self.semantic_error(
                sym.get('decl_line', self.current_line),
                f"Type mismatch in operands, Got {lhs_type} instead of {rhs_type}."
            )

        self.generate("ASSIGN", val, sym['address'])

    def declare_func(self):
        sym = self.SS.pop()
        self.data_address -= 4
        sym['ret_type'] = sym['type']
        sym['type'] = 'func'
        sym['params'] = []
        sym['pending_decl'] = False


        func_skip_hole = len(self.PB)
        self.PB.append(None)
        self.SS.append(func_skip_hole)

        sym['start_pc'] = len(self.PB)
        sym['ret_val'] = self.get_data_addr(4)
        sym['ret_addr'] = self.get_data_addr(4)

        self.symbol_table.append({})
        self.current_func = sym
        self.labels = {}
        self.unresolved_gotos = {}

    def end_func(self):
        self.symbol_table.pop()
        self.generate("JP", f"@{self.current_func['ret_addr']}")

        func_skip_hole = self.SS.pop()
        self.PB[func_skip_hole] = ["JP", len(self.PB), "", ""]

        self.current_func = None


        self.sem_stack.clear()

    def push_int(self): self.SS.append('int')
    def push_void(self): self.SS.append('void')

    def declare_param(self):
        type_ = self.SS.pop()
        name = self.last_id
        addr = self.get_data_addr(4)
        sym = {
            'name': name, 'type': type_, 'address': addr,
            'decl_type': type_, 'decl_line': self.last_id_line,
            'pending_decl': True
        }
        self.symbol_table[-1][name] = sym


        self.current_func['params'].append(sym)
        self.SS.append(sym)

    def param_array(self):
        sym = self.SS.pop()
        if sym.get('decl_type') == 'void':
            self.semantic_error(
                sym.get('decl_line', self.current_line),
                f"Illegal type of void for '{sym.get('name', '')}'."
            )
        sym['type'] = 'array_ptr'
        sym['pending_decl'] = False

    def declare_param_initial(self):
        sym = self.SS[-1]
        self.current_func['params'].append(sym)

    def save(self):
        cond = self.SS.pop()
        self.SS.append(cond)
        self.SS.append(len(self.PB))
        self.PB.append(None)
        self.sem_pop()

    def jpf_save(self):
        hole = self.SS.pop()
        cond = self.SS.pop()
        self.PB[hole] = ["JPF", cond, len(self.PB) + 1, ""]
        self.SS.append(len(self.PB))
        self.PB.append(None)

    def jp(self):
        hole = self.SS.pop()
        self.PB[hole] = ["JP", len(self.PB), "", ""]

    def jpf(self):
        hole = self.SS.pop()
        cond = self.SS.pop()
        self.PB[hole] = ["JPF", cond, len(self.PB), ""]

    def label(self):
        self.SS.append(len(self.PB))
        self.break_stack.append([])

    def while_(self):
        hole = self.SS.pop()
        cond = self.SS.pop()
        start = self.SS.pop()
        self.generate("JP", start)
        self.PB[hole] = ["JPF", cond, len(self.PB), ""]
        for b_hole in self.break_stack.pop():
            self.PB[b_hole] = ["JP", len(self.PB), "", ""]

    def break_(self):
        if self.break_stack:
            self.break_stack[-1].append(len(self.PB))
            self.PB.append(None)
        else:
            self.semantic_error(
                self.current_line,
                "No 'while' found for 'break'."
            )

    def return_void(self):
        self.generate("JP", f"@{self.current_func['ret_addr']}")

    def return_val(self):
        val = self.SS.pop()
        self.sem_pop()
        self.generate("ASSIGN", val, self.current_func['ret_val'])
        self.generate("JP", f"@{self.current_func['ret_addr']}")

    def pid(self):
        sym = self.lookup(self.last_id)
        if sym:
            self.SS.append(sym['address'])
            st = self.semantic_type(sym)
            self.sem_stack.append(self.sem_value(st, self.last_id_line, sym))
        else:
            self.SS.append(0)
            self.semantic_error(
                self.last_id_line,
                f"'{self.last_id}' is not defined."
            )
            self.sem_stack.append(self.sem_value('unknown', self.last_id_line, None))

    def pnum(self):
        self.SS.append(f"#{self.last_num}")
        self.sem_stack.append(self.sem_value('int', self.last_num_line))

    def assign(self):
        val = self.SS.pop()
        addr = self.SS.pop()

        rhs = self.sem_pop()
        lhs = self.sem_pop()
        lhs_type = lhs.get('type', 'unknown')
        rhs_type = rhs.get('type', 'unknown')
        if lhs_type != 'unknown' and rhs_type != 'unknown' and lhs_type != rhs_type:


            self.semantic_error(
                lhs.get('line', self.current_line),
                f"Type mismatch in operands, Got {lhs_type} instead of {rhs_type}."
            )
        result_type = rhs_type if rhs_type != 'unknown' else lhs_type
        self.sem_stack.append(self.sem_value(result_type, lhs.get('line', self.current_line)))

        self.generate("ASSIGN", val, addr)
        self.SS.append(val)

    def array_elem(self):
        idx = self.SS.pop()
        base_addr = self.SS.pop()

        sem_idx = self.sem_pop()
        sem_base = self.sem_pop()
        base_type = sem_base.get('type', 'unknown')
        idx_type = sem_idx.get('type', 'unknown')
        if base_type not in ('array', 'unknown'):
            self.semantic_error(
                sem_base.get('line', self.current_line),
                f"Type mismatch in operands, Got {base_type} instead of array."
            )
        elif idx_type not in ('int', 'unknown'):
            self.semantic_error(
                sem_idx.get('line', self.current_line),
                f"Type mismatch in operands, Got {idx_type} instead of int."
            )
        self.sem_stack.append(self.sem_value('int', sem_base.get('line', self.current_line)))

        sym = self.lookup_by_addr(base_addr)
        t1 = self.get_temp()
        self.generate("MULT", idx, "#4", t1)
        t2 = self.get_temp()
        if sym and sym.get('type') == 'array_ptr':
            self.generate("ADD", base_addr, t1, t2)
        else:
            self.generate("ADD", f"#{base_addr}", t1, t2)
        self.SS.append(f"@{t2}")

    def relop(self):
        right = self.SS.pop()
        op = self.SS.pop()
        left = self.SS.pop()

        sem_right = self.sem_pop()
        sem_left = self.sem_pop()
        if self.check_int_operand(sem_left):
            self.check_int_operand(sem_right)
        self.sem_stack.append(self.sem_value('int', sem_left.get('line', self.current_line)))

        t = self.get_temp()
        self.generate(op, left, right, t)
        self.SS.append(t)

    def push_lt(self): self.SS.append("LT")
    def push_eq(self): self.SS.append("EQ")

    def addsub(self):
        right = self.SS.pop()
        op = self.SS.pop()
        left = self.SS.pop()

        sem_right = self.sem_pop()
        sem_left = self.sem_pop()
        if self.check_int_operand(sem_left):
            self.check_int_operand(sem_right)
        self.sem_stack.append(self.sem_value('int', sem_left.get('line', self.current_line)))

        t = self.get_temp()
        self.generate(op, left, right, t)
        self.SS.append(t)

    def push_add(self): self.SS.append("ADD")
    def push_sub(self): self.SS.append("SUB")

    def multdiv(self):
        right = self.SS.pop()
        op = self.SS.pop()
        left = self.SS.pop()

        sem_right = self.sem_pop()
        sem_left = self.sem_pop()
        if self.check_int_operand(sem_left):
            self.check_int_operand(sem_right)
        self.sem_stack.append(self.sem_value('int', sem_left.get('line', self.current_line)))

        t = self.get_temp()
        self.generate(op, left, right, t)
        self.SS.append(t)

    def push_mult(self): self.SS.append("MULT")
    def push_div(self): self.SS.append("DIV")

    def pos(self):


        sem_val = self.sem_pop()
        self.check_int_operand(sem_val)
        self.sem_stack.append(self.sem_value('int', sem_val.get('line', self.current_line)))

    def neg(self):
        val = self.SS.pop()
        sem_val = self.sem_pop()
        self.check_int_operand(sem_val)
        self.sem_stack.append(self.sem_value('int', sem_val.get('line', self.current_line)))
        t = self.get_temp()
        self.generate("SUB", "#0", val, t)
        self.SS.append(t)

    def start_call(self):
        self.SS.append("CALL_MARKER")
        self.sem_stack.append("CALL_MARKER")

    def call(self):

        sem_args = []
        while self.sem_stack and self.sem_stack[-1] != "CALL_MARKER":
            sem_args.insert(0, self.sem_stack.pop())
        if self.sem_stack and self.sem_stack[-1] == "CALL_MARKER":
            self.sem_stack.pop()
        sem_func = self.sem_pop()

        func_sem_sym = sem_func.get('sym') if isinstance(sem_func, dict) else None
        result_type = 'unknown'
        if func_sem_sym and func_sem_sym.get('type') == 'func':
            if func_sem_sym.get('is_builtin'):
                param_types = list(func_sem_sym.get('sem_param_types', ['int']))
            else:
                param_types = [
                    'array' if p.get('type') in ('array', 'array_ptr') else p.get('type', 'unknown')
                    for p in func_sem_sym.get('params', [])
                ]

            call_line = sem_func.get('line', self.current_line)
            if len(sem_args) != len(param_types):
                self.semantic_error(
                    call_line,
                    f"Mismatch in numbers of arguments of '{func_sem_sym.get('name', '')}'."
                )
            else:
                for i, (arg, expected_type) in enumerate(zip(sem_args, param_types), 1):
                    actual_type = arg.get('type', 'unknown')
                    if actual_type != 'unknown' and expected_type != 'unknown' and actual_type != expected_type:
                        self.semantic_error(
                            call_line,
                            f"Mismatch in type of argument {i} of '{func_sem_sym.get('name', '')}'. "
                            f"Expected '{expected_type}' but got '{actual_type}' instead."
                        )


                        break
            result_type = func_sem_sym.get('ret_type', 'void')
        elif sem_func.get('type') == 'unknown':

            result_type = 'unknown'

        self.sem_stack.append(self.sem_value(result_type, sem_func.get('line', self.current_line)))


        args = []
        while self.SS[-1] != "CALL_MARKER":
            args.insert(0, self.SS.pop())
        self.SS.pop()
        func_addr = self.SS.pop()
        sym = self.lookup_by_addr(func_addr)

        if not sym:
            self.SS.append(0)
            return

        if sym.get('is_builtin'):
            self.generate("PRINT", args[0] if args else "")
            self.SS.append(0)
        else:
            for i, arg in enumerate(args):
                if i < len(sym['params']):
                    param_sym = sym['params'][i]
                    param_addr = param_sym['address']
                    arg_sym = self.lookup_by_addr(arg) if isinstance(arg, int) else None

                    if param_sym.get('type') == 'array_ptr':
                        if arg_sym and arg_sym.get('type') == 'array':
                            self.generate("ASSIGN", f"#{arg}", param_addr)
                        else:
                            self.generate("ASSIGN", arg, param_addr)
                    else:
                        self.generate("ASSIGN", arg, param_addr)

            self.generate("ASSIGN", f"#{len(self.PB) + 2}", sym['ret_addr'])
            self.generate("JP", sym['start_pc'])
            if sym.get('ret_type') == 'void':
                self.SS.append("#0")
            else:
                t = self.get_temp()
                self.generate("ASSIGN", sym['ret_val'], t)
                self.SS.append(t)

    def goto(self):
        label = self.last_id
        if label in self.labels:
            self.generate("JP", self.labels[label])
        else:
            self.unresolved_gotos.setdefault(label, []).append(len(self.PB))
            self.PB.append(None)

    def label_decl(self):
        label = self.last_id
        self.labels[label] = len(self.PB)
        for hole in self.unresolved_gotos.get(label, []):
            self.PB[hole] = ["JP", len(self.PB), "", ""]
        self.unresolved_gotos[label] = []

    def switch_start(self):
        switch_val = self.SS.pop()
        self.sem_pop()
        self.switch_stack.append({'val': switch_val, 'fall_throughs': []})
        self.break_stack.append([])

    def case_test(self):
        const = self.SS.pop()
        self.sem_pop()
        switch_info = self.switch_stack[-1]
        t = self.get_temp()
        self.generate("EQ", switch_info['val'], const, t)
        jpf_hole = len(self.PB)
        self.PB.append(None)


        for hole in switch_info['fall_throughs']:
            self.PB[hole] = ["JP", len(self.PB), "", ""]
        switch_info['fall_throughs'] = []

        self.SS.append(jpf_hole)
        self.SS.append(t)

    def case_end(self):
        t = self.SS.pop()
        jpf_hole = self.SS.pop()

        fall_through_hole = len(self.PB)
        self.PB.append(None)

        self.switch_stack[-1]['fall_throughs'].append(fall_through_hole)
        self.PB[jpf_hole] = ["JPF", t, len(self.PB), ""]

    def default_start(self):
        switch_info = self.switch_stack[-1]
        for hole in switch_info['fall_throughs']:
            self.PB[hole] = ["JP", len(self.PB), "", ""]
        switch_info['fall_throughs'] = []

    def switch_end(self):
        switch_info = self.switch_stack.pop()
        for hole in switch_info['fall_throughs']:
            self.PB[hole] = ["JP", len(self.PB), "", ""]

        for hole in self.break_stack.pop():
            self.PB[hole] = ["JP", len(self.PB), "", ""]


class RecursiveCodeGen(CodeGen):


    FP = 10000
    SP = 10004
    STACK_BASE = 20000

    def __init__(self):


        self.PB = []
        self.SS = []
        self.break_stack = []
        self.switch_stack = []
        self.labels = {}
        self.unresolved_gotos = {}
        self.temp_address = 500
        self.data_address = 100
        self.scratch_address = 1000000
        self.symbol_table = [{}]
        self.current_func = None
        self.last_id = ""
        self.last_num = ""
        self.last_id_line = 1
        self.last_num_line = 1
        self.current_line = 1
        self.sem_stack = []
        self.semantic_errors = []
        self._add_recursive_builtin()

    def _add_recursive_builtin(self):
        self.symbol_table[0]['output'] = {
            'name': 'output', 'type': 'func', 'is_builtin': True,
            'params': [], 'sem_param_types': ['int'], 'ret_type': 'void',
            'start_pc': -1
        }


    def scratch(self):
        a = self.scratch_address
        self.scratch_address += 4
        return a

    def alloc_frame(self, size=4):
        off = self.current_func['next_offset']
        self.current_func['next_offset'] += size
        return off

    def value_desc_for_sym(self, sym):
        if sym.get('type') == 'func':
            return ('func', sym)
        storage = sym.get('storage')
        if sym.get('type') == 'array':
            if storage == 'frame':
                return ('array_frame', sym['frame_offset'], sym.get('size', 0), sym)
            return ('array_global', sym['address'], sym.get('size', 0), sym)
        if sym.get('type') == 'array_ptr':
            return ('array_param', sym['frame_offset'], sym)
        if storage == 'frame':
            return ('frame', sym['frame_offset'], sym)
        return ('global', sym.get('address', 0), sym)

    def new_temp_desc(self):
        if self.current_func is not None:
            return ('frame', self.alloc_frame(4), None)


        addr = self.get_data_addr(4)
        return ('global', addr, None)

    def imm(self, value):
        return ('imm', int(value))

    def _is_desc(self, x, kind=None):
        return isinstance(x, tuple) and x and (kind is None or x[0] == kind)

    def read_operand(self, desc):


        if self._is_desc(desc, 'imm'):
            return f"#{desc[1]}"
        if self._is_desc(desc, 'global'):
            return desc[1]
        if self._is_desc(desc, 'frame'):
            ptr = self.scratch()
            self.generate('ADD', self.FP, f"#{desc[1]}", ptr)
            return f"@{ptr}"
        if self._is_desc(desc, 'elem'):
            return self.element_operand(desc)
        if self._is_desc(desc, 'array_global'):


            return f"#{desc[1]}"
        if self._is_desc(desc, 'array_frame'):
            ptr = self.scratch()
            self.generate('ADD', self.FP, f"#{desc[1]}", ptr)
            return ptr
        if self._is_desc(desc, 'array_param'):
            ptr = self.scratch()
            self.generate('ADD', self.FP, f"#{desc[1]}", ptr)
            return f"@{ptr}"

        if isinstance(desc, str) and desc.startswith('#'):
            return desc
        if isinstance(desc, (int, str)):
            return desc
        return '#0'

    def write_operand(self, desc):
        if self._is_desc(desc, 'global'):
            return desc[1]
        if self._is_desc(desc, 'frame'):
            ptr = self.scratch()
            self.generate('ADD', self.FP, f"#{desc[1]}", ptr)
            return f"@{ptr}"
        if self._is_desc(desc, 'elem'):
            return self.element_operand(desc)
        if isinstance(desc, (int, str)):
            return desc
        return 0

    def array_base_operand(self, desc):

        if self._is_desc(desc, 'array_global'):
            return f"#{desc[1]}"
        if self._is_desc(desc, 'array_frame'):
            ptr = self.scratch()
            self.generate('ADD', self.FP, f"#{desc[1]}", ptr)
            return ptr
        if self._is_desc(desc, 'array_param'):
            slot = self.scratch()
            self.generate('ADD', self.FP, f"#{desc[1]}", slot)
            return f"@{slot}"
        return self.read_operand(desc)

    def element_operand(self, desc):
        _, base, idx = desc
        idx_op = self.read_operand(idx)
        scaled = self.scratch()
        self.generate('MULT', idx_op, '#4', scaled)
        base_op = self.array_base_operand(base)
        address = self.scratch()
        self.generate('ADD', base_op, scaled, address)
        return f"@{address}"

    def stack_slot_destination(self, offset):
        ptr = self.scratch()
        self.generate('ADD', self.SP, f"#{offset}", ptr)
        return f"@{ptr}"

    def emit_function_epilogue(self):

        self.generate('ASSIGN', self.FP, self.SP)
        old_fp_ptr = self.scratch()
        ret_ptr = self.scratch()
        ret_pc = self.scratch()
        self.generate('ADD', self.SP, '#8', old_fp_ptr)
        self.generate('ADD', self.SP, '#4', ret_ptr)
        self.generate('ASSIGN', f"@{ret_ptr}", ret_pc)
        self.generate('ASSIGN', f"@{old_fp_ptr}", self.FP)
        self.generate('JP', f"@{ret_pc}")


    def init(self):
        self.generate('ASSIGN', '#0', self.FP)
        self.generate('ASSIGN', f"#{self.STACK_BASE}", self.SP)

    def end_program(self):
        sym = self.lookup('main')
        if not sym:
            return
        ret_slot = self.stack_slot_destination(4)

        return_pc = len(self.PB) + 2
        self.generate('ASSIGN', f"#{return_pc}", ret_slot)
        self.generate('JP', sym['start_pc'])

    def declare_id(self):
        type_ = self.SS.pop()
        name = self.last_id
        if self.current_func is None:
            addr = self.get_data_addr(4)
            sym = {
                'name': name, 'type': type_, 'address': addr, 'storage': 'global',
                'decl_type': type_, 'decl_line': self.last_id_line,
                'pending_decl': True,
            }
        else:
            off = self.alloc_frame(4)
            sym = {
                'name': name, 'type': type_, 'frame_offset': off, 'storage': 'frame',
                'decl_type': type_, 'decl_line': self.last_id_line,
                'pending_decl': True,
            }
        self.symbol_table[-1][name] = sym
        self.SS.append(sym)

    def declare_array(self):
        size = int(self.last_num)
        sym = self.SS.pop()
        if sym.get('decl_type') == 'void':
            self.semantic_error(
                sym.get('decl_line', self.current_line),
                f"Illegal type of void for '{sym.get('name', '')}'."
            )
        sym['type'] = 'array'
        sym['size'] = size
        sym['pending_decl'] = False
        if sym.get('storage') == 'frame':
            self.current_func['next_offset'] += max(0, size - 1) * 4
        else:
            self.get_data_addr(max(0, size - 1) * 4)
        self.SS.append(sym)

    def declare_assign(self):
        val = self.SS.pop()
        sym = self.SS.pop()
        invalid_void = sym.get('decl_type') == 'void'
        if invalid_void:
            self.semantic_error(
                sym.get('decl_line', self.current_line),
                f"Illegal type of void for '{sym.get('name', '')}'."
            )
        sym['pending_decl'] = False
        rhs = self.sem_pop()
        lhs_type = self.semantic_type(sym)
        rhs_type = rhs.get('type', 'unknown')
        if (not invalid_void and lhs_type not in ('unknown', 'func') and
                rhs_type != 'unknown' and lhs_type != rhs_type):
            self.semantic_error(
                sym.get('decl_line', self.current_line),
                f"Type mismatch in operands, Got {lhs_type} instead of {rhs_type}."
            )
        src = self.read_operand(val)
        dst = self.write_operand(self.value_desc_for_sym(sym))
        self.generate('ASSIGN', src, dst)

    def declare_func(self):
        sym = self.SS.pop()


        if sym.get('storage') == 'global' and self.data_address >= sym.get('address', 0) + 4:
            self.data_address -= 4
        sym['ret_type'] = sym['type']
        sym['type'] = 'func'
        sym['storage'] = 'func'
        sym['params'] = []
        sym['pending_decl'] = False

        skip_hole = len(self.PB)
        self.PB.append(None)
        self.SS.append(skip_hole)

        sym['start_pc'] = len(self.PB)
        sym['next_offset'] = 12


        old_fp_ptr = self.scratch()
        self.generate('ADD', self.SP, '#8', old_fp_ptr)
        self.generate('ASSIGN', self.FP, f"@{old_fp_ptr}")
        self.generate('ASSIGN', self.SP, self.FP)
        sym['frame_size_hole'] = len(self.PB)
        self.PB.append(['ADD', self.SP, '#0', self.SP])

        self.symbol_table.append({})
        self.current_func = sym
        self.labels = {}
        self.unresolved_gotos = {}

    def end_func(self):
        func = self.current_func


        self.emit_function_epilogue()
        frame_size = max(12, func['next_offset'])
        self.PB[func['frame_size_hole']] = ['ADD', self.SP, f"#{frame_size}", self.SP]

        self.symbol_table.pop()
        skip_hole = self.SS.pop()
        self.PB[skip_hole] = ['JP', len(self.PB), '', '']
        self.current_func = None
        self.sem_stack.clear()

    def declare_param(self):
        type_ = self.SS.pop()
        name = self.last_id
        off = self.alloc_frame(4)
        sym = {
            'name': name, 'type': type_, 'frame_offset': off, 'storage': 'frame',
            'decl_type': type_, 'decl_line': self.last_id_line,
            'pending_decl': True,
        }
        self.symbol_table[-1][name] = sym
        self.current_func['params'].append(sym)
        self.SS.append(sym)


    def pid(self):
        sym = self.lookup(self.last_id)
        if sym:
            self.SS.append(self.value_desc_for_sym(sym))
            st = self.semantic_type(sym)
            self.sem_stack.append(self.sem_value(st, self.last_id_line, sym))
        else:
            self.SS.append(self.imm(0))
            self.semantic_error(self.last_id_line, f"'{self.last_id}' is not defined.")
            self.sem_stack.append(self.sem_value('unknown', self.last_id_line, None))

    def pnum(self):
        self.SS.append(self.imm(self.last_num))
        self.sem_stack.append(self.sem_value('int', self.last_num_line))

    def assign(self):
        val = self.SS.pop()
        addr = self.SS.pop()
        rhs = self.sem_pop()
        lhs = self.sem_pop()
        lhs_type = lhs.get('type', 'unknown')
        rhs_type = rhs.get('type', 'unknown')
        if lhs_type != 'unknown' and rhs_type != 'unknown' and lhs_type != rhs_type:
            self.semantic_error(
                lhs.get('line', self.current_line),
                f"Type mismatch in operands, Got {lhs_type} instead of {rhs_type}."
            )
        result_type = rhs_type if rhs_type != 'unknown' else lhs_type
        self.sem_stack.append(self.sem_value(result_type, lhs.get('line', self.current_line)))

        src = self.read_operand(val)
        dst = self.write_operand(addr)
        self.generate('ASSIGN', src, dst)
        self.SS.append(val)

    def array_elem(self):
        idx = self.SS.pop()
        base = self.SS.pop()
        sem_idx = self.sem_pop()
        sem_base = self.sem_pop()
        base_type = sem_base.get('type', 'unknown')
        idx_type = sem_idx.get('type', 'unknown')
        if base_type not in ('array', 'unknown'):
            self.semantic_error(
                sem_base.get('line', self.current_line),
                f"Type mismatch in operands, Got {base_type} instead of array."
            )
        elif idx_type not in ('int', 'unknown'):
            self.semantic_error(
                sem_idx.get('line', self.current_line),
                f"Type mismatch in operands, Got {idx_type} instead of int."
            )
        self.sem_stack.append(self.sem_value('int', sem_base.get('line', self.current_line)))
        self.SS.append(('elem', base, idx))

    def binary(self, semantic_op=False):
        right = self.SS.pop()
        op = self.SS.pop()
        left = self.SS.pop()
        sem_right = self.sem_pop()
        sem_left = self.sem_pop()
        if self.check_int_operand(sem_left):
            self.check_int_operand(sem_right)
        self.sem_stack.append(self.sem_value('int', sem_left.get('line', self.current_line)))
        left_op = self.read_operand(left)
        right_op = self.read_operand(right)
        result = self.new_temp_desc()
        dst = self.write_operand(result)
        self.generate(op, left_op, right_op, dst)
        self.SS.append(result)

    def relop(self): self.binary(True)
    def addsub(self): self.binary()
    def multdiv(self): self.binary()

    def neg(self):
        val = self.SS.pop()
        sem_val = self.sem_pop()
        self.check_int_operand(sem_val)
        self.sem_stack.append(self.sem_value('int', sem_val.get('line', self.current_line)))
        src = self.read_operand(val)
        result = self.new_temp_desc()
        dst = self.write_operand(result)
        self.generate('SUB', '#0', src, dst)
        self.SS.append(result)


    def save(self):
        cond = self.SS.pop()
        cond_op = self.read_operand(cond)
        self.SS.append(cond_op)
        self.SS.append(len(self.PB))
        self.PB.append(None)
        self.sem_pop()

    def switch_start(self):
        switch_val = self.SS.pop()
        self.sem_pop()
        self.switch_stack.append({'val': switch_val, 'fall_throughs': []})
        self.break_stack.append([])

    def case_test(self):
        const = self.SS.pop()
        self.sem_pop()
        info = self.switch_stack[-1]
        left = self.read_operand(info['val'])
        right = self.read_operand(const)
        result = self.scratch()
        self.generate('EQ', left, right, result)
        jpf_hole = len(self.PB)
        self.PB.append(None)

        for hole in info['fall_throughs']:
            self.PB[hole] = ['JP', len(self.PB), '', '']
        info['fall_throughs'] = []

        self.SS.append(jpf_hole)
        self.SS.append(result)


    def return_void(self):
        self.emit_function_epilogue()

    def return_val(self):
        val = self.SS.pop()
        self.sem_pop()
        src = self.read_operand(val)
        self.generate('ASSIGN', src, f"@{self.FP}")
        self.emit_function_epilogue()

    def start_call(self):
        self.SS.append('CALL_MARKER')
        self.sem_stack.append('CALL_MARKER')

    def call(self):

        sem_args = []
        while self.sem_stack and self.sem_stack[-1] != 'CALL_MARKER':
            sem_args.insert(0, self.sem_stack.pop())
        if self.sem_stack and self.sem_stack[-1] == 'CALL_MARKER':
            self.sem_stack.pop()
        sem_func = self.sem_pop()
        func_sem_sym = sem_func.get('sym') if isinstance(sem_func, dict) else None
        result_type = 'unknown'
        if func_sem_sym and func_sem_sym.get('type') == 'func':
            if func_sem_sym.get('is_builtin'):
                param_types = list(func_sem_sym.get('sem_param_types', ['int']))
            else:
                param_types = [
                    'array' if p.get('type') in ('array', 'array_ptr') else p.get('type', 'unknown')
                    for p in func_sem_sym.get('params', [])
                ]
            call_line = sem_func.get('line', self.current_line)
            if len(sem_args) != len(param_types):
                self.semantic_error(call_line, f"Mismatch in numbers of arguments of '{func_sem_sym.get('name', '')}'.")
            else:
                for i, (arg, expected_type) in enumerate(zip(sem_args, param_types), 1):
                    actual_type = arg.get('type', 'unknown')
                    if actual_type != 'unknown' and expected_type != 'unknown' and actual_type != expected_type:
                        self.semantic_error(
                            call_line,
                            f"Mismatch in type of argument {i} of '{func_sem_sym.get('name', '')}'. Expected '{expected_type}' but got '{actual_type}' instead."
                        )
                        break
            result_type = func_sem_sym.get('ret_type', 'void')
        elif isinstance(sem_func, dict) and sem_func.get('type') == 'unknown':
            result_type = 'unknown'
        self.sem_stack.append(self.sem_value(result_type, sem_func.get('line', self.current_line) if isinstance(sem_func, dict) else self.current_line))

        args = []
        while self.SS and self.SS[-1] != 'CALL_MARKER':
            args.insert(0, self.SS.pop())
        if self.SS and self.SS[-1] == 'CALL_MARKER':
            self.SS.pop()
        func_desc = self.SS.pop() if self.SS else None
        sym = func_desc[1] if self._is_desc(func_desc, 'func') else None

        if not sym:
            self.SS.append(self.imm(0))
            return
        if sym.get('is_builtin'):
            arg = self.read_operand(args[0]) if args else '#0'
            self.generate('PRINT', arg)
            self.SS.append(self.imm(0))
            return


        for i, arg in enumerate(args):
            if i >= len(sym.get('params', [])):
                break
            param = sym['params'][i]
            dst = self.stack_slot_destination(param['frame_offset'])
            if param.get('type') == 'array_ptr':
                src = self.array_base_operand(arg)
            else:
                src = self.read_operand(arg)
            self.generate('ASSIGN', src, dst)

        ret_slot = self.stack_slot_destination(4)
        return_pc = len(self.PB) + 2
        self.generate('ASSIGN', f"#{return_pc}", ret_slot)
        self.generate('JP', sym['start_pc'])

        if sym.get('ret_type') == 'void':
            self.SS.append(self.imm(0))
        else:
            result = self.new_temp_desc()
            dst = self.write_operand(result)


            self.generate('ASSIGN', f"@{self.SP}", dst)
            self.SS.append(result)


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
    def __init__(self, scanner, recursive_mode=False):
        self.scanner = scanner
        self.first = compute_first_sets()
        self.follow = compute_follow_sets(self.first)
        self.table = create_parsing_table(self.first, self.follow)
        self.errors = []
        self.cg = RecursiveCodeGen() if recursive_mode else CodeGen()

    def get_grammar_symbol(self, token):
        _, t_type, lexeme = token
        if t_type == "EOF": return "$"
        if t_type == "ID": return "ID"
        if t_type == "NUM": return "NUM"
        return lexeme

    def parse(self):
        root = ParseNode("Program")
        eof_node = ParseNode("$")
        decl_node = ParseNode("Program")

        root.add_child(decl_node)
        root.add_child(eof_node)

        stack = [eof_node, decl_node]
        token = self.scanner.get_next_token()

        while stack:
            top = stack[-1]
            lookahead_sym = self.get_grammar_symbol(token)

            if is_action(top.symbol):
                action_name = top.symbol[1:]


                method = getattr(self.cg, action_name, None)
                if method is None:
                    method = getattr(self.cg, action_name + "_", None)
                if method is not None:
                    method()
                stack.pop()
                continue

            if top.symbol in TERMINALS or top.symbol == "$":
                if top.symbol == lookahead_sym:
                    self.cg.current_line = token[0]
                    if top.symbol == 'ID':
                        self.cg.last_id = token[2]
                        self.cg.last_id_line = token[0]
                    elif top.symbol == 'NUM':
                        self.cg.last_num = token[2]
                        self.cg.last_num_line = token[0]

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
                    children = []
                    for sym in rule:
                        if sym == "EPSILON":
                            child = ParseNode("epsilon")
                            top.add_child(child)
                        else:
                            child = ParseNode(sym)
                            children.append(child)
                            if not is_action(sym):
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


def contains_direct_recursion(text):


    sc = Scanner(text)
    tokens = []
    while True:
        tok = sc.get_next_token()
        if tok[1] == 'EOF':
            break
        tokens.append((tok[1], tok[2]))

    i = 0
    depth = 0
    while i + 2 < len(tokens):
        typ, lex = tokens[i]
        if lex == '{':
            depth += 1
            i += 1
            continue
        if lex == '}':
            depth = max(0, depth - 1)
            i += 1
            continue
        if depth == 0 and lex in ('int', 'void') and tokens[i + 1][0] == 'ID' and tokens[i + 2][1] == '(':
            name = tokens[i + 1][1]

            j = i + 2
            par = 0
            while j < len(tokens):
                if tokens[j][1] == '(':
                    par += 1
                elif tokens[j][1] == ')':
                    par -= 1
                    if par == 0:
                        j += 1
                        break
                j += 1
            while j < len(tokens) and tokens[j][1] != '{':
                j += 1
            if j >= len(tokens):
                i += 1
                continue
            body_start = j + 1
            braces = 1
            j += 1
            while j < len(tokens) and braces:
                if tokens[j][1] == '{':
                    braces += 1
                elif tokens[j][1] == '}':
                    braces -= 1
                    if braces == 0:
                        break
                if braces > 0 and tokens[j][0] == 'ID' and tokens[j][1] == name:
                    if j + 1 < len(tokens) and tokens[j + 1][1] == '(':
                        return True
                j += 1
            i = j + 1
            continue
        i += 1
    return False

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, 'input.txt')

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        text = ''

    recursive_mode = True
    scanner = Scanner(text)
    parser = Parser(scanner, recursive_mode=recursive_mode)

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

    with open(os.path.join(base_dir, 'semantic_errors.txt'), 'w', encoding='utf-8') as f:
        if parser.cg.semantic_errors:
            for err in parser.cg.semantic_errors:
                f.write(err + "\n")
        else:
            f.write("The input program is semantically correct.\n")

    with open(os.path.join(base_dir, 'output.txt'), 'w', encoding='utf-8') as f:
        if parser.errors or parser.cg.semantic_errors:
            f.write("The output code has not been generated.\n")
        else:
            for i, inst in enumerate(parser.cg.PB):
                if inst is None:
                    continue
                op = inst[0]
                arg1 = inst[1] if inst[1] is not None and inst[1] != "" else ""
                arg2 = inst[2] if inst[2] is not None and inst[2] != "" else ""
                arg3 = inst[3] if inst[3] is not None and inst[3] != "" else ""
                f.write(f"{i}\t({op}, {arg1}, {arg2}, {arg3})\n")

if __name__ == '__main__':
    main()
