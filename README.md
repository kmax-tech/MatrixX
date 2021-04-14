#MatrixX - A Solver for Argumentation Frameworks

Welcome to the MatrixX. This is a solver for Argumentation Frameworks (AFs), which supports stable and complete semantics.

##Overview

Matrixx is written in Python and consists of the following files:

matrixx - a bash script for executing the Python files

st_matrixx.py - the solver for stable semantics

cp_matrixx.py - the solver for complete semantics

tgf_load.py - for reading and preprocessing of .tgf files

apx_load.py - for reading and preprocessing of .apx files


##Install

- A version of Python 3.* is required; the solver was tested with Python 3.7 and Python 3.9, other versions might work as well.

- The "matrixx" file calls the command "python3"; therefore this command should run the installed Python interpreter in the used shell.

- In case the command for Python is not named "python3", the variable "python_command" can be manually edited in the "matrixx" file.

- The used Python modules are "re","time","pickle","argparse" and "functools". They are part of the Standard Library and should be included in any Python version.

- In order order to use the solver, just run "matrixx" as specified below.


##Usage:
For an overview of the supported tasks run:

```./matrixx --problems```

The supported problems are:

[CE-ST,SE-ST,DC-ST,DS-ST,CE-CO,SE-CO,DC-CO,DS-CO]

For supported formats run:


```./matrixx --formats```

The solver supports apx and tgf files.

The usage of the solver is according to the ICCMA 2021 Competiton Rules.

####Options:
- -p problem
- -f filename -- the name of the file
- -fo fileformat -- apx and tgf supported
- -a addtional_parameter -- a parameter for the SE-\* and CE-\* tasks.  

```./matrixx -p problem -f filename -fo fileformat [-a additional_parameter]```

- The ```-fo``` option can be omitted if the filename ends with ".apx" or".tgf"; in this case the fileformat is determined automatically.
- As an additional problem one can use "-p DEBUG"; in this case all interpretations are printed.


###Contact:

Author: Maximilian Heinrich

E-Mail: mheinrich@informatik.uni-leipzig.de