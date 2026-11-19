
from onet.skill_matcher import calculate_skill_match

student_skills = [
    "Python",
    "SQL",
    "Mathematics",
    "Critical Thinking",
    "Data Analysis",
]

required_skills = [
    "Mathematics",
    "Critical Thinking",
    "Programming",
    "Complex Problem Solving",
]

result = calculate_skill_match(student_skills, required_skills)

print("Fitness score:", result["fitness_score"])
print("Matched:", result["matched_skills"])
print("Missing:", result["missing_skills"])
