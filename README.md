# makeprime-python
A python port of Fudmotins prime generator.

## Overview
This tool creates a prime number for a given number of digits.  It is a python port of the original [C++ version](https://github.com/Fudmottin/makeprime).

## Usage

```
python3 makeprime.py <number of digits> [options]
```

Number of digits must be greater than 3.

Options:
- `--twin`: Find consecutive prime numbers
- `--random`: Use a random starting point and stride
- `--multi`: Use multicore search

### Example
```
python3 makeprime.py 100 --twin
```
