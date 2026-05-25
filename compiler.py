import os

KEYWORDS = ["break", "else", "for", "if", "int", "return", "void", "goto", "switch", "case", "default", "while"]
KEYWORD_SET = set(KEYWORDS)
SINGLE_SYMBOLS = set([';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '/', '=', '<'])
WHITESPACE = set([' ', '\n', '\r', '\t', '\v', '\f'])


class Scanner:
    def __init__(self, text):
        self.text = text
        self.length = len(text)
        self.index = 0
        self.line = 1
        self.tokens = {}
        self.errors = []
        self.symbols = list(KEYWORDS)
        self.symbol_set = set(KEYWORDS)

    def current_char(self):
        if self.index >= self.length:
            return None
        return self.text[self.index]

    def next_char(self):
        if self.index + 1 >= self.length:
            return None
        return self.text[self.index + 1]

    def add_token(self, line, token_type, lexeme):
        if line not in self.tokens:
            self.tokens[line] = []
        self.tokens[line].append("({0}, {1})".format(token_type, lexeme))

    def add_error(self, line, lexeme, message):
        self.errors.append((line, lexeme, message))

    def add_symbol(self, lexeme):
        if lexeme not in self.symbol_set:
            self.symbol_set.add(lexeme)
            self.symbols.append(lexeme)

    def is_letter(self, ch):
        return ch is not None and (('a' <= ch <= 'z') or ('A' <= ch <= 'Z'))

    def is_digit(self, ch):
        return ch is not None and ('0' <= ch <= '9')

    def is_identifier_char(self, ch):
        return self.is_letter(ch) or self.is_digit(ch) or ch == '_'

    def is_token_delimiter(self, ch):
        if ch is None:
            return True
        return ch in WHITESPACE or ch in SINGLE_SYMBOLS

    def unclosed_comment_lexeme(self, lexeme):
        if len(lexeme) > 9:
            return lexeme[:9] + '...'
        return lexeme

    def skip_whitespace(self):
        ch = self.current_char()
        if ch == '\n':
            self.line += 1
        self.index += 1

    def scan_identifier_or_keyword(self):
        start = self.index
        start_line = self.line

        while self.index < self.length and self.is_identifier_char(self.text[self.index]):
            self.index += 1

        if not self.is_token_delimiter(self.current_char()):
            while self.index < self.length and not self.is_token_delimiter(self.text[self.index]):
                self.index += 1
            self.add_error(start_line, self.text[start:self.index], "Invalid input")
            return

        lexeme = self.text[start:self.index]

        if lexeme in KEYWORD_SET:
            self.add_token(start_line, "KEYWORD", lexeme)
        else:
            self.add_symbol(lexeme)
            self.add_token(start_line, "ID", lexeme)

    def scan_number(self):
        start = self.index
        start_line = self.line

        while self.index < self.length and self.is_digit(self.text[self.index]):
            self.index += 1

        invalid = False

        if self.index - start > 1 and self.text[start] == '0':
            invalid = True

        if self.current_char() is not None and self.is_identifier_char(self.current_char()):
            invalid = True

        if invalid:
            while self.index < self.length and self.is_identifier_char(self.text[self.index]):
                self.index += 1
            self.add_error(start_line, self.text[start:self.index], "Invalid number")
            return

        self.add_token(start_line, "NUM", self.text[start:self.index])

    def scan_comment_or_slash(self):
        start_line = self.line

        if self.next_char() == '/':
            self.index += 2
            while self.index < self.length and self.text[self.index] != '\n':
                self.index += 1
            return

        if self.next_char() == '*':
            start = self.index
            self.index += 2

            while self.index < self.length:
                if self.text[self.index] == '*' and self.index + 1 < self.length and self.text[self.index + 1] == '/':
                    self.index += 2
                    return

                if self.text[self.index] == '\n':
                    self.line += 1

                self.index += 1

            self.add_error(start_line, self.unclosed_comment_lexeme(self.text[start:self.index]), "Unclosed comment")
            return

        self.add_token(start_line, "SYMBOL", '/')
        self.index += 1

    def scan_equal(self):
        start_line = self.line

        if self.next_char() == '=':
            self.add_token(start_line, "SYMBOL", '==')
            self.index += 2
        else:
            self.add_token(start_line, "SYMBOL", '=')
            self.index += 1

    def scan(self):
        while self.index < self.length:
            ch = self.current_char()

            if ch in WHITESPACE:
                self.skip_whitespace()

            elif ch == '/':
                self.scan_comment_or_slash()

            elif ch == '*' and self.next_char() == '/':
                self.add_error(self.line, '*/', "Unmatched comment")
                self.index += 2

            elif self.is_letter(ch):
                self.scan_identifier_or_keyword()

            elif self.is_digit(ch):
                self.scan_number()

            elif ch == '=':
                self.scan_equal()

            elif ch in SINGLE_SYMBOLS:
                self.add_token(self.line, "SYMBOL", ch)
                self.index += 1

            else:
                self.add_error(self.line, ch, "Invalid input")
                self.index += 1


def write_tokens(path, tokens):
    with open(path, 'w', encoding='utf-8') as f:
        for line in sorted(tokens.keys()):
            f.write("{0}.\t{1} \n".format(line, ' '.join(tokens[line])))


def write_errors(path, errors):
    with open(path, 'w', encoding='utf-8') as f:
        if not errors:
            f.write("There is no lexical error.\n")
        else:
            for line, lexeme, message in errors:
                f.write("{0}.\t({1}, {2})\n".format(line, lexeme, message))


def write_symbol_table(path, symbols):
    with open(path, 'w', encoding='utf-8') as f:
        for i, symbol in enumerate(symbols, 1):
            f.write("{0}.\t{1}\n".format(i, symbol))


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, 'input.txt')

    try:
        with open(input_path, 'r', encoding='utf-8', newline='') as f:
            text = f.read()
    except FileNotFoundError:
        text = ''

    scanner = Scanner(text)
    scanner.scan()

    write_tokens(os.path.join(base_dir, 'tokens.txt'), scanner.tokens)
    write_errors(os.path.join(base_dir, 'lexical_errors.txt'), scanner.errors)
    write_symbol_table(os.path.join(base_dir, 'symbol_table.txt'), scanner.symbols)


if __name__ == '__main__':
    main()
