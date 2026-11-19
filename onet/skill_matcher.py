
import re


# Common student skill names mapped to broader O*NET skill categories.
# These aliases help compare different names for the same underlying skill.
SKILL_ALIASES = {
    "programming": {
        "programming",
        "coding",
        "software programming",
        "python",
        "java",
        "c",
        "c++",
        "c#",
        "javascript",
        "typescript",
        "sql",
        "r programming",
    },
    "mathematics": {
        "mathematics",
        "math",
        "maths",
        "statistics",
        "probability",
        "linear algebra",
        "calculus",
    },
    "critical thinking": {
        "critical thinking",
        "analytical thinking",
        "logical thinking",
        "logical reasoning",
        "problem analysis",
    },
    "complex problem solving": {
        "complex problem solving",
        "problem solving",
        "troubleshooting",
        "debugging",
        "root cause analysis",
    },
    "reading comprehension": {
        "reading comprehension",
        "technical reading",
        "reading documentation",
        "understanding documentation",
    },
    "active learning": {
        "active learning",
        "self learning",
        "continuous learning",
        "learning new technologies",
    },
    "active listening": {
        "active listening",
        "listening skills",
    },
    "speaking": {
        "speaking",
        "verbal communication",
        "oral communication",
        "presentation skills",
    },
    "writing": {
        "writing",
        "technical writing",
        "documentation",
        "report writing",
    },
    "judgment and decision making": {
        "judgment and decision making",
        "decision making",
        "decision-making",
        "evaluating alternatives",
    },
    "monitoring": {
        "monitoring",
        "performance monitoring",
        "tracking performance",
    },
    "time management": {
        "time management",
        "prioritization",
        "task planning",
        "time planning",
    },
}


def normalize_skill(skill):
    """Normalize a skill label for comparison."""
    if not isinstance(skill, str):
        return ""

    skill = skill.casefold().strip()
    skill = re.sub(r"[^a-z0-9+#.]+", " ", skill)
    return re.sub(r"\s+", " ", skill).strip()


def get_skill_group(skill):
    """
    Return the O*NET skill category associated with a student skill.
    Unknown skills remain their own category and are not guessed.
    """
    normalized = normalize_skill(skill)

    if not normalized:
        return None

    for category, aliases in SKILL_ALIASES.items():
        normalized_aliases = {
            normalize_skill(alias) for alias in aliases
        }

        if normalized in normalized_aliases:
            return category

    return normalized


def calculate_skill_match(student_skills, required_skills):
    """
    Compare student skills against O*NET required skills.

    Each required O*NET skill can be matched only once.
    The score is the percentage of required skills matched.
    """

    student_skills = student_skills or []
    required_skills = required_skills or []

    # Remove blank and duplicate student entries.
    cleaned_student_skills = []
    seen_student = set()

    for skill in student_skills:
        normalized = normalize_skill(skill)

        if normalized and normalized not in seen_student:
            cleaned_student_skills.append(skill.strip())
            seen_student.add(normalized)

    # Remove duplicate required skills while preserving order.
    cleaned_required_skills = []
    seen_required = set()

    for skill in required_skills:
        normalized = normalize_skill(skill)

        if normalized and normalized not in seen_required:
            cleaned_required_skills.append(skill.strip())
            seen_required.add(normalized)

    if not cleaned_required_skills:
        return {
            "fitness_score": None,
            "matched_skills": [],
            "missing_skills": [],
            "student_skills": cleaned_student_skills,
            "required_skills": [],
            "message": (
                "No required skills were returned for this occupation. "
                "A fitness score cannot be calculated."
            ),
        }

    # Convert the student's skills to comparable categories.
    student_groups = {
        get_skill_group(skill)
        for skill in cleaned_student_skills
    }
    student_groups.discard(None)

    matched_skills = []
    missing_skills = []

    for required_skill in cleaned_required_skills:
        required_group = get_skill_group(required_skill)

        if required_group in student_groups:
            matched_skills.append(required_skill)
        else:
            missing_skills.append(required_skill)

    score = round(
        len(matched_skills) / len(cleaned_required_skills) * 100,
        2,
    )

    return {
        "fitness_score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "student_skills": cleaned_student_skills,
        "required_skills": cleaned_required_skills,
        "message": (
            "Your score shows how closely your listed skills match "
            "the selected career's O*NET skills. Use the missing "
            "skills to plan your learning."
        ),
    }
