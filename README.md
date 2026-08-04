# C-minus Compiler

A one-pass compiler for **C-minus**, developed as part of the Compiler Design course.

C-minus is a simplified version of the C programming language. The project is developed incrementally, and each phase extends the implementation produced in the previous phase.

## Current Status

- [x] Phase 1: Scanner / Lexical Analyzer
- [x] Phase 2: LL(1) Parser / Syntax Analyzer
- [ ] Phase 3: Semantic Analysis and Intermediate Code Generation

## Implemented Features

### Phase 1: Scanner

The scanner reads a C-minus source program character by character and recognizes the following token types:

- `KEYWORD`
- `ID`
- `NUM`
- `SYMBOL`

Supported keywords:

```text
break else if int return void while goto switch case default
```

The standalone Phase 1 implementation generated:

```text
tokens.txt
lexical_errors.txt
symbol_table.txt
```

Phase 1 is preserved in the Git tag:

```text
phase-1
```

### Phase 2: LL(1) Parser

The current version integrates the scanner with a predictive top-down **LL(1) parser**.

The parser:

- Receives tokens directly from the scanner
- Works without backtracking
- Computes First and Follow sets
- Constructs an LL(1) parsing table
- Generates a parse tree
- Recovers from syntax errors using Panic Mode
- Processes the input in a single-pass pipeline

## Input

The compiler reads the source program from:

```text
input.txt
```

The file must be located in the same directory as `compiler.py`.

## Output

Running the Phase 2 compiler generates:

```text
parse_tree.txt
syntax_errors.txt
```

### `parse_tree.txt`

Contains the parse tree generated for the input C-minus program.

### `syntax_errors.txt`

Contains syntax errors found during parsing.

If no syntax error is detected, the file contains:

```text
There is no syntax error.
```

## How to Run

Make sure `input.txt` is located next to `compiler.py`, then run:

```bash
python3 compiler.py
```

On Windows, the following command may also be used:

```bash
python compiler.py
```

## Project Structure

```text
cminus-compiler/
├── compiler.py
├── README.md
└── .gitignore
```

The following files are generated during execution and are not required to be committed:

```text
input.txt
parse_tree.txt
syntax_errors.txt
tokens.txt
lexical_errors.txt
symbol_table.txt
```

## Version History

- `phase-1`: Scanner / Lexical Analyzer
- `phase-2`: Integrated Scanner and LL(1) Parser
- `main`: Latest stable version of the compiler

## Environment

The project is intended to run with:

```text
Python 3.9+
Ubuntu Linux
```

The current implementation does not require external Python packages.

## Contributors

- **Arvin** — Phase 1: Scanner / Lexical Analyzer
- **[Partner Name]** — Phase 2: LL(1) Parser / Syntax Analyzer

## Course Project

This repository contains coursework developed for educational purposes as part of the Compiler Design course.
