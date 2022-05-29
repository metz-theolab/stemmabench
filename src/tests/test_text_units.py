import random
import unittest
from stemmabench.config_parser import ProbabilisticConfig
from stemmabench.textual_units.text import Text
from stemmabench.textual_units.sentence import Sentence
from stemmabench.textual_units.word import Word


class TestWord(unittest.TestCase):
    """Unit tests for the Word class.
    """

    def setUp(self):
        """Setup the unit test.
        """
        random.seed(5)
        self.test_word = Word("dog", pos="NOUN")
        self.test_word_no_synset = Word("toto")

    def test_init(self):
        """Tests that class initialization behaves as expected,
        even in the case of a capitalized or punctuated string.
        """
        self.assertEqual(self.test_word.word, "dog")
        self.assertEqual([synset.name() for synset in self.test_word.synset],
                         ['dog.n.01',
                          'frump.n.01',
                          'dog.n.03',
                          'cad.n.01',
                          'frank.n.02',
                          'pawl.n.01',
                          'andiron.n.01'])

    def test_clean(self):
        """Tests that in the case of a word tainted by punctuation,
        the cleaning behaves as expected.
        """
        self.assertEqual(Word("Rabbit.").word, "rabbit")

    def test_synonym(self):
        """Tests that returning a synonym works as expected.
        """
        self.assertEqual(self.test_word.synonym(), "frank")

    def test_no_synset(self):
        """Tests that when there is no synset, the word is always
        returned.
        """
        self.assertEqual(self.test_word_no_synset.synonym(),
                         self.test_word_no_synset.word)
        self.assertEqual(self.test_word_no_synset.hyponym(),
                         self.test_word_no_synset.word)
        self.assertEqual(self.test_word_no_synset.hypernym(),
                         self.test_word_no_synset.word)

    def test_hyponym(self):
        """Tests that returnig a hyponym works as expected when there is no
        hyponym for the word.
        """
        self.assertEqual(self.test_word.hyponym(), "Leonberg")

    def test_no_hyponym(self):
        """Tests that when there is no hyponym, the word itself is returned.
        """
        word_no_hyponym = Word("chocolate")
        self.assertEqual(word_no_hyponym.hyponym(),
                         word_no_hyponym.word)

    def test_hypernym(self):
        """Tests that returning a hypernym works as expected.
        """
        self.assertEqual(self.test_word.hypernym(), "domestic_animal")

    def test_no_hypernym(self):
        """Tests that when there is no hypernym, the word itself is returned.
        """
        word_no_hypernym = Word("behave")
        self.assertEqual(word_no_hypernym.word,
                         word_no_hypernym.hypernym())

    def test_mispell(self):
        """Tests that mispells behave as expected.
        """
        self.assertEqual(self.test_word.mispell(), "doi")

    def test_omit(self):
        """Tests that omitting a word behaves as expected.
        """
        self.assertEqual(self.test_word.omit(), "")


class TestSentence(unittest.TestCase):
    """Unit tests for the Sentence class.
    """

    def setUp(self):
        """Set up the unit tests.
        """
        random.seed(5)
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
        random.seed(15)
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
                         "But but first remember remember remember the signs.")

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
            "But but first remember remember remember the signs. "
            "Say say them to yourself when you wake in the morning and when you lie "
            "down at night and when you wake in the middle of the night."
        )

    def test_word_transform(self):
        """Tests that transforming at the word level behaves as expected.
        """


if __name__ == "__main__":
    unittest.main()
