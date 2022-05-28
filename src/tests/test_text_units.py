import random
import unittest

from stemmabench.textual_units.word import Word


class TestWord(unittest.TestCase):
    """Unit tests for the Word class.
    """

    def setUp(self):
        """Setup the unit test.
        """
        random.seed(5)
        self.test_word = Word("dog")
        self.test_word_single_synset = Word("below", pos="NA")

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

    def test_no_synonym(self):
        """Tests that when there is no synonym, the word itself is returned.
        """

    def test_hyponym(self):
        """Tests that returnig a hyponym works as expected when there is no
        hyponym for the word.
        """
        self.assertEqual(self.test_word.hyponym(), "Leonberg")

    def test_no_hyponym(self):
        """Tests that when there is no hyponym, the word itself is returned.
        """

    def test_hypernym(self):
        """Tests that returning a hypernym works as expected.
        """
        self.assertEqual(self.test_word.hypernym(), "domestic_animal")

    def test_no_hypernym(self):
        """Tests that when there is no hypernym, the word itself is returned.
        """

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


class TestText(unittest.TestCase):
    """Unit tests for the Text class.
    """


if __name__ == "__main__":
    unittest.main()
