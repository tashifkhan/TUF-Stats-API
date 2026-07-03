import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.canonical_mapper import heatmap_from_year_payloads, profile_from, stats_from  # noqa: E402


class MapperTests(unittest.TestCase):
    def test_stats_from_tuf_progress(self):
        stats = stats_from(
            {
                "data": {
                    "total_solved": 196,
                    "total_dsa": 1121,
                    "easy": {"total": 374, "solved": 84},
                    "medium": {"total": 477, "solved": 74},
                    "hard": {"total": 253, "solved": 38},
                }
            },
            {"data": [{"subject_name": "Arrays", "progress_count": 12}]},
        )
        self.assertEqual(stats.totalSolved, 196)
        self.assertEqual(stats.totalQuestions, 1121)
        self.assertEqual(stats.byDifficulty, {"easy": 84, "medium": 74, "hard": 38})
        self.assertEqual(stats.topicAnalysis[0].topic, "Arrays")

    def test_profile_from_tuf_profile(self):
        profile = profile_from(
            {
                "data": {
                    "personal_info": {"name": "Shaurya Rahlon", "college": "JIIT"},
                    "profile_image": {"image_url": "https://example.com/avatar.png"},
                    "social_links": {"github": "https://github.com/example"},
                }
            },
            "jimmy32",
        )
        self.assertEqual(profile.displayName, "Shaurya Rahlon")
        self.assertEqual(profile.username, "jimmy32")
        self.assertEqual(profile.institution, "JIIT")
        self.assertEqual(profile.social.github, "https://github.com/example")

    def test_heatmap_from_tuf_year_payloads(self):
        heatmap = heatmap_from_year_payloads(
            {
                2026: {
                    "data": {
                        "total": 4,
                        "months": {"1": {"22": {"dsa_sheet_checked": 1, "total": 1}}},
                    }
                }
            }
        )
        self.assertEqual(heatmap.dailyContributions[0].date, "2026-01-22")
        self.assertEqual(heatmap.dailyContributions[0].count, 1)
        self.assertEqual(heatmap.yearlyContributions[0].totalSubmissions, 1)


if __name__ == "__main__":
    unittest.main()
