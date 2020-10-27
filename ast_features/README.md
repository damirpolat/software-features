In this directory, you can find the needed information to extract static AST features from your source code. It consists of two steps.

## Compilation

First, you want to extract the Abstract Syntax Tree of your algorithm as constructed by the compiler Clang (we used version 9).
To do so, you can simply dump the ast in a file when compiling it. A typical make file would then look like this:

```
	CC	= 	clang++

.c:
		$(CC) -o $@ $< -Xclang -ast-dump -fsyntax-only -fno-color-diagnostics > $<.ast
		$(CC) -o $@ $< 
```

This would create for each file `source.c` an ast file `source.c.ast`

## Feature extraction

The `compure_features.py` script computes features for a set of ast dump files. It requires the libraries Scipy and NetworkX.
To use it, call:
```
	python3 ./compute_features.py <list of files separated by space>
```
The features value for the specified list of files will be printed in your terminal.