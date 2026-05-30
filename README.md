# Cminus Compiler

A simple compiler project for the Compiler Design course.

This repository currently contains the implementation of **Phase 1: Scanner / Lexical Analyzer** for a simplified version of the C programming language called **C-minus**.

## Current Status

* [x] Phase 1: Scanner / Lexical Analyzer
* [ ] Phase 2: Parser / Syntax Analyzer
* [ ] Phase 3: Semantic Analyzer
* [ ] Phase 4: Intermediate Code Generation

## Phase 1: Scanner

The scanner reads a C-minus source program from:

```text
input.txt
```

and generates the following output files:

```text
tokens.txt
lexical_errors.txt
symbol_table.txt
```

## Recognized Token Types

The scanner recognizes the following token types:

* `KEYWORD`
* `ID`
* `NUM`
* `SYMBOL`

Comments and whitespace are skipped and are not written to the output token file.

## Supported Keywords

```text
break else for if int return void goto switch case default while
```

## Lexical Error Handling

The scanner reports lexical errors in `lexical_errors.txt`.

Handled lexical errors include:

* Invalid input characters
* Invalid numbers
* Unmatched comments
* Unclosed comments

If there is no lexical error, `lexical_errors.txt` contains:

```text
There is no lexical error.
```

## How to Run

Place `input.txt` in the same directory as `compiler.py`, then run:

```bash
python compiler.py
```

After execution, the following files will be generated:

```text
tokens.txt
lexical_errors.txt
symbol_table.txt
```

## Project Structure

```text
cminus-compiler/
├── compiler.py
├── README.md
└── .gitignore
```

## Notes

* The project is implemented in Python.
* No external packages are required.
* The scanner uses only the Python standard library.
* The main executable file is `compiler.py`.
* The implementation is intended to be compatible with Python 3.8+.

```
```
