"""Offline checks for narrowed heatmap fetching and atomic rate limiting."""

import os
import sys
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services import canonical_mapper  # noqa: E402
from services.heatmap_window import window_heatmap  # noqa: E402


def year_payload(year: int, month: int = 1, day: int = 1, count: int = 1):
    return {"data": {"months": {str(month): {str(day): {"count": count}}}}}


class HeatmapYearSelectionTests(unittest.IsolatedAsyncioTestCase):
    def test_year_view_fetches_only_that_year(self):
        self.assertEqual(list(canonical_mapper._years_for_heatmap("year", 2024)), [2024])

    def test_last_365_fetches_only_intersecting_years(self):
        today = datetime.now(timezone.utc).date()
        start = (today - timedelta(days=364)).year
        self.assertEqual(
            list(canonical_mapper._years_for_heatmap("last_365", None)),
            list(range(start, today.year + 1)),
        )

    def test_all_view_fetches_every_year(self):
        today = datetime.now(timezone.utc).date()
        self.assertEqual(
            list(canonical_mapper._years_for_heatmap("all", None)),
            list(range(canonical_mapper.FIRST_HEATMAP_YEAR, today.year + 1)),
        )

    async def test_narrowed_fetch_keeps_advertised_years(self):
        fetched = []

        async def fake_fetch(username, year):
            fetched.append(year)
            return year_payload(year)

        with patch.object(canonical_mapper, "fetch_heatmap_year", fake_fetch):
            heatmap = await canonical_mapper.build_heatmap("alice", "year", 2024)

        self.assertEqual(fetched, [2024])
        self.assertEqual({day.date[:4] for day in heatmap.dailyContributions}, {"2024"})
        self.assertGreater(len(heatmap.availableYears), 1)
        self.assertIn(2024, heatmap.availableYears)
        self.assertEqual(heatmap.availableYears, sorted(heatmap.availableYears, reverse=True))
        self.assertEqual(min(heatmap.availableYears), canonical_mapper.FIRST_HEATMAP_YEAR)

    async def test_windowing_keeps_the_advertised_years(self):
        async def fake_fetch(username, year):
            return year_payload(year)

        with patch.object(canonical_mapper, "fetch_heatmap_year", fake_fetch):
            heatmap = await canonical_mapper.build_heatmap("alice", "year", 2024)

        windowed = window_heatmap(
            heatmap, "year", 2024, available_years=heatmap.availableYears or None
        )
        self.assertEqual({day.date[:4] for day in windowed.dailyContributions}, {"2024"})
        self.assertEqual(windowed.availableYears, heatmap.availableYears)
        self.assertEqual(windowed.view, "year")
        self.assertEqual(windowed.year, 2024)


class AtomicRateLimitTests(unittest.IsolatedAsyncioTestCase):
    async def test_one_server_side_call_per_decision(self):
        from core import rate_limit

        calls = []

        async def fake_command(name, *args, **kwargs):
            calls.append((name, args))
            return [1, 42, 29]

        with patch.object(rate_limit, "command", fake_command):
            result = await rate_limit.check_rate_limit("ip:tuf:1.2.3.4", 30, 60, "ip")

        self.assertEqual(len(calls), 1, "rate limiting must not fan out into sequential commands")
        self.assertEqual(calls[0][0], "eval")
        self.assertTrue(result.allowed)
        self.assertEqual(result.limit, 30)
        self.assertEqual(result.remaining, 29)

    async def test_denied_decision_reports_backoff(self):
        from core import rate_limit

        async def fake_command(name, *args, **kwargs):
            return [0, 120, 0]

        with patch.object(rate_limit, "command", fake_command):
            result = await rate_limit.check_rate_limit("ip:tuf:1.2.3.4", 30, 60, "ip")

        self.assertFalse(result.allowed)
        self.assertEqual(result.retry_after, 120)
        self.assertEqual(result.limited_by, "ip")

    async def test_store_failure_fails_open(self):
        from core import rate_limit

        async def broken(*args, **kwargs):
            return None

        with patch.object(rate_limit, "command", broken):
            result = await rate_limit.check_rate_limit("ip:tuf:1.2.3.4", 30, 60, "ip")

        self.assertTrue(result.allowed)


if __name__ == "__main__":
    unittest.main()
