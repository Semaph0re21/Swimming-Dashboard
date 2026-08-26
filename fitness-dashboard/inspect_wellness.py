import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("INTERVALS_API_KEY")

url = "https://intervals.icu/api/v1/athlete/0/wellness"

response = requests.get(
    url,
    auth=("API_KEY", api_key),
    params={
        "oldest": "2026-08-01",
        "newest": "2026-08-27",
    },
)

print("Status:", response.status_code)

if response.ok:
    wellness = response.json()

    print("Wellness records:", len(wellness))

    if wellness:
        print("\nAvailable fields:")
        for key in sorted(wellness[0].keys()):
            print("-", key)

        print("\nLatest record:")
        for key, value in wellness[0].items():
            print(f"{key}: {value}")
else:
    print(response.text)