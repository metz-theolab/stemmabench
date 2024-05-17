"""
Unit tests for textual units.
"""
import unittest
import numpy as np
from stemmabench.bench.config_parser import MetaConfig, ProbabilisticConfig, VariantConfig
from stemmabench.bench.textual_units.text import Text
from stemmabench.bench.textual_units.sentence import Sentence
from stemmabench.bench.textual_units.word import Word
from stemmabench.bench.textual_units.letter import Letter
from stemmabench.bench.data import LETTERS


class TestLetter(unittest.TestCase):
    """Unit tests for the Letter class.
    """

    def setUp(self):
        self.test_letter = Letter("a")
        self.rate = 0.6
        self.specific_rates = {
            "a": {'b': 0.3, 'c': 0.2, 'd': 0.025},
            "b": {'d': 0.1}
        }
        self.alphabet = ["a", "b", "c", "d"]

    def test_init(self):
        """Tests that the initialization of the Letter class behaves as expected.
        """
        self.assertEqual(self.test_letter.letter, "a")

    def test_build_probability_matrix(self):
        """Tests that the probability matrix is built as expected.
        """
        probability_matrix = self.test_letter.build_probability_matrix(
            rate=self.rate,
            specific_rates=self.specific_rates,
            alphabet=self.alphabet
        )
        self.assertDictEqual(
            probability_matrix,
                {
                 'a': {'b': 0.3, 'c': 0.2, 'd': 0.025, 'a': 0.4},
                 'b': {'d': 0.1, 'b': 0.4, 'c': 0.25, 'a': 0.25},
                 'c': {'c': 0.4, 'b': 0.19999999999999998, 'a': 0.19999999999999998, 'd': 0.19999999999999998},
                 'd': {'d': 0.4, 'b': 0.19999999999999998, 'c': 0.19999999999999998, 'a': 0.19999999999999998}
                 }
            )

    def test_wrong_build_probability_matrix(self):
        """Tests that the probability matrix is built as expected.
        """
        with self.assertRaises(ValueError):
            wrong_specific_rate = {
                "a": {'b': 0.3, 'c': 0.2, 'd': 0.3},
                "b": {'d': 0.1}
            }
            self.test_letter.build_probability_matrix(
                rate=self.rate,
                specific_rates= wrong_specific_rate,
                alphabet=["a", "b", "c"]
            )

    def test_mispell(self):
        """Tests that mispelling a letter behaves as expected.
        """
        np.random.seed(1)
        self.assertEqual(self.test_letter.mispell(
            rate=self.rate,
            specific_rates=self.specific_rates
        ), "c")


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
        self.assertEqual(self.test_word_no_synonym.synonym(),
                         self.test_word_no_synonym.word)

    def test_omit(self):
        """Tests that omitting a word behaves as expected.
        """
        self.assertEqual(self.test_word.omit(), "")

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
        np.random.seed(15)
        word_config = {
            "synonym": ProbabilisticConfig(**{
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
        self.assertEqual("come alive",
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
            "omit": ProbabilisticConfig(**{
                "law": "Bernouilli",
                "rate": 0.1,
                "args": {}
            })
        }
        self.assertEqual(
            "but simply  remember remember think of the signs",
            self.test_text.transform_words(
                sentence="But but first remember remember remember the signs.",
                word_config=word_config,
                language="en"))

    def test_letter_transform(self):
        """Tests that transforming a sentence at the letter level behaves as expected.
        """
        np.random.seed(15)
        letter_config = {
            "mispell": ProbabilisticConfig(**{
                "law": "Bernouilli",
                "rate": 1,
                "args": {
                    "specific_rates": {
                        "a": {
                            "b": 0.999,
                            "c": 0.001
                        },
                }
            }})
        }
        self.assertEqual(
            "b",
            self.test_text.transform_letter(
                letter=Letter("a"),
                letter_config=letter_config,
            )
        )

    def test_letters_transform(self):
        """
        Tests that transforming a sentence at the letter level behaves as expected.
        """
        letter_config = {
            "mispell": ProbabilisticConfig(**{
                "law": "Bernouilli",
                "rate": 1,
                "args": {
                    "specific_rates": {
                        "a": {
                            "b": 1,
                        },
                        "b": {
                            "c": 1,
                        },
                        "c": {
                            "d": 1,
                        },
                        "d": {
                            "e": 1,
                        },
                        "e": {
                            "f": 1,
                        },
                        "f": {
                            "g": 1,
                        },
                        "g": {
                            "h": 1,
                        },
                        "h": {
                            "i": 1,
                        },
                        "i": {
                            "j": 1,
                        },
                        "j": {
                            "k": 1,
                        },
                        "k": {
                            "l": 1,
                        },
                        "l": {
                            "m": 1,
                        },
                        "m": {
                            "n": 1,
                        },
                        "n": {
                            "o": 1,
                        },
                        "o": {
                            "p": 1,
                        },
                        "p": {
                            "q": 1,
                        },
                        "q": {
                            "r": 1,
                        },
                        "r": {
                            "s": 1,
                        },
                        "s": {
                            "t": 1,
                        },
                        "t": {
                            "u": 1,
                        },
                        "u": {
                            "v": 1,
                        },
                        "v": {
                            "w": 1,
                        },
                        "w": {
                            "x": 1,
                        },
                        "x": {
                            "y": 1,
                        },
                        "y": {
                            "z": 1,
                        },
                        "z": {
                            "a": 1,
                        },
                }
            }})
}
        self.assertEqual(
            "cvu, gjstu, sfnfncfs, sfnfncfs, sfnfncfs uif tjhot.",
            self.test_text.transform_letters(
                sentence="But, first, remember, remember, remember the signs.",
                letter_config=letter_config,
                language="en"
            )
        )

    def test_text_transform(self):
        """Tests that the transformation of the text behaves as expected.
        """
        np.random.seed(3)
        meta_config = MetaConfig(**{"language": "en"})
        variant_config = VariantConfig(**{
            "sentences": {
                "duplicate": ProbabilisticConfig(
                    **{
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
                "omit": ProbabilisticConfig(**{
                    "law": "Bernouilli",
                    "rate": 0.1,
                    "args": {}
                })
            },
            "letters": {
                "mispell": ProbabilisticConfig(**{
                    "law": "Bernouilli",
                    "rate": 0.3,
                    "args": {
                        "specific_rates": {
                            "a": {
                                "d": 0.025
                            },
                    }
                }})
            }}
        )
        result = self.test_text.transform(
            variant_config=variant_config, meta_config=meta_config)
        expected_result = self.test_text.text
        self.assertNotEqual(expected_result, result)


if __name__ == "__main__":
    unittest.main()
