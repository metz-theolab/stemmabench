# Generated outputs

StemmaBench generates two outputs within the `output_folder` specified in the command line:

- A file `edge.txt` which represents the tree as a set of node.
- A set of file `*.txt` which contain the copied text and which number represent their hierarchy in the tree. `0` is the first text, then `0_0` and `0_1` are its descendants, then `0_0_0` and `0_0_1` are the descendants of `0_0` in a bifid tree fashion, etc.