# Generated outputs

StemmaBench generates two outputs within the `output_folder` specified in the command line:

1. A file `edge.txt` which represents the tree as a set of node.
2. A set of file `*.txt` which contain the copied text and which number represent their hierarchy in the tree. `0` is the first text, then `0_0` and `0_1` are its descendants, then `0_0_0` and `0_0_1` are the descendants of `0_0` in a bifid tree fashion, etc.

Furthermore, if the `rate` parameter of the `missing_manuscripts` option is greater than zero, an additional folder called `missing_tradition` is created within the `output_folder` specified in the command line. This folder includes:

- A file named `edge_missing.txt` containing the edges connecting the non-missing manuscripts still available.
- A collection of `*.txt` files with the remaining manuscripts in the tradition. These files exclude any manuscripts that were deleted during the process.
