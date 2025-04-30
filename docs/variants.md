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

- **specific_rates**: Represents the probability of a letter being substituted with another letter. If letter is not in **specific_rates** the probability of that letter to be substituted is equal to : (**rate**-sum(**specific_rates**))/(length(alphabet)-length(**specific_rates**)).

### Exemple of specific_rates

We define the following YAML file:
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
  b: 0.02
  c: 0.001
  d: 0.001
  e: 0.001
  f: 0.001
  g: 0.001
  h: 0.001
  i: 0.001
  j: 0.001
  k: 0.001
  l: 0.001
  m: 0.001
  n: 0.001
  o: 0.001
  p: 0.001
  q: 0.001
  r: 0.001
  s: 0.001
  t: 0.001
  u: 0.001
  v: 0.001
  w: 0.001
  x: 0.001
  y: 0.001
  z: 0.001
b:
  a: 0.01
  b: 0.95
  c: 0.002
  d: 0.002
  e: 0.002
  f: 0.002
  g: 0.002
  h: 0.002
  i: 0.002
  j: 0.002
  k: 0.002
  l: 0.002
  m: 0.002
  n: 0.002
  o: 0.002
  p: 0.002
  q: 0.002
  r: 0.002
  s: 0.002
  t: 0.002
  u: 0.002
  v: 0.002
  w: 0.002
  x: 0.002
  y: 0.002
  z: 0.002
c:
  a: 0.02
  b: 0.001
  c: 0.95
  d: 0.001
  e: 0.001
  f: 0.001
  g: 0.001
  h: 0.001
  i: 0.001
  j: 0.001
  k: 0.001
  l: 0.001
  m: 0.001
  n: 0.001
  o: 0.001
  p: 0.001
  q: 0.001
  r: 0.001
  s: 0.001
  t: 0.001
  u: 0.001
  v: 0.001
  w: 0.001
  x: 0.001
  y: 0.001
  z: 0.001
d:
  a: 0.002
  b: 0.002
  c: 0.002
  d: 0.95
  e: 0.002
  f: 0.002
  g: 0.002
  h: 0.002
  i: 0.002
  j: 0.002
  k: 0.002
  l: 0.002
  m: 0.002
  n: 0.002
  o: 0.002
  p: 0.002
  q: 0.002
  r: 0.002
  s: 0.002
  t: 0.002
  u: 0.002
  v: 0.002
  w: 0.002
  x: 0.002
  y: 0.002
  z: 0.002
e:
  a: 0.002
  b: 0.002
  c: 0.002
  d: 0.002
  e: 0.95
  f: 0.002
  g: 0.002
  h: 0.002
  i: 0.002
  j: 0.002
  k: 0.002
  l: 0.002
  m: 0.002
  n: 0.002
  o: 0.002
  p: 0.002
  q: 0.002
  r: 0.002
  s: 0.002
  t: 0.002
  u: 0.002
  v: 0.002
  w: 0.002
  x: 0.002
  y: 0.002
  z: 0.002
f:
  a: 0.002
  b: 0.002
  c: 0.002
  d: 0.002
  e: 0.002
  f: 0.95
  g: 0.002
  h: 0.002
  i: 0.002
  j: 0.002
  k: 0.002
  l: 0.002
  m: 0.002
  n: 0.002
  o: 0.002
  p: 0.002
  q: 0.002
  r: 0.002
  s: 0.002
  t: 0.002
  u: 0.002
  v: 0.002
  w: 0.002
  x: 0.002
  y: 0.002
  z: 0.002
g:
  a: 0.002
  b: 0.002
  c: 0.002
  d: 0.002
  e: 0.002
  f: 0.002
  g: 0.95
  h: 0.002
  i: 0.002
  j: 0.002
  k: 0.002
  l: 0.002
  m: 0.002
  n: 0.002
  o: 0.002
  p: 0.002
  q: 0.002
  r: 0.002
  s: 0.002
  t: 0.002
  u: 0.002
  v: 0.002
  w: 0.002
  x: 0.002
  y: 0.002
  z: 0.002
h:
  a: 0.002
  b: 0.002
  c: 0.002
  d: 0.002
  e: 0.002
  f: 0.002
  g: 0.002
  h: 0.95
  i: 0.002
  j: 0.002
  k: 0.002
  l: 0.002
  m: 0.002
  n: 0.002
  o: 0.002
  p: 0.002
  q: 0.002
  r: 0.002
  s: 0.002
  t: 0.002
  u: 0.002
  v: 0.002
  w: 0.002
  x: 0.002
  y: 0.002
  z: 0.002
i:
  a: 0.002
  b: 0.002
  c: 0.002
  d: 0.002
  e: 0.002
  f: 0.002
  g: 0.002
  h: 0.002
  i: 0.95
  j: 0.002
  k: 0.002
  l: 0.002
  m: 0.002
  n: 0.002
  o: 0.002
  p: 0.002
  q: 0.002
  r: 0.002
  s: 0.002
  t: 0.002
  u: 0.002
  v: 0.002
  w: 0.002
  x: 0.002
  y: 0.002
  z: 0.002
j:
  a: 0.002
  b: 0.002
  c: 0.002
  d: 0.002
  e: 0.002
  f: 0.002
  g: 0.002
  h: 0.002
  i: 0.002
  j: 0.95
  k: 0.002
  l: 0.002
  m: 0.002
  n: 0.002
  o: 0.002
  p: 0.002
  q: 0.002
  r: 0.002
  s: 0.002
  t: 0.002
  u: 0.002
  v: 0.002
  w: 0.002
  x: 0.002
  y: 0.002
  z: 0.002
k:
  a: 0.002
  b: 0.002
  c: 0.002
  d: 0.002
  e: 0.002
  f: 0.002
  g: 0.002
  h: 0.002
  i: 0.002
  j: 0.002
  k: 0.95
  l: 0.002
  m: 0.002
  n: 0.002
  o: 0.002
  p: 0.002
  q: 0.002
  r: 0.002
  s: 0.002
  t: 0.002
  u: 0.002
  v: 0.002
  w: 0.002
  x: 0.002
  y: 0.002
  z: 0.002
l:
  a: 0.002
  b: 0.002
  c: 0.002
  d: 0.002
  e: 0.002
  f: 0.002
  g: 0.002
  h: 0.002
  i: 0.002
  j: 0.002
  k: 0.002
  l: 0.95
  m: 0.002
  n: 0.002
  o: 0.002
  p: 0.002
  q: 0.002
  r: 0.002
  s: 0.002
  t: 0.002
  u: 0.002
  v: 0.002
  w: 0.002
  x: 0.002
  y: 0.002
  z: 0.002
m:
  a: 0.002
  b: 0.002
  c: 0.002
  d: 0.002
  e: 0.002
  f: 0.002
  g: 0.002
  h: 0.002
  i: 0.002
  j: 0.002
  k: 0.002
  l: 0.002
  m: 0.95
  n: 0.002
  o: 0.002
  p: 0.002
  q: 0.002
  r: 0.002
  s: 0.002
  t: 0.002
  u: 0.002
  v: 0.002
  w: 0.002
  x: 0.002
  y: 0.002
  z: 0.002
n:
  a: 0.002
  b: 0.002
  c: 0.002
  d: 0.002
  e: 0.002
  f: 0.002
  g: 0.002
  h: 0.002
  i: 0.002
  j: 0.002
  k: 0.002
  l: 0.002
  m: 0.002
  n: 0.95
  o: 0.002
  p: 0.002
  q: 0.002
  r: 0.002
  s: 0.002
  t: 0.002
  u: 0.002
  v: 0.002
  w: 0.002
  x: 0.002
  y: 0.002
  z: 0.002
o:
  a: 0.002
  b: 0.002
  c: 0.002
  d: 0.002
  e: 0.002
  f: 0.002
  g: 0.002
  h: 0.002
  i: 0.002
  j: 0.002
  k: 0.002
  l: 0.002
  m: 0.002
  n: 0.002
  o: 0.95
  p: 0.002
  q: 0.002
  r: 0.002
  s: 0.002
  t: 0.002
  u: 0.002
  v: 0.002
  w: 0.002
  x: 0.002
  y: 0.002
  z: 0.002
p:
  a: 0.002
  b: 0.002
  c: 0.002
  d: 0.002
  e: 0.002
  f: 0.002
  g: 0.002
  h: 0.002
  i: 0.002
  j: 0.002
  k: 0.002
  l: 0.002
  m: 0.002
  n: 0.002
  o: 0.002
  p: 0.95
  q: 0.002
  r: 0.002
  s: 0.002
  t: 0.002
  u: 0.002
  v: 0.002
  w: 0.002
  x: 0.002
  y: 0.002
  z: 0.002
q:
  a: 0.002
  b: 0.002
  c: 0.002
  d: 0.002
  e: 0.002
  f: 0.002
  g: 0.002
  h: 0.002
  i: 0.002
  j: 0.002
  k: 0.002
  l: 0.002
  m: 0.002
  n: 0.002
  o: 0.002
  p: 0.002
  q: 0.95
  r: 0.002
  s: 0.002
  t: 0.002
  u: 0.002
  v: 0.002
  w: 0.002
  x: 0.002
  y: 0.002
  z: 0.002
r:
  a: 0.002
  b: 0.002
  c: 0.002
  d: 0.002
  e: 0.002
  f: 0.002
  g: 0.002
  h: 0.002
  i: 0.002
  j: 0.002
  k: 0.002
  l: 0.002
  m: 0.002
  n: 0.002
  o: 0.002
  p: 0.002
  q: 0.002
  r: 0.95
  s: 0.002
  t: 0.002
  u: 0.002
  v: 0.002
  w: 0.002
  x: 0.002
  y: 0.002
  z: 0.002
s:
  a: 0.002
  b: 0.002
  c: 0.002
  d: 0.002
  e: 0.002
  f: 0.002
  g: 0.002
  h: 0.002
  i: 0.002
  j: 0.002
  k: 0.002
  l: 0.002
  m: 0.002
  n: 0.002
  o: 0.002
  p: 0.002
  q: 0.002
  r: 0.002
  s: 0.95
  t: 0.002
  u: 0.002
  v: 0.002
  w: 0.002
  x: 0.002
  y: 0.002
  z: 0.002
t:
  a: 0.002
  b: 0.002
  c: 0.002
  d: 0.002
  e: 0.002
  f: 0.002
  g: 0.002
  h: 0.002
  i: 0.002
  j: 0.002
  k: 0.002
  l: 0.002
  m: 0.002
  n: 0.002
  o: 0.002
  p: 0.002
  q: 0.002
  r: 0.002
  s: 0.002
  t: 0.95
  u: 0.002
  v: 0.002
  w: 0.002
  x: 0.002
  y: 0.002
  z: 0.002
u:
  a: 0.002
  b: 0.002
  c: 0.002
  d: 0.002
  e: 0.002
  f: 0.002
  g: 0.002
  h: 0.002
  i: 0.002
  j: 0.002
  k: 0.002
  l: 0.002
  m: 0.002
  n: 0.002
  o: 0.002
  p: 0.002
  q: 0.002
  r: 0.002
  s: 0.002
  t: 0.002
  u: 0.95
  v: 0.002
  w: 0.002
  x: 0.002
  y: 0.002
  z: 0.002
v:
  a: 0.002
  b: 0.002
  c: 0.002
  d: 0.002
  e: 0.002
  f: 0.002
  g: 0.002
  h: 0.002
  i: 0.002
  j: 0.002
  k: 0.002
  l: 0.002
  m: 0.002
  n: 0.002
  o: 0.002
  p: 0.002
  q: 0.002
  r: 0.002
  s: 0.002
  t: 0.002
  u: 0.002
  v: 0.95
  w: 0.002
  x: 0.002
  y: 0.002
  z: 0.002
w:
  a: 0.002
  b: 0.002
  c: 0.002
  d: 0.002
  e: 0.002
  f: 0.002
  g: 0.002
  h: 0.002
  i: 0.002
  j: 0.002
  k: 0.002
  l: 0.002
  m: 0.002
  n: 0.002
  o: 0.002
  p: 0.002
  q: 0.002
  r: 0.002
  s: 0.002
  t: 0.002
  u: 0.002
  v: 0.002
  w: 0.95
  x: 0.002
  y: 0.002
  z: 0.002
x:
  a: 0.002
  b: 0.002
  c: 0.002
  d: 0.002
  e: 0.002
  f: 0.002
  g: 0.002
  h: 0.002
  i: 0.002
  j: 0.002
  k: 0.002
  l: 0.002
  m: 0.002
  n: 0.002
  o: 0.002
  p: 0.002
  q: 0.002
  r: 0.002
  s: 0.002
  t: 0.002
  u: 0.002
  v: 0.002
  w: 0.002
  x: 0.95
  y: 0.002
  z: 0.002
y:
  a: 0.002
  b: 0.002
  c: 0.002
  d: 0.002
  e: 0.002
  f: 0.002
  g: 0.002
  h: 0.002
  i: 0.002
  j: 0.002
  k: 0.002
  l: 0.002
  m: 0.002
  n: 0.002
  o: 0.002
  p: 0.002
  q: 0.002
  r: 0.002
  s: 0.002
  t: 0.002
  u: 0.002
  v: 0.002
  w: 0.002
  x: 0.002
  y: 0.95
  z: 0.002
z:
  a: 0.002
  b: 0.002
  c: 0.002
  d: 0.002
  e: 0.002
  f: 0.002
  g: 0.002
  h: 0.002
  i: 0.002
  j: 0.002
  k: 0.002
  l: 0.002
  m: 0.002
  n: 0.002
  o: 0.002
  p: 0.002
  q: 0.002
  r: 0.002
  s: 0.002
  t: 0.002
  u: 0.002
  v: 0.002
  w: 0.002
  x: 0.002
  y: 0.002
  z: 0.95
```

### At the letter level

- **Mispell**: The probability of a letter being substituted is decided according to a Bernouilli distribution with the probability **rate**. The substitution is done by drawing a random letter according to the probability matrix defined above.

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
