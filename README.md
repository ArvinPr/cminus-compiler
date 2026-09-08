# Cminus Compiler

A compiler implementation project for the Compiler Design course.

This repository contains the implementation of a compiler for a simplified version of the C language called **C-minus**.

The compiler is implemented in Python and includes the following phases:

- Lexical Analysis (Scanner)
- Syntax Analysis (Parser)
- Semantic Analysis
- Intermediate Code Generation

---

## Project Status

- [x] Phase 1: Scanner / Lexical Analyzer
- [x] Phase 2: Parser / Syntax Analyzer
- [x] Phase 3: Code Generation

### Phase 3 Bonus Features

- [x] Semantic Analyzer
- [x] Recursive Function Support

---

# Phase 1: Scanner

The scanner reads a C-minus source program from:

```text
input.txt
```

and converts the source code into tokens.

Generated output files:

```text
tokens.txt
lexical_errors.txt
symbol_table.txt
```

## Recognized Token Types

- KEYWORD
- ID
- NUM
- SYMBOL

## Lexical Error Handling

The scanner detects:

- Invalid input characters
- Invalid numbers
- Unmatched comments
- Unclosed comments

If there is no lexical error:

```text
There is no lexical error.
```

is written to the output file.

---

# Phase 2: Parser

The parser performs syntax analysis based on the grammar of the C-minus language.

Implemented features:

- Grammar-based parsing
- FIRST and FOLLOW set calculation
- Predictive parsing table generation
- Syntax error detection

---

# Phase 3: Code Generation

The compiler generates intermediate code in the form of **Three Address Code (TAC)**.

Implemented features:

- Variable declarations
- Array handling
- Expressions
- Assignment statements
- Function declarations and calls
- Conditional statements
- Loop statements
- Return statements
- Switch statements
- Goto statements

Generated files:

```text
output.txt
semantic_errors.txt
```

---

# Bonus Features

## Semantic Analyzer

Semantic analysis is performed during parsing.

The compiler checks:

- Undefined variables and functions
- Invalid variable declarations
- Function argument count mismatch
- Function argument type mismatch
- Invalid break statements
- Type mismatch in expressions

Semantic errors are written to:

```text
semantic_errors.txt
```

If the program is semantically correct:

```text
The input program is semantically correct.
```

is written.

---

## Recursive Function Support

Recursive function calls are supported using a runtime stack mechanism.

The compiler manages:

- Function activation records
- Parameters
- Local variables
- Return addresses
- Stack frames

This allows recursive functions to maintain separate execution contexts for each function call.

---

# How to Run

Place the C-minus source code in:

```text
input.txt
```

in the same directory as:

```text
compiler.py
```

Run:

```bash
python compiler.py
```

The generated output files will be created after execution.

---

# Project Structure

```text
cminus-compiler/
│
├── compiler.py
├── README.md
└── .gitignore
```

---

# Requirements

- Python 3.8+

No external packages are required.

The project uses only Python standard libraries.

---

# Notes

- The compiler follows the C-minus language specification used in the Compiler Design course.
- The generated intermediate code is represented as Three Address Code (TAC).
- Semantic analysis and recursive function support are implemented as additional features.