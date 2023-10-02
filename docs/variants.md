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
- **Synonym**: A synonym is randomly drawn from NLTK semantic net.

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
