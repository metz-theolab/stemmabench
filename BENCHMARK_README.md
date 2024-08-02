# How to run a benchmark with the stemmabench package

> [NOTE]
> The following commands must all be run from the root of the stemmabench project. 
> You must also have a version of python 3.8 or above to ensure that the package functions correctly.

## Installing stemmabench

- Download the github repository.

- Create a new python virtual environment by running the following command: `python -m venv .venv`.

- Activate your virtual environment by running the following command:
    + For windows: `.venv\Scripts\activate`
    + For mac or linux: `.venv/bin/activate`

- Install the invoke package with the following command: 
    + For windows: `.venv\Scripts\pip3.exe install invoke`
    + For mac or linux: `pip install invoke` 

- Run the following command to fully install the stemmabench package: `invoke install`.

- Run the following command to compile the code implemented in C on your machine:
    + For windows: `src\stemmabench\algorithms\compile.bat`
    + For mac or linux: `bash src/stemmabench/algorithms/compile.sh`

> [Warning]
> If any errors occur during compilation:
> - Check that you compiler has the necessary libraries installed. The necessary C libraries are specified at the top of the `src\stemmabench\algorithms\rhm.c` file.
> - On windows you may need to specify the path to the folder containing the lib files or the header files. If so append the following parameter to the end of the compilation commands in the `src\stemmabench\algorithms\compile.bat` file:
>       + For lib folder: `-L<path to compiler library file folder>`
>       + For header files:`-I<path to compiler header file folder>`

## Runing the benchmarking

> [NOTE]
> The automation of benchmarking is not yet implemented for windows as at present only the bash scripts have been written.

To initiate a full automatic benchmarking from a single original text using all the algorithms implemented in the stemmabench package run the command with the desiered parameters: 
- `scripts/run_benchmark.sh <mispell rate> <synonim rate> <omit rate> <duplicate rate> <n duplicate> <specific rate> <benchmark name> <path to text> <depth> <width> <percent missing>`.

> [NOTE]
> For more detailed information on the parameters taken by the `run_benchmark.sh` script read the Variant configuration section in the documentation.

The `run_benchmark.sh` script takes the bellow parameters in the specified order:
- 1.`mispell rate`: Represents the general probability of a letter being modified. (between 0 and 1)
- 2.`synonim rate`: The rate at which words are replaced with synonyms. (between 0 and 1)
- 3.`omit rate`: The rate at which words are omitted. (between 0 and 1)
- 4.`duplicate rate`: The rate at which words are duplicated. (between 0 and 1)
- 5.`n duplicate`: The number of times a word is repeated when word repetition occurs.
- 6.`specific rate`: A string containing a python dictionary which references the misspell rates of specific letters.
Example: "{"a" : {"o" : 0.5, "q" : 0.3}, "d": {"o" : 0.4}}" or "None". 
- 7.`benchmark name`: The name given to the oututed folders and files to identify this specific tradition generation.
- 8.`path to text`: The path to the text which will be the root of the textual tradition.
- 9.`depth`: The depth of the textual tradition generated.
- 10.`width`: The maximum number of children generated per text.
- 11.`percent missing`: The percent of texts that will be randomly selected as missing texts in the generated textual tradition. (supports from 0 to 10)