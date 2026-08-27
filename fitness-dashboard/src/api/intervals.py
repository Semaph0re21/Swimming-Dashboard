import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("INTERVALS_API_KEY")
if not API_KEY:
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "INTERVALS_API_KEY" in st.secrets:
            API_KEY = st.secrets["INTERVALS_API_KEY"]
    except Exception:
        pass

BASE_URL = "https://intervals.icu/api/v1"


def get_activities(oldest, newest):
    """Get activities between two dates."""
    url = f"{BASE_URL}/athlete/0/activities"

    response = requests.get(
        url,
        auth=("API_KEY", API_KEY),
        params={
            "oldest": oldest,
            "newest": newest,
        },
        timeout=30,
    )

    response.raise_for_status()
    return response.json()


def get_wellness(oldest, newest):
    """Get daily wellness data between two dates."""
    url = f"{BASE_URL}/athlete/0/wellness"

    response = requests.get(
        url,
        auth=("API_KEY", API_KEY),
        params={
            "oldest": oldest,
            "newest": newest,
        },
        timeout=30,
    )

    response.raise_for_status()
    return response.json()