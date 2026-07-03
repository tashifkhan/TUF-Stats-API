import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.canonical import Card, make_envelope  # noqa: E402


class SchemaTests(unittest.TestCase):
    def test_card_has_all_sections(self):
        card = Card(username="u").model_dump()
        self.assertEqual(
            set(card),
            {"platform", "username", "category", "profile", "stats", "contests", "rating", "heatmap", "badges"},
        )
        self.assertEqual(card["platform"], "tuf")
        self.assertEqual(card["category"], "dsa")

    def test_envelope_adds_canonical_data(self):
        env = make_envelope("u", Card(username="u"), legacy={"success": True, "message": "ok"})
        self.assertTrue(env["success"])
        self.assertEqual(env["platform"], "tuf")
        self.assertEqual(env["username"], "u")
        self.assertEqual(env["data"]["stats"]["totalSolved"], 0)


if __name__ == "__main__":
    unittest.main()
