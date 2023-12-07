# Welcome to StemmaBench

A powerful and easy to use Python library to generate artificial **manuscript tradition**, by simulating scribal behavior in order to benchmark stemmatology algorithms. You can simply generate a tradition, apply your stemmatology algorithms on the generated texts, and assess how well your tree was reconstructed compared to the ground truth.

## Installing

Stemmabench is available on PyPi:

```pip install stemmabench```

You can also clone the source code if you want access to the demonstration folder, then install it using in the root folder:

```invoke install```

## Using StemmaBench

StemmaBench requires two items:

- The initial text to be copied by the artificial scribe.

- A YAML configuration file parametrizing the variants. For more information regarding the configuration file, go to [the variant description page](variants.md).

Once you have your wanted text and wanted configuration file, you can run the command:

```shell
stemmabench generate-tradition input.txt output_folder config.yaml
```

This will output the generated text as well as the tree structure in the folder `output_folder`.

Demonstration data is available in the folder `./demo`.

