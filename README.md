AlgoHW
======

This repository collects algorithm implementations and experiments. Two main modules are included:

- Mcmf: C implementation of Min-Cost Max-Flow (successive shortest path with SPFA). Includes Python reference (`mcmf_ref.py`), correctness tests, performance experiments, and documentation (`Mcmf/README.md`).
- kmp: Python implementation of the KMP string-matching algorithm with complexity analysis, plots, and tests. See `kmp/README.md` for details.

Quick start
-----------

- Build/run Mcmf:
	- `cd Mcmf && make` (or `gcc -std=c11 -O2 mcmf.c -o mcmf`)
	- Run correctness tests: `./run_correctness_tests.sh`
- KMP tests:
	- `cd kmp && python test_complexity.py`

Docs
----

- Mcmf: `Mcmf/README.md` .
- KMP: `kmp/README.md` (with generated performance plots in `kmp/`).

Notes
-----

- All code is self-contained; no external dependencies beyond standard C toolchain and Python 3 with matplotlib/numpy for KMP plots.
