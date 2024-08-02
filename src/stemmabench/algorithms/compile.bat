rem-LC:\msys64\ucrt64\lib
REM Compile rhm.c to rhm.dll from the root of stemmabench 
gcc -o src\stemmabench\algorithms\rhm.dll -shared src\stemmabench\algorithms\rhm.c -lz -static 