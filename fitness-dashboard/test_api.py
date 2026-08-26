import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("INTERVALS_API_KEY")

if not api_key:
    raise RuntimeError("INTERVALS_API_KEY not found in .env")

url = "https://intervals.icu/api/v1/athlete/0/activities"

response = requests.get(
    url,
    auth=("API_KEY", api_key),
    params={
        "oldest": "2026-01-01",
        "newest": "2026-08-27",
    },
)

print("Status:", response.status_code)

if response.ok:
    activities = response.json()

    with open("activities_raw.json", "w", encoding="utf-8") as f:
        json.dump(activities, f, indent=2)

    print(f"Activities received: {len(activities)}")
    print("Saved to activities_raw.json")

else:
    print(response.text)