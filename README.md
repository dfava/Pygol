# Pygol

Game of Life in Python.

> **Implements:**
> Eight neighbor rule on a square grid
> Six neighbor rule on a hex grid (http://www.mathrecreation.com/2012/10/hex-life.html)
> Twelve neighbor rule on a hex grid (http://www.well.com/~dgb/hexrules.html)

#### Run

> python3 gol.py

Example runs:

Use -8 for a square board and eight neighbor rule and -12 for a hex board with 12 neighbor rule.  Otherwise, defaults to hex board and 6 neighbor rule.

> python3 gol.py -f oscillators.txt -8 -nc
> python3 gol.py -f hex6_oscillators.txt -nc
> python3 gol.py -12 -nc

Use -nc to see a "movie" of the output.

Use -f for reading a board from a file.  Otherwise, a 100x100 board is created randomly with probability 0.5 of a cell being alive.  Use -size and -i to adjust the board size and probability respectively.

Other command line options are -g and -p to specify the number of generations to simulate (defaults to 10) and -p to specify that every nth generation should be printed (defaults to 1).

#### Test

Minimal testing using small oscillators and gliders and watching standard output.