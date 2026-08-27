"""
Tests for cycling, walking, sleep, performance, and personal records modules.
"""
import unittest
from src.analytics.cycling import get_cycling_analytics
from src.analytics.walking import get_walking_analytics
from src.analytics.sleep import get_sleep_analytics
from src.analytics.performance import get_performance_analytics, calculate_activity_streak
from src.analytics.personal_records import calculate_all_personal_records


class TestNewAnalytics(unittest.TestCase):
    def setUp(self):
        self.mock_activities = [
            {
                "id": "1",
                "sport": "Swim",
                "name": "Pool Swim",
                "date": "2026-08-25T08:00:00",
                "distance_km": 2.0,
                "moving_time_min": 50.0,
                "avg_hr": 135,
                "max_hr": 155,
                "calories": 450,
                "training_load": 40,
            },
            {
                "id": "2",
                "sport": "Run",
                "name": "Morning Run",
                "date": "2026-08-24T07:00:00",
                "distance_km": 5.0,
                "moving_time_min": 30.0,
                "avg_hr": 150,
                "max_hr": 170,
                "calories": 400,
                "training_load": 50,
            },
            {
                "id": "3",
                "sport": "Ride",
                "name": "City Ride",
                "date": "2026-08-23T09:00:00",
                "distance_km": 20.0,
                "moving_time_min": 60.0,
                "avg_speed": 5.55,  # ~20 km/h
                "avg_hr": 130,
                "max_hr": 150,
                "elevation_m": 120.0,
                "calories": 500,
                "training_load": 45,
            },
            {
                "id": "4",
                "sport": "Walk",
                "name": "Evening Walk",
                "date": "2026-08-22T18:00:00",
                "distance_km": 3.0,
                "moving_time_min": 36.0,
                "avg_hr": 105,
                "max_hr": 120,
                "elevation_m": 15.0,
                "calories": 150,
                "total_steps": 4200,
                "training_load": 10,
            },
        ]
        self.mock_wellness = [
            {
                "id": "2026-08-25",
                "sleepSecs": 27000,
                "sleepScore": 82,
                "restingHR": 58,
                "hrv": 68.0,
                "steps": 8500,
            },
            {
                "id": "2026-08-26",
                "sleepSecs": 25200,
                "sleepScore": 75,
                "restingHR": 60,
                "hrv": 64.0,
                "steps": 6200,
            },
        ]

    def test_cycling_analytics(self):
        res = get_cycling_analytics(self.mock_activities)
        self.assertEqual(res["total_rides"], 1)
        self.assertEqual(res["total_distance_km"], 20.0)
        self.assertEqual(res["total_elevation_m"], 120.0)
        self.assertTrue(len(res["personal_bests"]) >= 1)

    def test_walking_analytics(self):
        res = get_walking_analytics(self.mock_activities)
        self.assertEqual(res["total_walks"], 1)
        self.assertEqual(res["total_distance_km"], 3.0)
        self.assertEqual(res["total_steps"], 4200)
        self.assertTrue(len(res["personal_bests"]) >= 1)

    def test_sleep_analytics(self):
        res = get_sleep_analytics(self.mock_wellness)
        self.assertEqual(res["total_days_tracked"], 2)
        self.assertAlmostEqual(res["avg_sleep_score"], 78.5)
        self.assertAlmostEqual(res["avg_resting_hr"], 59.0)

    def test_performance_analytics(self):
        res = get_performance_analytics(self.mock_activities)
        self.assertIn("Swim", res["sport_distribution"])
        self.assertIn("Run", res["sport_distribution"])
        self.assertIn("Ride", res["sport_distribution"])
        self.assertIn("Walk", res["sport_distribution"])
        self.assertTrue(len(res["weekly_multi_sport"]) >= 1)

    def test_personal_records(self):
        records = calculate_all_personal_records(self.mock_activities)
        self.assertTrue(len(records["Swimming"]) >= 1)
        self.assertTrue(len(records["Running"]) >= 1)
        self.assertTrue(len(records["Cycling"]) >= 1)
        self.assertTrue(len(records["Walking"]) >= 1)


if __name__ == "__main__":
    unittest.main()
