# Scribal behavior modelization

StemmaBench relies on the assumption that scribal behavior can be successfully modelized using probabilistic processes.

The parameters are specified into a YAML file, such as:

```yaml
meta:
  language: eng

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

stemma:
  depth: 2
  width:
    law: Uniform
    min: 2
    max: 4
```

## Scribal dependent variants

For now, the following possible variants are modelized using a Bernouilli law, meaning that each time a word is "generated" (*i.e.* each time a scribe "writes" a word) the word is modified with probability *p* (else it remains the same).

Possible variants are:

### At the word level

- **Word mispell**: A random letter location is drawn according to a uniform law across the whole word. The letter is then replace with a randomly drawn letter from the alphabet.
- **Word omission**: The word is omitted.
- **Synonym**: A synonym is randomly drawn from NLTK semantic net.

### At the sentence level

- **Duplication**: A word can be copied several times. A random location in the sentence is selected, and words are duplicated by a configurable number of words (for now, fixed).


## Scribal independent variants

### Fragmentation

### Missing manuscripts