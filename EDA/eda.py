# ============================================
# Job Fitness AI - Exploratory Data Analysis
# ============================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------
# 1. Load Cleaned Dataset
# --------------------------------------------

df = pd.read_csv("career_dataset_cleaned.csv")

print("Dataset Loaded Successfully!")

# --------------------------------------------
# 2. Basic Dataset Information
# --------------------------------------------

print("\n==============================")
print("DATASET SHAPE")
print("==============================")

print("Rows:", df.shape[0])
print("Columns:", df.shape[1])


print("\n==============================")
print("COLUMN NAMES")
print("==============================")

print(df.columns.tolist())


print("\n==============================")
print("DATA TYPES")
print("==============================")

print(df.dtypes)


# --------------------------------------------
# 3. First 5 Records
# --------------------------------------------

print("\n==============================")
print("FIRST 5 RECORDS")
print("==============================")

print(df.head())


# --------------------------------------------
# 4. Missing Values
# --------------------------------------------

print("\n==============================")
print("MISSING VALUES")
print("==============================")

missing_values = df.isnull().sum()

print(missing_values)

print("\nTotal Missing Values:",
      missing_values.sum())


# --------------------------------------------
# 5. Duplicate Records
# --------------------------------------------

print("\n==============================")
print("DUPLICATE RECORDS")
print("==============================")

duplicates = df.duplicated().sum()

print("Duplicate Rows:", duplicates)


# --------------------------------------------
# 6. Statistical Summary
# --------------------------------------------

print("\n==============================")
print("NUMERICAL STATISTICS")
print("==============================")

print(df.describe())


# --------------------------------------------
# 7. Unique Values
# --------------------------------------------

print("\n==============================")
print("UNIQUE VALUES")
print("==============================")

for col in df.columns:
    print("\n", col)
    print("Number of Unique Values:",
          df[col].nunique())


# --------------------------------------------
# 8. Career Distribution
# --------------------------------------------

print("\n==============================")
print("CAREER DISTRIBUTION")
print("==============================")

career_counts = df["Recommended_Job"].value_counts()

print(career_counts)


# --------------------------------------------
# 9. Career Distribution Graph
# --------------------------------------------

plt.figure(figsize=(12, 6))

career_counts.plot(kind="bar")

plt.title("Distribution of Recommended Careers")
plt.xlabel("Career")
plt.ylabel("Number of Students")

plt.xticks(rotation=45, ha="right")

plt.tight_layout()
plt.show()


# --------------------------------------------
# 10. Numerical Columns
# --------------------------------------------

numerical_columns = [
    "Age",
    "CGPA",
    "Years_of_Experience",
    "Resume_Score",
    "Coding_Test_Score",
    "Interview_Score"
]

# Keep only columns that actually exist
numerical_columns = [
    col for col in numerical_columns
    if col in df.columns
]


# --------------------------------------------
# 11. Histograms
# --------------------------------------------

for col in numerical_columns:

    plt.figure(figsize=(8, 5))

    plt.hist(df[col], bins=20)

    plt.title("Distribution of " + col)
    plt.xlabel(col)
    plt.ylabel("Frequency")

    plt.tight_layout()
    plt.show()


# --------------------------------------------
# 12. Boxplots for Numerical Columns
# --------------------------------------------

for col in numerical_columns:

    plt.figure(figsize=(8, 4))

    plt.boxplot(df[col].dropna())

    plt.title("Boxplot of " + col)
    plt.ylabel(col)

    plt.tight_layout()
    plt.show()


# --------------------------------------------
# 13. Categorical Column Analysis
# --------------------------------------------

categorical_columns = [
    "Gender",
    "Education",
    "Degree",
    "Experience",
    "Interest",
    "Prefered_work_Mode"
]

categorical_columns = [
    col for col in categorical_columns
    if col in df.columns
]


for col in categorical_columns:

    print("\n==============================")
    print(col.upper())
    print("==============================")

    print(df[col].value_counts())


# --------------------------------------------
# 14. Categorical Graphs
# --------------------------------------------

for col in categorical_columns:

    plt.figure(figsize=(10, 5))

    df[col].value_counts().plot(kind="bar")

    plt.title("Distribution of " + col)
    plt.xlabel(col)
    plt.ylabel("Number of Students")

    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()
    plt.show()


# --------------------------------------------
# 15. Correlation Analysis
# --------------------------------------------

print("\n==============================")
print("CORRELATION MATRIX")
print("==============================")

correlation = df[numerical_columns].corr()

print(correlation)


# --------------------------------------------
# 16. Correlation Heatmap
# --------------------------------------------

plt.figure(figsize=(10, 7))

plt.imshow(correlation, interpolation="nearest")

plt.title("Correlation Matrix")

plt.colorbar()

plt.xticks(
    range(len(correlation.columns)),
    correlation.columns,
    rotation=45,
    ha="right"
)

plt.yticks(
    range(len(correlation.columns)),
    correlation.columns
)

plt.tight_layout()
plt.show()


# --------------------------------------------
# 17. Average Scores by Career
# --------------------------------------------

score_columns = [
    "CGPA",
    "Resume_Score",
    "Coding_Test_Score",
    "Interview_Score"
]

score_columns = [
    col for col in score_columns
    if col in df.columns
]

career_scores = df.groupby(
    "Recommended_Job"
)[score_columns].mean()

print("\n==============================")
print("AVERAGE SCORES BY CAREER")
print("==============================")

print(career_scores)


# --------------------------------------------
# 18. Print Final EDA Summary
# --------------------------------------------

print("\n======================================")
print("EDA COMPLETED SUCCESSFULLY")
print("======================================")

print("Dataset Shape:", df.shape)

print("Total Missing Values:",
      df.isnull().sum().sum())

print("Total Duplicate Rows:",
      df.duplicated().sum())

print("Number of Careers:",
      df["Recommended_Job"].nunique())

print("EDA analysis completed.")