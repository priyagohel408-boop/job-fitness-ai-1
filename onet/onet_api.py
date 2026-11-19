
import os
from urllib.parse import quote

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ONET_API_KEY", "").strip()
BASE_URL = "https://api-v2.onetcenter.org/online"
TIMEOUT = 25


class ONetAPIError(Exception):
    """Raised when an O*NET request cannot be completed."""


def onet_get(path, params=None):
    if not API_KEY:
        raise ONetAPIError(
            "ONET_API_KEY is missing. Add your O*NET v2 key to .env."
        )

    url = f"{BASE_URL}/{path.lstrip('/')}"

    try:
        response = requests.get(
            url,
            headers={
                "X-API-Key": API_KEY,
                "Accept": "application/json",
            },
            params=params or {},
            timeout=TIMEOUT,
        )

        if not response.ok:
            # Avoid returning credentials or lengthy server HTML.
            raise ONetAPIError(
                f"O*NET returned HTTP {response.status_code}. "
                "Check the API key, endpoint, and O*NET service status."
            )

        try:
            return response.json()
        except ValueError as exc:
            raise ONetAPIError(
                "O*NET returned a response that was not valid JSON."
            ) from exc

    except requests.Timeout as exc:
        raise ONetAPIError("O*NET request timed out.") from exc

    except requests.RequestException as exc:
        raise ONetAPIError(
            "Could not connect to O*NET. Check your internet connection."
        ) from exc


def search_occupations(career, limit=20):
    career = career.strip()

    if not career:
        return []

    data = onet_get(
        "search",
        params={
            "keyword": career,
            "start": 1,
            "end": min(max(int(limit), 1), 20),
        },
    )

    results = data.get("occupation", [])

    return [
        {
            "code": item.get("code"),
            "title": item.get("title"),
            "href": item.get("href"),
        }
        for item in results
        if item.get("code") and item.get("title")
    ]


def get_occupation(code):
    if not code:
        raise ValueError("Occupation code is required.")

    safe_code = quote(str(code), safe=".-")
    return onet_get(f"occupations/{safe_code}/")



def get_occupation_skills(code):
    """Fetch all skill records for an O*NET occupation."""
    if not code:
        raise ValueError("Occupation code is required.")

    safe_code = quote(str(code), safe=".-")
    path = f"occupations/{safe_code}/summary/skills"

    all_elements = []
    start = 1
    page_size = 20

    while True:
        data = onet_get(
            path,
            params={
                "start": start,
                "end": start + page_size - 1,
            },
        )

        elements = data.get("element", [])
        if not isinstance(elements, list):
            break

        all_elements.extend(elements)

        total = data.get("total")
        if not elements or total is None:
            break

        start += len(elements)

        if start > int(total):
            break

    return {
        "total": len(all_elements),
        "element": all_elements,
    }

def get_occupation_technology_skills(code):
    """Fetch technology skills for an O*NET occupation."""
    if not code:
        raise ValueError("Occupation code is required.")

    safe_code = quote(str(code), safe=".-")
    path = f"occupations/{safe_code}/details/technology_skills"

    data = onet_get(path)

    # Return the original response so the extraction function
    # can handle the actual O*NET response structure.
    return data
