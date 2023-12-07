# Scribal behavior modelization

StemmaBench relies on the assumption that scribal behavior can be successfully modelized using probabilistic processes.

The parameters are specified into a YAML file, such as:

```yaml
meta:
  language: en

variants:
  words:
    synonym:
      law: Bernouilli
      rate: 0.1
    mispell:
      law: Bernouilli
      rate: 0.05
    omit:
      law: Bernouilli
      rate: 0.05
  sentences:
    duplicate:
      args:
        nbr_words: 2
      law: Bernouilli
      rate: 0.1
  texts:
    fragmentation:
      max_rate: 0.5
      distribution: 
        law: Poisson
        rate: 0.9

stemma:
  depth: 2
  width:
    law: Uniform
    min: 2
    max: 4
  missing_manuscripts:
    law: Bernouilli
    rate: 0.5
  fragmentation_proba: 1
```

## Scribal dependent variants

For now, the following possible variants are modelized using a Bernouilli law, meaning that each time a word is "generated" (*i.e.* each time a scribe "writes" a word) the word is modified with probability *p* (else it remains the same).

Possible variants are:

### At the word level

- **Word mispell**: A random letter location is drawn according to a uniform law across the whole word. The letter is then replace with a randomly drawn letter from the alphabet.
- **Word omission**: The word is omitted.
- **Synonym**: A synonym is randomly drawn from a hard-coded dictionary.

### At the sentence level

- **Duplication**: A word can be copied several times. A random location in the sentence is selected, and words are duplicated by a configurable number of words (for now, fixed).


## Scribal independent variants

### Fragmentation
Fragmentation refers to the loss of certain parts of the text over time. In our modeling approach, we represent this as the deletion of some words within the text. The whole process occurs **_at the text level_** as follows:

After each level of generation, each manuscript within the tradition can be impacted by fragmentation with a probability, called fragmentation probability, constant over time. This means that some manuscripts may remain unaffected and preserve the original text, while others experience the loss of words due to fragmentation. The parameter `fragmentation_probability` defines the likelihood that a manuscript is affected by fragmentation. It essentially controls how widespread fragmentation is across the various manuscripts in the stemma.
 
For each manuscript that is affected, we determine the degree of fragmentation, or the fragmentation rate, which signifies the extent of this phenomenon within that particular manuscript. The `max_rate` parameter sets the upper limit within a [0, 1] subset interval from which we derive the actual fragmentation rate for each manuscript. 

Subsequently, we employ the `distribution` input to designate the specific locations within the text where word deletions will occur. The underlying concept here is that certain portions of the text, (for e.g. the beginning or the end), may be more susceptible to fragmentation. The distribution parameter allows us to account for these characteristics by specifying where in the text the deletions are more likely to happen.

### Missing manuscripts
In the StemmaBench package, the concept of missing manuscripts is modeled using a probabilistic process governed by a p-parameter Bernoulli distribution. After having generating the whole tradition, a proportion *p* of the manuscripts are selected (with equiprobability) and deleted from the tradition. This simulates the loss of certain manuscripts over time.

> [!WARNING]
> 
> Currently, the missing manunscript feature is only available in command-line interface, not in RAM.

## Supported languages
Two languages are currently supported:
- English;
- Greek.

Additional support for biblical Hebrew is underway.



# Variant analyzer

The `variant_analyzer` module is designed for **analyzing text variants**. It identifies variant positions and types for manuscript comparisons and estimates operation probabilities like omission and misspelling rates. This module utilizes a class that takes a `collatex` alignment table as input, converting it into a NumPy array for analysis.

The `utils` module provides convenient functions for **loading traditions from folders** and **formatting them** similar to the `Stemma` class's `texts_lookup` method. These tools simplify variant analysis in your text data.

Methods are provided to identify variant locations between pairs of witnesses, determine the type of variant between two words, and calculate the dissimilarity matrix and operation rates for different types of variants. Additional methods are provided to analyze fragmentation in the alignment table, including identifying fragment locations, calculating fragment rates, and estimating the fragmentation distribution.

- The method `variant_locations_pairwise_matrix()` creates a boolean symmetric 3D array, which is a matrix composed of mask vectors (vectors of booleans). This matrix signifies, for each pair of manuscripts, whether each corresponding reading represents a variant location or not.
- The method `variant_type_pairwise_matrix()` identifies the type of variant for each variant location within the variant_locations_pairwise_matrix result, using the following labels: "O" for omit, "M" for misspell, "S" for synonym, "U" for undetermined, and False for locations that are not variant.
- The method `dissimilarity_matrix()` generates a dissimilarity matrix between manuscripts, considering a specific variant type.
- For fragmentation analysis, the computation is performed at the individual manuscript level by identifying missing readings. The function `fragment_locations_matrix()` produces a 2D array with manuscripts as rows and columns, containing booleans to indicate if a reading is missing or not. Additionally, the function `fragment_locations_count()` returns a vector indicating the number of missing readings for each manuscript.
- The methods `omit_rate()`, `misspell_rate()`, `synonym_rate()`, `undetermined_rate()`, and `fragment_rate()` provide estimates of the occurrence rates across manuscripts estimates. For all operations except fragmentation, the rates are computed as the average rate across pairs of manuscripts. In the case of fragmentation, the default behaviour is to use the maximum rate of fragmentation to maintain consistency with the implementation of fragmentation in the generation process. However, it also allows for using the "mean" rate if needed.
- `analysis_summary()` return a dictionary with the estimated rate. It is possible to select only a subset of the operation. Also, if the `disable_synonyms` property of the `VariantAnalyzer`  is set to `True` then synonym rate is never return. The latter `disable_synonyms` property depends on whether the language is supported.


```python
# Assuming your have all your witnesses (as .txt file) in a folder named "input_folder".

# Load tradition from the input file.
tradition = load_tradition(input_folder="input_folder")
# Format tradition as input for collatex collation and alignment table.
tradition_formatted = format_tradition(tradition=tradition)
# Create alignment table
collation = collatex.Collation().create_from_dict(tradition_formatted)
alignment_table = collatex.collate(
    collation, segmentation=False, near_match=True, layout="vertical"
)
# Create a VariantAnalyzer object
analyzer = VariantAnalyzer(alignment_table, language="en")
# Calculate the omit rate
omit_rate = analyzer.omit_rate()
# Calculate the misspelling rate
mispell_rate = analyzer.mispell_rate()
# Calculate the synonym rate
synonym_rate = analyzer.synonym_rate()
# Calculate the fragment rate
fragment_rate = analyzer.fragment_rate()
# Get the fragment distribution
fragment_distribution = analyzer.fragment_distribution()
```


- #TODO: 
- [ ] Allow for using directly a numpy array as input (requiring the rows to be the witnesses and the columns to be the readings). 


