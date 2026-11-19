# ============================================================
# JOB FITNESS AI - O*NET CAREER PIPELINE
# ============================================================

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ONET_API_KEY")
BASE_URL = "https://api-v2.onetcenter.org/online"

if not API_KEY:
    print("ERROR: ONET_API_KEY not found in .env file.")
    exit()

HEADERS = {"X-API-Key": API_KEY}


# ============================================================
# 1. SEARCH O*NET OCCUPATIONS
# ============================================================

def search_occupations(career, limit=10):
    url = f"{BASE_URL}/search"

    params = {"keyword": career}

    response = requests.get(url, headers=HEADERS, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()
    return data.get("occupation", data.get("occupations", []))[:limit]


# ============================================================
# 2. DISPLAY OCCUPATION RESULTS
# ============================================================

def display_occupations(results):
    print("\n==========================================")
    print("O*NET OCCUPATION RESULTS")
    print("==========================================")

    if not results:
        print("No O*NET occupation found.")
        return

    for i, occupation in enumerate(results, 1):
        title = occupation.get("title", "Unknown")
        code = occupation.get("code", "Unknown")
        print(f"{i}. {title} [{code}]")


# ============================================================
# 3. SELECT OCCUPATION
# ============================================================

def select_occupation(results):
    if not results:
        return None

    while True:
        try:
            choice = int(input("\nSelect occupation number: "))

            if 1 <= choice <= len(results):
                return results[choice - 1]

            print("Invalid selection. Try again.")

        except ValueError:
            print("Please enter a number.")


# ============================================================
# 4. GET OCCUPATION DETAILS
# ============================================================

def get_occupation_details(code):
    url = f"{BASE_URL}/occupations/{code}/"

    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()

    return response.json()


# ============================================================
# 5. MAIN
# ============================================================

print("\n==========================================")
print("JOB FITNESS AI - O*NET CAREER PIPELINE")
print("==========================================")

career = input("\nEnter career: ").strip()

if not career:
    print("Career cannot be empty.")
    exit()

try:
    results = search_occupations(career)

    display_occupations(results)

    selected = select_occupation(results)

    if selected is None:
        exit()

    title = selected.get("title", "Unknown")
    code = selected.get("code", "")

    print("\n==========================================")
    print("SELECTED O*NET OCCUPATION")
    print("==========================================")
    print("Career:", career)
    print("O*NET Occupation:", title)
    print("O*NET-SOC Code:", code)

    details = get_occupation_details(code)

    print("\n==========================================")
    print("O*NET OCCUPATION DETAILS")
    print("==========================================")

    print("Title:", details.get("title", title))
    print("Code:", details.get("code", code))

    print("\nO*NET occupation successfully retrieved.")

except requests.exceptions.HTTPError as error:
    print("\nO*NET API HTTP Error:", error)

except requests.exceptions.RequestException as error:
    print("\nO*NET API Connection Error:", error)

except Exception as error:
    print("\nUnexpected Error:", error)