#!/bin/bash

gcc -o src/stemmabench/algorithms/rhm.o -shared src/stemmabench/algorithms/rhm.c -lz -fPIC