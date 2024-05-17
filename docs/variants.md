# Scribal behavior modelization

StemmaBench relies on the assumption that scribal behavior can be successfully modelized using probabilistic processes.

The parameters are specified in a YAML file, such as:

```yaml
meta:
  language: en

variants:
  letters:
    mispell:
      law: Bernouilli
      rate: 0.05
      args:
        specific_rates:
          a:
            b: 0.01
            c: 0.02
          b:
            a: 0.02
            c: 0.01
  words:
    synonym:
      law: Bernouilli
      rate: 0.1
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
  missing_manuscripts:
    law: Bernouilli
    rate: 0.5
```

## Scribal dependent variants

For now, the following possible variants are modelized using a Bernouilli law, meaning that each time a word is "generated" (*i.e.* each time a scribe "writes" a word) the word is modified with probability *p* (else it remains the same).

Possible variants are:

### At the letter level
This section is used to customize the probability of a letter being modified according to a custom rate given by the user in the **specific_rates** field.

- **rate**: Represents the total probability of a letter being modified.
> [!WARNING]
> Rate include values of **specific_rates**. If the sum of the **specific_rates** is greater than **rate** an error will be raised.

- **specific_rates**: Represents the probability of a letter being substituted with another letter. If letter is not in **specific_rates** the probality of that letter be substituted is equal to : (**rate**-sum(**specific_rates**))/(lenght(alphabet)-lenght(**specific_rates**)).

### Exemple of specific_rates

Let a alphabet with 4 letters: a, b, c, d. We define the following YAML file:
```yaml
meta:
  language: en

variants:
  letters:
    mispell:
      law: Bernouilli
      rate: 0.05
      args:
        specific_rates:
          a:
            b: 0.01
            c: 0.02
          b:
            a: 0.01
          c:
            a: 0.02
  words:
    synonym:
      law: Bernouilli
      rate: 0.1
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
  missing_manuscripts:
    law: Bernouilli
    rate: 0.5
```

This configuration generates the following matrix of probabilities for misspelling letters:
```yaml
a:
  a: 0.95
  b: 0.01
  c: 0.02
  d: 0.02
b:
  a: 0.01
  b: 0.95
  c: 0.02
  d: 0.02
c:
  a: 0.02
  b: 0.015
  c: 0.95
  d: 0.015
d:
  a: 0.016
  b: 0.016
  c: 0.016
  d: 0.95
```

### At the letter level

- **Mispell**: The probability of a letter being substituded is decided according to a Bernouilli distribution with the probability **rate**. The substitution is done by drawing a random letter according the probability matrix define above.

### At the word level

- **Word omission**: The word is omitted.
- **Synonym**: A synonym is randomly drawn from NLTK semantic net.

### At the sentence level

- **Duplication**: A word can be copied several times. A random location in the sentence is selected, and words are duplicated by a configurable number of words (for now, fixed).


## Scribal independent variants

### Fragmentation

### Missing manuscripts
In the StemmaBench package, the concept of missing manuscripts is modeled using a probabilistic process governed by a p-parameter Bernoulli distribution. After having generated the whole tradition, a proportion *p* of the manuscripts are selected (with equiprobability) and deleted from the tradition. This simulates the loss of certain manuscripts over time.

> [!WARNING IN RAM]
> 
> Currently, the missing manuscript feature is only available after dumping the stemma to a folder using the *dump()* method.


## Supported languages
Two languages are currently supported:
- English;
- Greek.

Additional support for biblical Hebrew is underway.
