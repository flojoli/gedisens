# gedisens

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

3. Use the following command in the base directory to install:

```bash
python -m pip install .
```

For an editable ("developer mode") installation, use the following
instead:

```bash
python -m pip install -e .
```

## How to run it

In order to run it examples are given below:
Correlation plot
```bash
gedisens -data-file <filepath+name>  -correlation-plot -x-var alsFHD -y-var gediFHDcal -out-dir <outpath>
```

Structure plot
```bash
gedisens -data-file <filepath+name> -structure-plot -dz 1 -shot-number 35070600200401943 -add-info fhd -out-dir <outpath>
```

Calculate layers
```bash
gedisens -data-file <filepath+name> -layers -out-dir <outpath>
```

Calculate foliage height diversity
```bash
gedisens -data-file <filepath+name> -fhd -out-dir <outpath>
```