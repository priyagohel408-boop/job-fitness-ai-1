# ============================================================
# JOB FITNESS AI
# STEP 5 - NEW STUDENT CAREER PREDICTION
# ============================================================

import os
import joblib
import pandas as pd
import numpy as np


# ============================================================
# 1. PATHS
# ============================================================

MODEL_FOLDER = "models"


# ============================================================
# 2. LOAD TRAINED MODEL AND PREPROCESSORS
# ============================================================

print("==========================================")
print("JOB FITNESS AI - STEP 5")
print("NEW STUDENT CAREER PREDICTION")
print("==========================================")


model = joblib.load(
    os.path.join(
        MODEL_FOLDER,
        "job_fitness_model.pkl"
    )
)


basic_preprocessor = joblib.load(
    os.path.join(
        MODEL_FOLDER,
        "basic_preprocessor.pkl"
    )
)


multi_label_encoders = joblib.load(
    os.path.join(
        MODEL_FOLDER,
        "multi_label_encoders.pkl"
    )
)


feature_information = joblib.load(
    os.path.join(
        MODEL_FOLDER,
        "feature_information.pkl"
    )
)


print("\nModel and preprocessors loaded successfully!")


# ============================================================
# 3. GET FEATURE INFORMATION
# ============================================================

numerical_features = (
    feature_information["numerical_features"]
)

categorical_features = (
    feature_information["categorical_features"]
)

multi_value_features = (
    feature_information["multi_value_features"]
)


print("\nNumerical Features:")
print(numerical_features)

print("\nCategorical Features:")
print(categorical_features)

print("\nMulti-value Features:")
print(multi_value_features)


# ============================================================
# 4. SAMPLE NEW STUDENT
# ============================================================
student = {

    "Age": 20,

    "Gender": "Male",

    "Education": "Diploma",

    "Degree": "Computer Engineering",

    "CGPA": 8.2,

    "Experience_Level": "Fresher",

    "Years_of_Experience": 0,

    "Programming_Languages":
        "Python, SQL",

    "Skills":
        "MySQL, NumPy, Power BI, Tableau",

    "Certifications":
        "Google Data Analytics",

    "Interest":
        "Data Science",

    "Soft_Skills":
        "Communication, Problem Solving",

    "Preferred_Work_Mode":
        "Hybrid",

    "Resume_Score": 75,

    "Coding_Test_Score": 80,

    "Interview_Score": 78
}

student_df = pd.DataFrame(
    [student]
)


print("\n==========================================")
print("NEW STUDENT DATA")
print("==========================================")

print(student_df)


# ============================================================
# 5. PROCESS BASIC FEATURES
# ============================================================

basic_input = student_df[
    numerical_features +
    categorical_features
]


X_basic = basic_preprocessor.transform(
    basic_input
)


# ============================================================
# 6. CONVERT BASIC FEATURES TO NUMPY
# ============================================================

if hasattr(X_basic, "toarray"):

    X_basic = X_basic.toarray()


# ============================================================
# 7. PROCESS MULTI-VALUE FEATURES
# ============================================================

multi_encoded_features = []


for column in multi_value_features:

    value = student_df.iloc[0][column]

    # Convert comma-separated text into list

    values = [
        item.strip()
        for item in str(value).split(",")
        if item.strip()
    ]

    encoder = multi_label_encoders[column]

    encoded = encoder.transform(
        [values]
    )

    multi_encoded_features.append(
        encoded
    )


# ============================================================
# 8. COMBINE MULTI-VALUE FEATURES
# ============================================================

if len(multi_encoded_features) > 0:

    X_multi = np.hstack(
        multi_encoded_features
    )

else:

    X_multi = np.empty(
        (1, 0)
    )


# ============================================================
# 9. COMBINE ALL FEATURES
# ============================================================

X_new = np.hstack(
    [
        X_basic,
        X_multi
    ]
)


print("\n==========================================")
print("PROCESSED STUDENT DATA")
print("==========================================")

print(
    "Processed Input Shape:",
    X_new.shape
)


# ============================================================
# 10. PREDICT CAREER
# ============================================================

prediction = model.predict(
    X_new
)


predicted_career = prediction[0]


print("\n==========================================")
print("CAREER PREDICTION")
print("==========================================")


print(
    "Recommended Career:",
    predicted_career
)


# ============================================================
# 11. GET CAREER PROBABILITIES
# ============================================================

probabilities = model.predict_proba(
    X_new
)[0]


career_classes = model.classes_


career_probabilities = list(
    zip(
        career_classes,
        probabilities
    )
)


career_probabilities.sort(
    key=lambda x: x[1],
    reverse=True
)


# ============================================================
# 12. TOP 3 CAREER RECOMMENDATIONS
# ============================================================

print("\n==========================================")
print("TOP 3 CAREER RECOMMENDATIONS")
print("==========================================")


for career, probability in career_probabilities[:3]:

    print(
        career,
        "->",
        round(
            probability * 100,
            2
        ),
        "%"
    )


# ============================================================
# 13. FINAL OUTPUT
# ============================================================

print("\n==========================================")
print("PREDICTION COMPLETED")
print("==========================================")

print(
    "Best Career:",
    predicted_career
)

print(
    "Top Alternative Careers:",
    [
        career
        for career, probability
        in career_probabilities[1:3]
    ]
)