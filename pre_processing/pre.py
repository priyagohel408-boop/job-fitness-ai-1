# ============================================================
# JOB FITNESS AI
# STEP 3 - FINAL PREPROCESSING
# ============================================================

import os
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler,
    MultiLabelBinarizer
)
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline


# ============================================================
# 1. FILE PATHS
# ============================================================

INPUT_FILE = "career_dataset_cleaned.csv"
MODEL_FOLDER = "models"


# Create models folder if it doesn't exist
os.makedirs(MODEL_FOLDER, exist_ok=True)


# ============================================================
# 2. LOAD CLEANED DATASET
# ============================================================

df = pd.read_csv(INPUT_FILE)

print("==========================================")
print("JOB FITNESS AI - STEP 3")
print("==========================================")

print("\nDataset Loaded Successfully!")

print("Dataset Shape:", df.shape)


# ============================================================
# 3. DEFINE TARGET VARIABLE
# ============================================================

target_column = "Recommended_Job"


X = df.drop(
    target_column,
    axis=1
)

y = df[target_column]


print("\n==========================================")
print("TARGET VARIABLE")
print("==========================================")

print("Target:", target_column)

print("\nCareer Classes:")

print(y.value_counts())


# ============================================================
# 4. DEFINE NUMERICAL FEATURES
# ============================================================

numerical_features = [
    "Age",
    "CGPA",
    "Years_of_Experience",
    "Resume_Score",
    "Coding_Test_Score",
    "Interview_Score"
]


# ============================================================
# 5. DEFINE CATEGORICAL FEATURES
# ============================================================

categorical_features = [
    "Gender",
    "Education",
    "Degree",
    "Experience_Level",
    "Interest",
    "Preferred_Work_Mode"
]


# ============================================================
# 6. DEFINE MULTI-VALUE FEATURES
# ============================================================

multi_value_features = [
    "Programming_Languages",
    "Skills",
    "Certifications",
    "Soft_Skills"
]


# ============================================================
# 7. CHECK REQUIRED COLUMNS
# ============================================================

required_columns = (
    numerical_features
    + categorical_features
    + multi_value_features
    + [target_column]
)


missing_columns = [
    col
    for col in required_columns
    if col not in df.columns
]


if missing_columns:

    print("\nERROR!")

    print(
        "Missing columns:",
        missing_columns
    )

    raise ValueError(
        "Required columns are missing from dataset."
    )


print("\nAll required columns are available.")


# ============================================================
# 8. CONVERT MULTI-VALUE COLUMNS
# ============================================================
def convert_to_list(value):

    if pd.isna(value):
        return []

    value = str(value).strip()

    if value == "":
        return []

    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]


for col in multi_value_features:

    X[col] = X[col].apply(convert_to_list)


print("\nMulti-value columns converted successfully.")


# ============================================================
# 9. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print("\n==========================================")
print("TRAIN / TEST SPLIT")
print("==========================================")

print(
    "X_train:",
    X_train.shape
)

print(
    "X_test:",
    X_test.shape
)

print(
    "y_train:",
    y_train.shape
)

print(
    "y_test:",
    y_test.shape
)


# ============================================================
# 10. NUMERICAL PREPROCESSOR
# ============================================================

numerical_transformer = Pipeline(
    steps=[
        (
            "scaler",
            StandardScaler()
        )
    ]
)


# ============================================================
# 11. CATEGORICAL PREPROCESSOR
# ============================================================

categorical_transformer = Pipeline(
    steps=[
        (
            "onehot",
            OneHotEncoder(
                handle_unknown="ignore"
            )
        )
    ]
)


# ============================================================
# 12. COLUMN TRANSFORMER
# ============================================================

basic_preprocessor = ColumnTransformer(
    transformers=[

        (
            "numerical",
            numerical_transformer,
            numerical_features
        ),

        (
            "categorical",
            categorical_transformer,
            categorical_features
        )
    ],

    remainder="drop"
)


# ============================================================
# 13. FIT PREPROCESSOR ONLY ON TRAINING DATA
# ============================================================

X_train_basic = basic_preprocessor.fit_transform(
    X_train
)


X_test_basic = basic_preprocessor.transform(
    X_test
)


print("\nBasic preprocessing completed.")


# ============================================================
# 14. MULTI-VALUE FEATURE ENCODING
# ============================================================

multi_train_parts = []

multi_test_parts = []

multi_label_encoders = {}


for col in multi_value_features:

    print(
        "\nProcessing multi-value feature:",
        col
    )

    mlb = MultiLabelBinarizer()

    # Fit ONLY on training data
    train_encoded = mlb.fit_transform(
        X_train[col]
    )

    # Transform test data
    test_encoded = mlb.transform(
        X_test[col]
    )

    # Save encoder
    multi_label_encoders[col] = mlb

    # Save encoded data
    multi_train_parts.append(
        train_encoded
    )

    multi_test_parts.append(
        test_encoded
    )

    print(
        "Unique values learned:",
        len(mlb.classes_)
    )


# ============================================================
# 15. COMBINE MULTI-VALUE FEATURES
# ============================================================

X_train_multi = np.hstack(
    multi_train_parts
)


X_test_multi = np.hstack(
    multi_test_parts
)


# ============================================================
# 16. CONVERT BASIC FEATURES TO NUMPY
# ============================================================

if hasattr(
    X_train_basic,
    "toarray"
):

    X_train_basic = (
        X_train_basic.toarray()
    )


if hasattr(
    X_test_basic,
    "toarray"
):

    X_test_basic = (
        X_test_basic.toarray()
    )


# ============================================================
# 17. COMBINE ALL FEATURES
# ============================================================

X_train_processed = np.hstack(
    [
        X_train_basic,
        X_train_multi
    ]
)


X_test_processed = np.hstack(
    [
        X_test_basic,
        X_test_multi
    ]
)


# ============================================================
# 18. FINAL PREPROCESSING OUTPUT
# ============================================================

print("\n==========================================")
print("FINAL PREPROCESSING OUTPUT")
print("==========================================")

print(
    "Original X_train:",
    X_train.shape
)

print(
    "Processed X_train:",
    X_train_processed.shape
)

print(
    "Original X_test:",
    X_test.shape
)

print(
    "Processed X_test:",
    X_test_processed.shape
)

print(
    "y_train:",
    y_train.shape
)

print(
    "y_test:",
    y_test.shape
)


print(
    "\nTotal ML Features:",
    X_train_processed.shape[1]
)


# ============================================================
# 19. SAVE TRAIN / TEST DATA
# ============================================================

joblib.dump(
    X_train_processed,
    os.path.join(
        MODEL_FOLDER,
        "X_train.pkl"
    )
)


joblib.dump(
    X_test_processed,
    os.path.join(
        MODEL_FOLDER,
        "X_test.pkl"
    )
)


joblib.dump(
    y_train,
    os.path.join(
        MODEL_FOLDER,
        "y_train.pkl"
    )
)


joblib.dump(
    y_test,
    os.path.join(
        MODEL_FOLDER,
        "y_test.pkl"
    )
)


# ============================================================
# 20. SAVE BASIC PREPROCESSOR
# ============================================================

joblib.dump(
    basic_preprocessor,
    os.path.join(
        MODEL_FOLDER,
        "basic_preprocessor.pkl"
    )
)


# ============================================================
# 21. SAVE MULTI-LABEL ENCODERS
# ============================================================

joblib.dump(
    multi_label_encoders,
    os.path.join(
        MODEL_FOLDER,
        "multi_label_encoders.pkl"
    )
)


# ============================================================
# 22. SAVE FEATURE INFORMATION
# ============================================================

feature_information = {

    "numerical_features":
        numerical_features,

    "categorical_features":
        categorical_features,

    "multi_value_features":
        multi_value_features,

    "target_column":
        target_column,

    "total_features":
        X_train_processed.shape[1]
}


joblib.dump(
    feature_information,
    os.path.join(
        MODEL_FOLDER,
        "feature_information.pkl"
    )
)


# ============================================================
# 23. COMPLETION
# ============================================================

print("\n==========================================")
print("STEP 3 COMPLETED SUCCESSFULLY!")
print("==========================================")

print("\nFiles created inside models/:")

print("1. X_train.pkl")
print("2. X_test.pkl")
print("3. y_train.pkl")
print("4. y_test.pkl")
print("5. basic_preprocessor.pkl")
print("6. multi_label_encoders.pkl")
print("7. feature_information.pkl")

print("\nThese files are ready for STEP 4.")