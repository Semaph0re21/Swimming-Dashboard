import unittest
from datetime import datetime
from pathlib import Path

from src.data.strava import (
    parse_strava_date,
    load_strava_activities,
    get_strava_media_path,
    find_strava_export_path,
)
from src.data.dashboard import (
    get_dashboard_data,
    merge_and_deduplicate_activities,
)


class TestStravaIntegration(unittest.TestCase):

    def test_strava_date_parsing(self):
        # Test UTC date conversion to local IST (+5:30)
        utc_date = "Aug 23, 2026, 1:18:24 PM"
        local_iso = parse_strava_date(utc_date)
        self.assertEqual(local_iso, "2026-08-23T18:48:24")

    def test_strava_activities_loaded(self):
        acts = load_strava_activities()
        self.assertGreaterEqual(len(acts), 100)
        
        # Verify first activity schema
        first = acts[0]
        self.assertIn("id", first)
        self.assertIn("sport", first)
        self.assertIn("distance_km", first)
        self.assertIn("duration_min", first)
        self.assertIn("training_load", first)

    def test_multi_sport_presence(self):
        acts = load_strava_activities()
        sports = set(a["sport"] for a in acts)
        self.assertIn("Swim", sports)
        self.assertIn("Ride", sports)
        self.assertIn("Walk", sports)
        self.assertIn("Run", sports)
        self.assertIn("Workout", sports)

    def test_media_resolution(self):
        acts = load_strava_activities()
        media_acts = [a for a in acts if a.get("media")]
        self.assertGreater(len(media_acts), 0)
        
        first_media = media_acts[0]["media"][0]
        path = get_strava_media_path(first_media)
        self.assertIsNotNone(path)
        self.assertTrue(path.exists())

    def test_dashboard_merge(self):
        data = get_dashboard_data("2025-10-01", "2026-08-27", source_filter="all")
        self.assertGreaterEqual(len(data["activities"]), 100)
        self.assertTrue(data["strava_found"])
        self.assertGreaterEqual(data["total_strava_count"], 100)
        self.assertGreaterEqual(data["strava_matched"], 40)
        self.assertGreaterEqual(data["strava_added"], 50)
        
        # Check that swim baseline extracted endurance swims
        self.assertGreaterEqual(len(data["swim_baseline"]), 20)


if __name__ == "__main__":
    unittest.main()
