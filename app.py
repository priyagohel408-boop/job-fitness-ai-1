import os
from pathlib import Path

from onet.skills import extract_technology_skills, filter_career_skills
import joblib
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from onet.onet_api import (
    ONetAPIError,
    get_occupation,
    get_occupation_skills,
    get_occupation_technology_skills,
)
from onet.resolver import resolve_career, get_best_occupation
from onet.skills import extract_skills, extract_technology_skills
from onet.skill_matcher import calculate_skill_match


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"

load_dotenv(BASE_DIR / ".env")

app = FastAPI(
    title="Job Fitness AI API",
    description=(
        "Career prediction, O*NET occupation search, "
        "and checklist-based skill fitness assessment."
    ),
    version="2.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Load existing saved ML artifacts (no retraining)
# ---------------------------------------------------------

try:
    model = joblib.load(MODEL_DIR / "job_fitness_model.pkl")
    basic_preprocessor = joblib.load(MODEL_DIR / "basic_preprocessor.pkl")
    multi_label_encoders = joblib.load(MODEL_DIR / "multi_label_encoders.pkl")
    feature_information = joblib.load(MODEL_DIR / "feature_information.pkl")

    numerical_features = feature_information["numerical_features"]
    categorical_features = feature_information["categorical_features"]
    multi_value_features = feature_information["multi_value_features"]
except Exception as exc:
    raise RuntimeError(
        "Could not load model artifacts from the models folder. "
        "Check filenames and feature_information.pkl."
    ) from exc


# ---------------------------------------------------------
# Request schemas
# ---------------------------------------------------------

class StudentProfile(BaseModel):
    Age: int = Field(ge=13, le=100)
    Gender: str
    Education: str
    Degree: str
    CGPA: float = Field(ge=0, le=10)
    Experience_Level: str
    Years_of_Experience: float = Field(ge=0, le=60)
    Programming_Languages: str
    Skills: str
    Certifications: str
    Interest: str
    Soft_Skills: str
    Preferred_Work_Mode: str
    Resume_Score: float = Field(ge=0, le=100)
    Coding_Test_Score: float = Field(ge=0, le=100)
    Interview_Score: float = Field(ge=0, le=100)


class CareerSearchRequest(BaseModel):
    career: str = Field(min_length=1, max_length=150)
    occupation_code: str | None = None


class FitnessRequest(BaseModel):
    career: str = Field(min_length=1, max_length=150)
    occupation_code: str | None = None
    selected_skills: list[str] = Field(default_factory=list)


class AssessmentRequest(StudentProfile):
    career: str | None = Field(default=None, max_length=150)
    occupation_code: str | None = None
    # None means use skills from the profile; [] means checklist submitted with none checked.
    selected_skills: list[str] | None = None


# ---------------------------------------------------------
# ML prediction
# ---------------------------------------------------------

def prepare_model_input(profile):
    """Apply the same saved preprocessing sequence used by the project."""
    row = profile.model_dump()

    basic_columns = numerical_features + categorical_features
    basic_frame = pd.DataFrame(
        [{column: row[column] for column in basic_columns}],
        columns=basic_columns,
    )

    basic_matrix = basic_preprocessor.transform(basic_frame)
    if hasattr(basic_matrix, "toarray"):
        basic_matrix = basic_matrix.toarray()

    encoded_parts = [np.asarray(basic_matrix)]

    for column in multi_value_features:
        raw_value = row.get(column, "")
        values = [
            item.strip()
            for item in str(raw_value).split(",")
            if item.strip()
        ]

        encoder = multi_label_encoders[column]
        encoded = encoder.transform([values])

        if hasattr(encoded, "toarray"):
            encoded = encoded.toarray()

        encoded_parts.append(np.asarray(encoded))

    return np.hstack(encoded_parts)


def predict_careers(profile):
    X_new = prepare_model_input(profile)
    predicted = model.predict(X_new)[0]

    response = {
        "recommended_career": str(predicted),
        "top_careers": [],
    }

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(X_new)[0]
        classes = model.classes_

        ranked = sorted(
            zip(classes, probabilities),
            key=lambda item: item[1],
            reverse=True,
        )[:3]

        response["top_careers"] = [
            {
                "career": str(career),
                "model_probability": round(float(probability) * 100, 2),
            }
            for career, probability in ranked
        ]

    return response


# ---------------------------------------------------------
# O*NET helpers
# ---------------------------------------------------------

def require_occupation(career, occupation_code=None):
    try:
        occupation, resolution = get_best_occupation(
            career,
            occupation_code=occupation_code,
        )
    except ONetAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if occupation is None:
        return None, resolution

    return occupation, None


def get_skills_for_occupation(occupation):
    """Return occupation details and technology examples only."""
    code = occupation.get("code")

    if not code:
        raise HTTPException(
            status_code=502,
            detail="O*NET search result did not contain an occupation code.",
        )

    try:
        details = get_occupation(code)
        raw_technology = get_occupation_technology_skills(code)
        technical_skills = extract_technology_skills(raw_technology)

        # Keep a predictable maximum checklist size.
        technical_skills = filter_career_skills(
            technical_skills,
            limit=15,
        )

    except ONetAPIError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    return details, raw_technology, technical_skills


def collect_student_skills(profile):
    """Collect comma-separated skill-related fields from the profile."""
    fields = [
        profile.Skills,
        profile.Programming_Languages,
        profile.Certifications,
        profile.Soft_Skills,
    ]

    collected = []
    for field in fields:
        collected.extend(
            item.strip()
            for item in field.split(",")
            if item.strip()
        )

    unique = {}
    for item in collected:
        unique.setdefault(item.casefold(), item)

    return list(unique.values())


def normalize_selected_skills(selected_skills, required_skills):
    """Accept only selected labels that actually belong to this occupation."""
    lookup = {
        skill.strip().casefold(): skill
        for skill in required_skills
        if isinstance(skill, str) and skill.strip()
    }

    accepted = []
    seen = set()

    for skill in selected_skills or []:
        if not isinstance(skill, str):
            continue
        key = skill.strip().casefold()
        if key in lookup and key not in seen:
            accepted.append(lookup[key])
            seen.add(key)

    return accepted



def build_learning_roadmap(career, missing_skills):
    """Build a staged learning roadmap from the skills still missing."""

    missing_skills = [
        skill.strip()
        for skill in (missing_skills or [])
        if isinstance(skill, str) and skill.strip()
    ]

    if not missing_skills:
        return {
            "career": career,
            "status": "complete",
            "note": "No missing skills were identified by this assessment.",
            "stages": [],
        }

    # Group skills into learning stages.
    groups = {
        "foundations": [],
        "machine_learning": [],
        "data_platforms": [],
        "data_engineering": [],
        "communication": [],
        "additional_tools": [],
    }

    for skill in missing_skills:
        name = skill.casefold()

        if any(term in name for term in [
            "pandas", "numpy", "structured query language",
            "sql", "data analysis", "microsoft access",
        ]):
            groups["foundations"].append(skill)

        elif any(term in name for term in [
            "pytorch", "tensorflow", "scikit-learn",
            "machine learning",
        ]):
            groups["machine_learning"].append(skill)

        elif any(term in name for term in [
            "amazon", "aws", "redshift", "bigquery",
            "microsoft sql server", "azure", "cloud",
        ]):
            groups["data_platforms"].append(skill)

        elif any(term in name for term in [
            "pyspark", "spark", "neo4j", "database",
        ]):
            groups["data_engineering"].append(skill)

        elif any(term in name for term in [
            "powerpoint", "presentation",
        ]):
            groups["communication"].append(skill)

        else:
            groups["additional_tools"].append(skill)

    # Career-specific capstone suggestions.
    career_name = career.casefold()

    if "data scientist" in career_name or "machine learning" in career_name:
        capstone = (
            "Build a data science project: clean a dataset, explore it, "
            "train and evaluate a machine-learning model, and explain "
            "the results and limitations."
        )
    elif "data analyst" in career_name:
        capstone = (
            "Analyze a public dataset, answer business questions, "
            "and present the findings using charts or a dashboard."
        )
    elif "developer" in career_name or "software" in career_name:
        capstone = (
            "Build a small working application that demonstrates "
            "the relevant skills and document how it works."
        )
    elif "cloud" in career_name or "devops" in career_name:
        capstone = (
            "Complete a small deployment or infrastructure practice "
            "project and document the configuration and testing."
        )
    else:
        capstone = (
            "Build a small project relevant to the selected career "
            "and document the skills demonstrated."
        )

    stage_templates = [
        (
            "foundations",
            "Stage 1: Core foundations",
            "Learn and practise the basic data, programming, or database tools listed here.",
            "Complete a small exercise using sample data and record the result.",
        ),
        (
            "machine_learning",
            "Stage 2: Machine learning",
            "Study the listed machine-learning tools and understand their main purpose.",
            "Train or run a small model, then evaluate its results where applicable.",
        ),
        (
            "data_platforms",
            "Stage 3: Cloud and data platforms",
            "Learn how the listed platforms store, query, or process data.",
            "Complete a guided practice exercise and document the steps.",
        ),
        (
            "data_engineering",
            "Stage 4: Data engineering and databases",
            "Explore the listed data-processing or database technologies.",
            "Complete a small data workflow or database exercise.",
        ),
        (
            "communication",
            "Stage 5: Communicating results",
            "Practise explaining technical work and presenting findings clearly.",
            "Prepare a short presentation of your work, results, and limitations.",
        ),
        (
            "additional_tools",
            "Stage 6: Additional tools",
            "Review the remaining occupation-related technology examples one at a time.",
            "Create a small exercise or demonstration for each relevant tool.",
        ),
    ]

    stages = []

    for key, title, objective, activity in stage_templates:
        skills = groups[key]

        if not skills:
            continue

        stages.append({
            "stage": len(stages) + 1,
            "title": title,
            "skills_to_learn": skills,
            "objective": objective,
            "practice_task": activity,
        })

    return {
        "career": career,
        "status": "in_progress",
        "based_on_missing_skills": missing_skills,
        "note": (
            "This is a suggested learning sequence based on the missing "
            "O*NET technology examples. These examples are not a ranked "
            "list of mandatory job requirements. Check current job "
            "descriptions to prioritise the most relevant skills."
        ),
        "stages": stages,
        "capstone_project": capstone,
    }



def build_fitness_response(occupation, details, required_skills, selected_skills):
    checked_skills = normalize_selected_skills(
        selected_skills,
        required_skills,
    )

    checked_keys = {skill.casefold() for skill in checked_skills}

    unchecked_skills = [
        skill for skill in required_skills
        if skill.casefold() not in checked_keys
    ]

    fitness = calculate_skill_match(checked_skills, required_skills)

    career_name = (
        occupation.get("title", "Selected career")
        if isinstance(occupation, dict)
        else "Selected career"
    )

    roadmap = build_learning_roadmap(career_name, unchecked_skills)

    return {
        "matched": True,
        "occupation": occupation,
        "description": (
            details.get("description")
            if isinstance(details, dict)
            else None
        ),
        "required_skills": required_skills,
        "checked_skills": checked_skills,
        "unchecked_skills": unchecked_skills,
        "fitness": fitness,
        "learning_roadmap": roadmap,
        "message": (
            "Your score reflects the skills you checked as skills you "
            "already have. Follow the suggested roadmap to practise "
            "relevant missing skills."
        ),
    }

# ---------------------------------------------------------
# General endpoints
# ---------------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Job Fitness AI API is running.",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/careers")
def careers_info():
    return {
        "message": (
            "Enter a career title in POST /careers/search. "
            "Results come from O*NET and are not limited to a hard-coded list."
        ),
        "search_endpoint": "/careers/search",
    }


# ---------------------------------------------------------
# Dynamic O*NET career search
# ---------------------------------------------------------

@app.post("/careers/search")
def career_search(request: CareerSearchRequest):
    try:
        return resolve_career(request.career)
    except ONetAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


# ---------------------------------------------------------
# Get occupation details and checklist skills
# ---------------------------------------------------------

@app.post("/career-skills")
def career_skills(request: CareerSearchRequest):
    occupation, error_result = require_occupation(
        request.career,
        request.occupation_code,
    )

    if error_result:
        return error_result

    if occupation is None:
        return {
            "matched": False,
            "message": "Please select an occupation from the search results.",
        }

    details, raw_skills, skills = get_skills_for_occupation(occupation)

    return {
        "matched": True,
        "career_query": request.career,
        "occupation": occupation,
        "description": details.get("description") if isinstance(details, dict) else None,
        "skills": skills,
        "skills_available": bool(skills),
        "skill_extraction_note": (
            None if skills else
            "The occupation was found, but no skill names were extracted. "
            "Inspect raw_skills_response and the skill extractor."
        ),
        "raw_skills_response": raw_skills if not skills else None,
    }


# ---------------------------------------------------------
# Career fitness from checklist
# ---------------------------------------------------------

@app.post("/career-fitness")
def career_fitness(request: FitnessRequest):
    occupation, error_result = require_occupation(
        request.career,
        request.occupation_code,
    )

    if error_result:
        return error_result

    if occupation is None:
        return {
            "matched": False,
            "message": "Please select an occupation from the search results.",
        }

    details, raw_skills, required_skills = get_skills_for_occupation(occupation)

    if not required_skills:
        return {
            "matched": True,
            "occupation": occupation,
            "fitness": None,
            "message": "No required skills could be extracted from O*NET.",
            "raw_skills_response": raw_skills,
        }

    return build_fitness_response(
        occupation,
        details,
        required_skills,
        request.selected_skills,
    )


# ---------------------------------------------------------
# ML career recommendation
# ---------------------------------------------------------

@app.post("/predict-career")
def predict_career(profile: StudentProfile):
    try:
        return predict_careers(profile)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Career prediction failed. Check that the input features "
                "and saved preprocessing artifacts match the training pipeline."
            ),
        ) from exc


# ---------------------------------------------------------
# Combined assessment: selected career or ML recommendation
# ---------------------------------------------------------

@app.post("/assess")
def assess(request: AssessmentRequest):
    profile_data = request.model_dump(
        exclude={"career", "occupation_code", "selected_skills"}
    )
    profile = StudentProfile(**profile_data)

    if request.career and request.career.strip():
        selected_career = request.career.strip()
        path = "career_selected"
        prediction = None
    else:
        path = "career_predicted"
        try:
            prediction = predict_careers(profile)
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail="ML career prediction failed.",
            ) from exc
        selected_career = prediction["recommended_career"]

    occupation, error_result = require_occupation(
        selected_career,
        request.occupation_code,
    )

    if error_result:
        return {
            "path": path,
            "career": selected_career,
            "prediction": prediction,
            "occupation_result": error_result,
            "fitness": None,
        }

    if occupation is None:
        return {
            "path": path,
            "career": selected_career,
            "prediction": prediction,
            "fitness": None,
            "message": "No matching O*NET occupation was selected.",
        }

    details, raw_skills, required_skills = get_skills_for_occupation(occupation)

    if not required_skills:
        return {
            "path": path,
            "career": selected_career,
            "prediction": prediction,
            "occupation": occupation,
            "description": details.get("description") if isinstance(details, dict) else None,
            "fitness": None,
            "message": "Occupation found, but no skills could be extracted from O*NET.",
            "raw_skills_response": raw_skills,
        }

    if request.selected_skills is not None:
        # Checklist was submitted: checked skills are the only skills counted.
        student_skills = normalize_selected_skills(
            request.selected_skills,
            required_skills,
        )
    else:
        # Backward-compatible behavior for requests without a checklist.
        student_skills = collect_student_skills(profile)

    fitness = calculate_skill_match(student_skills, required_skills)
    
    matched_skills = fitness["matched_skills"]
    unchecked_skills = fitness["missing_skills"]
 
    response = {
        "path": path,
        "career": selected_career,
        "prediction": prediction,
        "occupation": occupation,
        "description": details.get("description") if isinstance(details, dict) else None,
        "student_skills_used": student_skills,
        "required_skills": required_skills,
        "checked_skills": matched_skills,
        "unchecked_skills": unchecked_skills,
        "fitness": fitness,
        "message": (
            "Your score reflects how closely your checked skills match the "
            "selected career's O*NET skill requirements. Review unchecked "
            "skills as areas to develop."
        ),
        "learning_roadmap": build_learning_roadmap(selected_career,unchecked_skills,),
    }
    return response
