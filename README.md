# timeseries

The aim of the project is to analyze the options to assess vertical
forest strucutre from ALS and GEDI LiDAR data.

It provides the following shell script: `gedisens`.
For usage information, type `gedisens --help`.


## Prerequisites

You need a working Python environment, and `pip` installed.


## Installation
1. Create virtual environment with:

```bash
python3 -m venv env.
```

2. Activate the virtual environment with:

```bash
source env/bin/activate.
```

3. For some reason one has to do:

```bash
pyton setup.py bdist_wheel.
```

4. Use the following command in the base directory to install:

```bash
python -m pip install .
```

For an editable ("developer mode") installation, use the following
instead:

```bash
python -m pip install -e .
```

## How to run it

In order to run it an example is given below:

```bash
timeseries -csv <filename> -anom -linfit -dep_var <var name> -ind_var <var name> -anom_plot 

```
