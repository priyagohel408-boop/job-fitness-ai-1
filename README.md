# Job Fitness AI

PHP frontend connected to the existing FastAPI backend. The Random Forest model, saved preprocessors, and O*NET client are reused. There is no student database.

## Run

From this project folder:

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app:app --reload --port 8000
```

In a second terminal:

```bat
php -S localhost:8080
```

Open http://localhost:8080

PHP needs the cURL extension (`extension=curl` in php.ini). Keep `ONET_API_KEY` in the backend `.env` file only. `.env` is gitignored.

## API used by the frontend

| Page | Method + path | Request | Response used by PHP |
|---|---|---|---|
| profile.php | POST /predict-career | StudentProfile fields listed below | `recommended_career`, optional `top_careers` |
| dream-career.php | POST /careers/search | `{"career": "..."}` | `occupations[{code,title}]` |
| dream-career.php | POST /career-skills | `{"career": "...", "occupation_code": "..."}` | `skills`, `occupation`, `description` |
| results.php Path A | POST /career-fitness | `{"career": "...", "occupation_code": "...", "selected_skills": ["..."]}` | nested `fitness.fitness_score`, `matched_skills`, `missing_skills` |
| results.php Path B | POST /assess | StudentProfile plus `career` and optional `occupation_code` | same fitness fields; may return `occupation_result.selection_required` |

StudentProfile fields: `Age` (int), `Gender`, `Education`, `Degree`, `CGPA` (0-10), `Experience_Level`, `Years_of_Experience`, `Programming_Languages` (comma-separated string), `Skills`, `Certifications`, `Interest`, `Soft_Skills`, `Preferred_Work_Mode`, `Resume_Score`, `Coding_Test_Score`, `Interview_Score`.

PHP calls FastAPI from the server, so the browser does not need CORS.

## What is not implemented

The backend does not return certifications, learning roadmaps, or essential/optional skill tiers. The results page lists unmatched O*NET skills as gaps only.
