# ============================================================
# JOB FITNESS AI - STEP 6
# CAREER SELECTION + ESCO SKILL MAPPING
# ============================================================

import requests
import json
import re

SEARCH_API = "https://ec.europa.eu/esco/api/search"
CONCEPT_API = "https://ec.europa.eu/esco/api/resource/"

# ============================================================
# 1. STUDENT-FRIENDLY CAREERS
# ============================================================

CAREERS = [
    "AI Engineer",
    "Machine Learning Engineer",
    "Data Scientist",
    "Data Analyst",
    "Software Developer",
    "Web Developer",
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "Cybersecurity Analyst",
    "Cloud Engineer",
    "DevOps Engineer",
    "Database Administrator",
    "Mobile App Developer",
    "Game Developer",
    "UI/UX Designer"
]

# ============================================================
# 2. ESCO SEARCH TERMS
# ============================================================

CAREER_SEARCH = {
    "AI Engineer": ["artificial intelligence", "machine learning"],
    "Machine Learning Engineer": ["machine learning", "artificial intelligence"],
    "Data Scientist": ["data scientist"],
    "Data Analyst": ["data analyst"],
    "Software Developer": ["software developer"],
    "Web Developer": ["web developer"],
    "Frontend Developer": ["web developer"],
    "Backend Developer": ["software developer"],
    "Full Stack Developer": ["software developer", "web developer"],
    "Cybersecurity Analyst": ["cyber security", "security analyst"],
    "Cloud Engineer": ["cloud computing", "software developer"],
    "DevOps Engineer": ["software developer"],
    "Database Administrator": ["database administrator"],
    "Mobile App Developer": ["software developer"],
    "Game Developer": ["game developer"],
    "UI/UX Designer": ["web designer", "user interface designer"]
}

# ============================================================
# 3. GET ENGLISH TEXT
# ============================================================

def get_english_text(value):
    if isinstance(value, dict):
        return value.get("en", next(iter(value.values()), ""))
    return str(value)

# ============================================================
# 4. SEARCH ESCO
# ============================================================

def search_esco(query, limit=20):
    params = {
        "text": query,
        "type": "occupation",
        "language": "en",
        "limit": limit,
        "selectedVersion": "1.2.0"
    }

    response = requests.get(SEARCH_API, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    return data.get("_embedded", {}).get("results", [])

# ============================================================
# 5. NORMALIZE TEXT
# ============================================================

def normalize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# ============================================================
# 6. CALCULATE CAREER MATCH
# ============================================================

def calculate_match(career, occupation):
    career_words = set(normalize(career).split())
    occupation_words = set(normalize(occupation).split())

    if not career_words:
        return 0

    common = career_words.intersection(occupation_words)

    return round((len(common) / len(career_words)) * 100, 2)

# ============================================================
# 7. FIND ESCO OCCUPATION
# ============================================================

def find_esco_occupation(career):
    search_terms = CAREER_SEARCH.get(career, [career])
    candidates = {}

    for term in search_terms:
        results = search_esco(term)

        for item in results:
            title = get_english_text(
                item.get("preferredLabel", "")
            )

            uri = item.get("uri", "")

            if not title or not uri:
                continue

            score = calculate_match(career, title)

            candidates[uri] = {
                "title": title,
                "uri": uri,
                "score": score
            }

    if not candidates:
        return None, []

    results = list(candidates.values())
    results.sort(key=lambda x: x["score"], reverse=True)

    return results[0], results[:10]

# ============================================================
# 8. CONVERT ESCO URI TO API RESOURCE URL
# ============================================================

def get_resource_url(uri):
    if "/occupation/" in uri:
        identifier = uri.split("/occupation/")[-1]
        return CONCEPT_API + "occupation/" + identifier

    return uri

# ============================================================
# 9. GET ESCO OCCUPATION DATA
# ============================================================

def get_occupation_data(uri):
    url = get_resource_url(uri)

    response = requests.get(
        url,
        params={
            "selectedVersion": "1.2.0"
        },
        headers={
            "Accept": "application/json"
        },
        timeout=30
    )

    if response.status_code != 200:
        print("\nESCO API returned:", response.status_code)
        print("URL:", url)
        return None

    return response.json()

# ============================================================
# 10. EXTRACT SKILL FROM RELATIONSHIP
# ============================================================

def extract_skill(relation, relationship):
    if not isinstance(relation, dict):
        return None

    skill = relation.get("skill", relation)

    if not isinstance(skill, dict):
        return None

    name = get_english_text(
        skill.get("preferredLabel", "")
    )

    uri = skill.get("uri", "")

    if not name:
        return None

    return {
        "name": name,
        "uri": uri,
        "relationship": relationship
    }

# ============================================================
# 11. GET ESCO SKILLS
# ============================================================

def get_esco_skills(occupation_uri):
    data = get_occupation_data(occupation_uri)

    if not data:
        return []

    skills = []

    essential_keys = [
        "hasEssentialSkill",
        "hasEssentialSkills"
    ]

    optional_keys = [
        "hasOptionalSkill",
        "hasOptionalSkills"
    ]

    for key in essential_keys:
        for relation in data.get(key, []):
            skill = extract_skill(
                relation,
                "Essential"
            )

            if skill:
                skills.append(skill)

    for key in optional_keys:
        for relation in data.get(key, []):
            skill = extract_skill(
                relation,
                "Optional"
            )

            if skill:
                skills.append(skill)

    unique = {}

    for skill in skills:
        key = skill["uri"] or skill["name"].lower()
        unique[key] = skill

    return list(unique.values())

# ============================================================
# 12. MAIN PROGRAM
# ============================================================

print("\n==========================================")
print("JOB FITNESS AI - STEP 6")
print("CAREER SELECTION + ESCO SKILL MAPPING")
print("==========================================")

search = input("\nSearch career: ").strip()

matches = [
    career for career in CAREERS
    if search.lower() in career.lower()
]

if not matches:
    matches = [
        career for career in CAREERS
        if any(
            word in career.lower()
            for word in search.lower().split()
        )
    ]

if not matches:
    print("\nNo matching career found.")

    print("\nAvailable Careers:")

    for i, career in enumerate(CAREERS, 1):
        print(f"{i}. {career}")

    exit()

# ============================================================
# 13. DISPLAY CAREER RESULTS
# ============================================================

print("\n==========================================")
print("CAREER RESULTS")
print("==========================================")

for i, career in enumerate(matches, 1):
    print(f"{i}. {career}")

try:
    choice = int(
        input("\nSelect career number: ")
    )
except ValueError:
    print("Invalid selection.")
    exit()

if choice < 1 or choice > len(matches):
    print("Invalid career selection.")
    exit()

selected_career = matches[choice - 1]

print("\nSelected Career:", selected_career)

# ============================================================
# 14. ESCO MAPPING
# ============================================================

print("\n==========================================")
print("ESCO CAREER MAPPING")
print("==========================================")

best_match, alternatives = find_esco_occupation(
    selected_career
)

if best_match is None:
    print("No ESCO occupation found.")
    exit()

print("ESCO Occupation:", best_match["title"])
print("Match Score:", str(best_match["score"]) + "%")
print("ESCO URI:", best_match["uri"])

# ============================================================
# 15. SHOW ALTERNATIVE ESCO OCCUPATIONS
# ============================================================

print("\nOther ESCO Matches:")

for i, item in enumerate(alternatives[:5], 1):
    print(
        f"{i}. {item['title']} "
        f"({item['score']}%)"
    )

# ============================================================
# 16. GET SKILLS
# ============================================================

print("\n==========================================")
print("ESCO SKILLS + RELATIONSHIPS")
print("==========================================")

skills = get_esco_skills(
    best_match["uri"]
)

if not skills:
    print("\nNo skills could be retrieved.")
    print("The occupation mapping worked, but")
    print("ESCO did not return skill relationships")
    print("through this response.")

    exit()

essential = [
    skill for skill in skills
    if skill["relationship"] == "Essential"
]

optional = [
    skill for skill in skills
    if skill["relationship"] == "Optional"
]

for i, skill in enumerate(skills, 1):
    print(
        f"{i}. {skill['name']} "
        f"[{skill['relationship']}]"
    )

# ============================================================
# 17. SUMMARY
# ============================================================

print("\n==========================================")
print("STEP 6 SUMMARY")
print("==========================================")

print("Student Career:", selected_career)
print("ESCO Occupation:", best_match["title"])
print("Essential Skills:", len(essential))
print("Optional Skills:", len(optional))
print("Total Skills:", len(skills))

# ============================================================
# 18. SAVE OUTPUT FOR STEP 7
# ============================================================

step6_output = {
    "student_career": selected_career,
    "esco_occupation": best_match["title"],
    "esco_uri": best_match["uri"],
    "essential_skills": essential,
    "optional_skills": optional,
    "total_skills": len(skills)
}

with open(
    "step6_output.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        step6_output,
        file,
        indent=4,
        ensure_ascii=False
    )

print("\nStep 6 completed successfully!")
print("Output saved as: step6_output.json")