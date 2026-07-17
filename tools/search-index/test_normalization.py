from __future__ import annotations

import unittest

from search_common import normalize_search_text, prefix_upper_bound


class NormalizationTests(unittest.TestCase):
    def test_latin_accents_are_folded(self):
        self.assertEqual("caffe firenze", normalize_search_text("  Caffè—FIRENZE "))

    def test_devanagari_marks_are_preserved(self):
        self.assertEqual("बेंगलुरु", normalize_search_text("बेंगलुरु"))

    def test_kannada_marks_are_preserved(self):
        self.assertEqual("ಬೆಂಗಳೂರು", normalize_search_text("ಬೆಂಗಳೂರು"))

    def test_punctuation_collapses(self):
        self.assertEqual("santa maria novella", normalize_search_text("Santa  Maria / Novella"))

    def test_prefix_successor(self):
        self.assertEqual("firs", prefix_upper_bound("firr"))
        self.assertEqual("बेंगलुरू", prefix_upper_bound("बेंगलुरु"))


if __name__ == "__main__":
    unittest.main()
