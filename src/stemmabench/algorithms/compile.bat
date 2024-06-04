REM Compile rhm.c to rhm.dll
gcc -o rhm.dll -shared rhm.c -LC:\msys64\ucrt64\lib -lz -static