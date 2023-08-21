"""
Unit tests for textual units.
"""
import unittest
import unittest.mock
import numpy as np
from stemmabench.config_parser import (
    ProbabilisticConfig,
    FragmentationConfig, 
    VariantConfig, 
    TextConfig,
    MetaConfig
)
from stemmabench.textual_units.text import Text
from stemmabench.textual_units.sentence import Sentence
from stemmabench.textual_units.word import Word
from stemmabench.data import LETTERS

class TestWord(unittest.TestCase):
    """Unit tests for the Word class.
    """

    def setUp(self):
        """Setup the unit test.
        """
        np.random.seed(1)
        self.test_word = Word("rabbit")
        self.test_word_no_synonym = Word("toto")

    def test_init(self):
        """Tests that class initialization behaves as expected,
        even in the case of a capitalized or punctuated string.
        """
        self.assertEqual(self.test_word.word, "rabbit")

    def test_clean(self):
        """Tests that in the case of a word tainted by punctuation,
        the cleaning behaves as expected.
        """
        self.assertEqual(Word("Rabbit.").word, "rabbit")

    def test_synonym(self):
        """Tests that returning a synonym works as expected when.
        """
        self.assertEqual(self.test_word.synonym(), "hare")

    def test_no_synonym(self):
        """Tests that returning a synonym works as expected when.
        """
        self.assertEqual(self.test_word_no_synonym.synonym(), self.test_word_no_synonym.word)

    def test_mispell(self):
        """Tests that mispells behave as expected.
        """
        self.assertEqual(self.test_word.mispell(), "rabbil")

    def test_omit(self):
        """Tests that omitting a word behaves as expected.
        """
        self.assertEqual(self.test_word.omit(), "")

    def test_greek_mispell(self):
        """Tests that working with greek characters behaves as expected by
        using greek only characters.
        """
        test_word = Word("λειπω", language="gr")
        self.assertFalse(
            sum((letter not in LETTERS["gr"]) for letter in test_word.mispell())
        )

    def test_greek_synonym(self):
        """Tests that working with greek characters behaves as expected when requesting greek
        synonyms.
        """
        test_word = Word("λείπω", language="gr")
        self.assertEqual(
            test_word.synonym(),
            "ἐκπρολείπω"
        )

class TestSentence(unittest.TestCase):
    """Unit tests for the Sentence class.
    """

    def setUp(self):
        """Set up the unit tests.
        """
        np.random.seed(5)
        self.test_sentence = Sentence("The rabbit is blue.")

    def test_init_sentence(self):
        """Tests that the attributes computed at the sentence level
        behave as expected.
        """
        self.assertEqual(self.test_sentence.sentence,
                         "The rabbit is blue.")
        self.assertListEqual(self.test_sentence.words,
                             ["the", "rabbit", "is", "blue"])
        self.assertEqual(self.test_sentence.nbr_words, 4)

    def test_duplicate(self):
        """Tests that duplicating the sentence behaves as expected.
        """
        # In the cae where the nbr of words is more than the requested
        # switched sentence length
        self.assertEqual(self.test_sentence.duplicate(nbr_words=2),
                         "The rabbit is rabbit is blue.")
        # In the case where the nbr of words is too high, simply return
        # the sentence
        self.assertEqual(self.test_sentence.duplicate(nbr_words=5),
                         "The rabbit is blue.")


class TestText(unittest.TestCase):
    """Unit tests for the Text class.
    """

    def setUp(self):
        """Setup the unit testing by creating a test instance of the
        text.
        """
        np.random.seed(15)
        self.test_text = Text(
            "But, first, remember, remember, remember the signs. "
            "Say them to yourself when you wake in the morning "
            "and when you lie down at night, "
            "and when you wake in the middle of the night.")
        self.test_text2 = Text("word1, word2. word3, word4 word5.")

    def test_init(self):
        """Tests that the initialization of the Text class behaves
        as expected.
        """
        self.assertEqual(self.test_text.text,
                         "But, first, remember, remember, remember the signs. "
                         "Say them to yourself when you wake in the morning "
                         "and when you lie down at night, "
                         "and when you wake in the middle of the night.")
        # Check that everything is ok for the first sentence
        self.assertEqual(self.test_text.sentences[0].sentence,
                         Sentence("But, first, remember, remember, remember the signs").sentence)
        # Check that everything is ok for the second sentence
        self.assertEqual(self.test_text.words[0].word,
                         Word("but").word)

    def test_sentence_transform(self):
        """Tests that transformation for a sentence works as expected,
        by transforming the first sentence.
        """
        test_config = {
            "duplicate": ProbabilisticConfig(
                **{
                    "args": {
                        "nbr_words": 1
                    },
                    "law": "Bernouilli",
                    "rate": 1
                })
        }
        transformed_sentence = self.test_text.transform_sentence(self.test_text.sentences[0],
                                                                 sentence_config=test_config)
        self.assertEqual(transformed_sentence,
                         "But first remember remember remember remember the signs.")

    def test_sentences_transform(self):
        """Tests that transformation for all the sentences of the text behaves
        as expected.
        """
        test_config = {
            "duplicate": ProbabilisticConfig(
                **{
                    "args": {
                        "nbr_words": 1
                    },
                    "law": "Bernouilli",
                    "rate": 1
                })
        }
        transformed_sentences = self.test_text.transform_sentences(
            sentence_config=test_config
        )
        self.assertEqual(
            transformed_sentences,
            "But first remember remember remember remember the signs. "
            "Say them to yourself when you wake in the morning and when you lie "
            "down at night and when you wake in the middle of the night."
        )

    def test_word_transform(self):
        """Tests that transforming at the word level behaves as expected.
        """
        word_config = {
            "synonym": ProbabilisticConfig(**{
                "law": "Bernouilli",
                "rate": 1,
                "args": {}
            }),
            "mispell": ProbabilisticConfig(**{
                "law": "Bernouilli",
                "rate": 1,
                "args": {}
            }),
            "omit": ProbabilisticConfig(**{
                "law": "Bernouilli",
                "rate": 0.2,
                "args": {}

            })
        }
        self.assertEqual("home alive",
                         self.test_text.transform_word(self.test_text.words[27],
                                                       word_config=word_config))

    def test_words_transform(self):
        """Tests that transformation at the words level behaves as expected.
        """
        word_config = {
            "synonym": ProbabilisticConfig(**{
                "law": "Bernouilli",
                "rate": 0.1,
                "args": {}
            }),
            "mispell": ProbabilisticConfig(**{
                "law": "Bernouilli",
                "rate": 1,
                "args": {}
            }),
            "omit": ProbabilisticConfig(**{
                "law": "Bernouilli",
                "rate": 0.1,
                "args": {}
            })
        }
        self.assertEqual(
            "hut onlx firmt  relember reiember hhe figns",
            self.test_text.transform_words(
                sentence="But but first remember remember remember the signs.",
                word_config=word_config,
                language="en"))

    def test_text_transform(self):
        """Tests that the transformation of the text behaves as expected.
        """
        np.random.seed(15)
        meta_config = MetaConfig(**{"language": "en"})
        variant_config = VariantConfig(**{
            "sentences": {
                "duplicate": ProbabilisticConfig(**{
                    "args": {
                        "nbr_words": 1
                    },
                    "law": "Bernouilli",
                    "rate": 1
                })
            },
            "words": {
                "synonym": ProbabilisticConfig(**{
                    "law": "Bernouilli",
                    "rate": 0.1,
                    "args": {}
                }),
                "mispell": ProbabilisticConfig(**{
                    "law": "Bernouilli",
                    "rate": 1,
                    "args": {}
                }),
                "omit": ProbabilisticConfig(**{
                    "law": "Bernouilli",
                    "rate": 0.1,
                    "args": {}
                })
             },
             "texts": TextConfig(**{
                 "fragmentation": FragmentationConfig(**{
                     "max_rate": 0.5,
                     "distribution": ProbabilisticConfig(**{
                         "law": "Poisson",
                         "rate": 0.9
                     })
                 })
             })
        })
        self.assertEqual("But bht firit rememzer remembhr remembes thu pigns. Saf jay  tm yoursclf whmn you vake  tfe morbing ahd  yom rert dowa et nihht anl wuen yos wade is dhe muddle ol thd nioht.",
            self.test_text.transform(variant_config=variant_config, meta_config=meta_config)
        )

    def test_fragment_deletion(self):
        """Test fragmentation
        """
        fragment_config = FragmentationConfig(**{
            "max_rate": 1,
            "distribution": ProbabilisticConfig(**{
                "law": "Poisson",
                "rate": 0.9
            })
        })

        self.assertEqual(Text(self.test_text2.text, seed=15)
                         .fragment(fragment_config),"word4 word5.")

if __name__ == "__main__":
    unittest.main()
