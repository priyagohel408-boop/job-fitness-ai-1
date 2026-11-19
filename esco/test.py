# ============================================================
# JOB FITNESS AI - O*NET CAREER TEST
# ============================================================

import requests

API_KEY = "ZdA1W-9KsWt-9q5LV-tMkDf"

BASE_URL = "https://api-v2.onetcenter.org"

HEADERS = {
    "X-API-Key": API_KEY
}

CAREERS = [
    "AI Engineer",
    "Machine Learning Engineer",
    "Data Scientist",
    "Data Analyst",
    "AR/VR Engineer",
    "Software Developer",
    "Python Developer",
    "Cloud Engineer",
    "DevOps Engineer",
    "Cybersecurity Analyst",
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "UI/UX Designer",
    "Database Administrator"
]

for career in CAREERS:
    url = f"{BASE_URL}/online/search"
    params = {
        "keyword": career,
        "start": 1,
        "end": 5
    }

    response = requests.get(url, headers=HEADERS, params=params, timeout=20)

    print("\n" + "=" * 60)
    print("SEARCH:", career)
    print("=" * 60)

    if response.status_code != 200:
        print("ERROR:", response.status_code)
        continue

    data = response.json()
    occupations = data.get("occupation", [])

    if not occupations:
        print("No occupation found.")
        continue

    for i, occupation in enumerate(occupations, 1):
        print(f"{i}. {occupation['title']}")
        print(f"   Code: {occupation['code']}")