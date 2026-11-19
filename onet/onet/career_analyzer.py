import os
import re
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ONET_API_KEY")
BASE_URL = "https://api-v2.onetcenter.org/online"
HEADERS = {"X-API-Key": API_KEY}

def normalize(text):
    return re.sub(r"[^a-z0-9+#.]", "", text.lower())

def search_career(career):
    url = f"{BASE_URL}/search"
    params = {"keyword": career, "start": 1, "end": 5}
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    occupations = response.json().get("occupation", [])
    return occupations

def get_professional_skills(onet_code):
    url = f"{BASE_URL}/occupations/{onet_code}/details/skills"
    params = {"start": 1, "end": 100, "sort": "importance"}
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("element", [])

def get_technical_skills(onet_code):
    url = f"{BASE_URL}/occupations/{onet_code}/summary/technology_skills"
    params = {"start": 1, "end": 100}
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    data = response.json()

    technical = []

    for category in data.get("category", []):
        technical.append(category.get("title", ""))

        for example in category.get("example", []):
            technical.append(example.get("title", ""))

        for example in category.get("example_more", []):
            technical.append(example.get("title", ""))

    return list(dict.fromkeys(skill for skill in technical if skill))

def match_skills(student_skills, required_skills):
    student_normalized = {normalize(skill): skill for skill in student_skills}
    matched = []
    missing = []

    for skill in required_skills:
        skill_key = normalize(skill)

        if skill_key in student_normalized:
            matched.append(skill)
        else:
            missing.append(skill)

    total = len(required_skills)
    score = round((len(matched) / total) * 100, 2) if total else 0

    return matched, missing, score

def analyze_career(career, student_skills):
    print("\nSearching O*NET for:", career)

    occupations = search_career(career)

    if not occupations:
        print("No O*NET occupation found.")
        return None

    occupation = occupations[0]
    onet_code = occupation["code"]
    onet_title = occupation["title"]

    print("O*NET Career:", onet_title)
    print("O*NET Code:", onet_code)

    professional_data = get_professional_skills(onet_code)
    professional_skills = [item["name"] for item in professional_data]

    technical_skills = get_technical_skills(onet_code)

    matched_professional, missing_professional, professional_score = match_skills(
        student_skills, professional_skills
    )

    matched_technical, missing_technical, technical_score = match_skills(
        student_skills, technical_skills
    )

    all_required = professional_skills + technical_skills
    all_matched = matched_professional + matched_technical
    overall_score = round((len(all_matched) / len(all_required)) * 100, 2) if all_required else 0

    result = {
        "career": career,
        "onet_title": onet_title,
        "onet_code": onet_code,
        "student_skills": student_skills,
        "professional_skills": professional_skills,
        "technical_skills": technical_skills,
        "matched_professional": matched_professional,
        "missing_professional": missing_professional,
        "professional_score": professional_score,
        "matched_technical": matched_technical,
        "missing_technical": missing_technical,
        "technical_score": technical_score,
        "overall_score": overall_score
    }

    return result

def print_result(result):
    print("\n" + "=" * 60)
    print("CAREER ANALYSIS")
    print("=" * 60)

    print("Career:", result["onet_title"])
    print("O*NET Code:", result["onet_code"])

    print("\nProfessional Skills Match:", result["professional_score"], "%")
    print("Matched:", ", ".join(result["matched_professional"]) or "None")
    print("Missing:", ", ".join(result["missing_professional"]) or "None")

    print("\nTechnical Skills Match:", result["technical_score"], "%")
    print("Matched:", ", ".join(result["matched_technical"]) or "None")
    print("Missing:", ", ".join(result["missing_technical"]) or "None")

    print("\nOverall Skill Match:", result["overall_score"], "%")
    print("=" * 60)

def main():
    if not API_KEY:
        print("ERROR: ONET_API_KEY was not found in .env")
        return

    career = input("Enter the selected career: ").strip()
    skills_input = input("Enter your skills separated by commas: ").strip()

    student_skills = [skill.strip() for skill in skills_input.split(",") if skill.strip()]

    result = analyze_career(career, student_skills)

    if result:
        print_result(result)

        with open("onet/career_analysis_result.json", "w", encoding="utf-8") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

        print("\nResult saved to: onet/career_analysis_result.json")

if __name__ == "__main__":
    main()