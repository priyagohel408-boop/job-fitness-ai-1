# ============================================================
# JOB FITNESS AI
# STEP 4 - RANDOM FOREST MODEL TRAINING
# ============================================================

import os
import joblib
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay
)


# ============================================================
# 1. FILE PATH
# ============================================================

MODEL_FOLDER = "models"


# ============================================================
# 2. LOAD PREPROCESSED DATA
# ============================================================

print("==========================================")
print("JOB FITNESS AI - STEP 4")
print("==========================================")

print("\nLoading preprocessed data...")


X_train = joblib.load(
    os.path.join(
        MODEL_FOLDER,
        "X_train.pkl"
    )
)

X_test = joblib.load(
    os.path.join(
        MODEL_FOLDER,
        "X_test.pkl"
    )
)

y_train = joblib.load(
    os.path.join(
        MODEL_FOLDER,
        "y_train.pkl"
    )
)

y_test = joblib.load(
    os.path.join(
         MODEL_FOLDER,       
      "y_test.pkl"
    )
)


print("Data loaded successfully!")


# ============================================================
# 3. DISPLAY DATA INFORMATION
# ============================================================

print("\n==========================================")
print("DATA INFORMATION")
print("==========================================")

print(
    "X_train Shape:",
    X_train.shape
)

print(
    "X_test Shape:",
    X_test.shape
)

print(
    "y_train Shape:",
    y_train.shape
)

print(
    "y_test Shape:",
    y_test.shape
)


# ============================================================
# 4. CHECK CAREER DISTRIBUTION
# ============================================================

print("\n==========================================")
print("CAREER DISTRIBUTION")
print("==========================================")

print("\nTraining Data:")

print(
    y_train.value_counts()
)


print(
    "\nNumber of Career Classes:",
    y_train.nunique()
)


# ============================================================
# 5. CREATE RANDOM FOREST MODEL
# ============================================================

print("\n==========================================")
print("CREATING RANDOM FOREST MODEL")
print("==========================================")


model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)


print(
    "Random Forest model created successfully!"
)


# ============================================================
# 6. TRAIN MODEL
# ============================================================

print("\n==========================================")
print("MODEL TRAINING")
print("==========================================")


model.fit(
    X_train,
    y_train
)


print(
    "Random Forest training completed!"
)


# ============================================================
# 7. MAKE PREDICTIONS
# ============================================================

print("\n==========================================")
print("MAKING PREDICTIONS")
print("==========================================")


y_pred = model.predict(
    X_test
)


print(
    "Predictions generated successfully!"
)


# ============================================================
# 8. CALCULATE ACCURACY
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)


print("\n==========================================")
print("MODEL ACCURACY")
print("==========================================")


print(
    "Accuracy:",
    accuracy
)


print(
    "Accuracy Percentage:",
    round(
        accuracy * 100,
        2
    ),
    "%"
)


# ============================================================
# 9. CLASSIFICATION REPORT
# ============================================================

print("\n==========================================")
print("CLASSIFICATION REPORT")
print("==========================================")


print(
    classification_report(
        y_test,
        y_pred,
        zero_division=0
    )
)


# ============================================================
# 10. CONFUSION MATRIX
# ============================================================

print("\n==========================================")
print("CONFUSION MATRIX")
print("==========================================")


cm = confusion_matrix(
    y_test,
    y_pred
)


print(cm)


# ============================================================
# 11. CONFUSION MATRIX GRAPH
# ============================================================

plt.figure(
    figsize=(12, 8)
)


ConfusionMatrixDisplay.from_predictions(
    y_test,
    y_pred,
    xticks_rotation=45
)


plt.title(
    "Random Forest - Career Prediction Confusion Matrix"
)


plt.tight_layout()


plt.show()


# ============================================================
# 12. FEATURE IMPORTANCE
# ============================================================

print("\n==========================================")
print("FEATURE IMPORTANCE")
print("==========================================")


feature_importances = (
    model.feature_importances_
)


print(
    "Total Feature Importances:",
    len(feature_importances)
)


# Display top 20 important features

top_features = sorted(
    enumerate(feature_importances),
    key=lambda x: x[1],
    reverse=True
)


print("\nTop 20 Important Features:")


for index, importance in top_features[:20]:

    print(
        "Feature",
        index,
        "Importance:",
        round(
            importance,
            4
        )
    )


# ============================================================
# 13. SAVE TRAINED MODEL
# ============================================================

model_path = os.path.join(
    MODEL_FOLDER,
    "job_fitness_model.pkl"
)


joblib.dump(
    model,
    model_path
)


print("\n==========================================")
print("MODEL SAVED")
print("==========================================")


print(
    "Model saved at:",
    model_path
)


# ============================================================
# 14. FINAL SUMMARY
# ============================================================

print("\n==========================================")
print("STEP 4 COMPLETED SUCCESSFULLY!")
print("==========================================")


print(
    "Algorithm: Random Forest Classifier"
)


print(
    "Training Samples:",
    X_train.shape[0]
)


print(
    "Testing Samples:",
    X_test.shape[0]
)


print(
    "ML Features:",
    X_train.shape[1]
)


print(
    "Career Classes:",
    y_train.nunique()
)


print(
    "Accuracy:",
    round(
        accuracy * 100,
        2
    ),
    "%"
)


print(
    "\nSaved Model:",
    "models/job_fitness_model.pkl"
)


print(
    "\nReady for the next stage!"
)