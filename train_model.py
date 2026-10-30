"""
Model Training and Dataset Generation Script
AI-Powered Skill Gap Analyzer & Career Path Recommendation System
"""

import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
MODEL_DIR = os.path.join(BASE_DIR, 'model')
DATASET_PATH = os.path.join(DATASET_DIR, 'career_skills.csv')
MODEL_PATH = os.path.join(MODEL_DIR, 'career_model.pkl')

os.makedirs(DATASET_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# 15 Skill Columns (11 Technical, 4 Soft)
SKILL_COLUMNS = [
    'Python', 'Java', 'C', 'C++', 'SQL', 
    'HTML', 'CSS', 'JavaScript', 'Machine_Learning', 
    'Data_Analysis', 'Excel',
    'Communication', 'Problem_Solving', 'Teamwork', 'Leadership'
]

CAREERS = [
    'Data Analyst',
    'Data Scientist',
    'Python Developer',
    'Web Developer',
    'Full Stack Developer',
    'Machine Learning Engineer',
    'Software Developer',
    'Database Administrator'
]

# Career archetypes: (Primary strong skills, Secondary moderate skills, Typical interest)
CAREER_PROFILES = {
    'Data Analyst': {
        'strong': ['SQL', 'Data_Analysis', 'Excel', 'Communication'],
        'moderate': ['Python', 'Problem_Solving', 'Teamwork'],
        'interest': 'Data Analytics'
    },
    'Data Scientist': {
        'strong': ['Python', 'Machine_Learning', 'Data_Analysis', 'Problem_Solving'],
        'moderate': ['SQL', 'Communication', 'Excel'],
        'interest': 'Data Science'
    },
    'Python Developer': {
        'strong': ['Python', 'SQL', 'Problem_Solving'],
        'moderate': ['HTML', 'CSS', 'JavaScript', 'Teamwork'],
        'interest': 'Backend Development'
    },
    'Web Developer': {
        'strong': ['HTML', 'CSS', 'JavaScript'],
        'moderate': ['Python', 'Problem_Solving', 'Communication', 'Teamwork'],
        'interest': 'Frontend Development'
    },
    'Full Stack Developer': {
        'strong': ['HTML', 'CSS', 'JavaScript', 'Python', 'SQL'],
        'moderate': ['Problem_Solving', 'Teamwork', 'Communication'],
        'interest': 'Full Stack Development'
    },
    'Machine Learning Engineer': {
        'strong': ['Python', 'Machine_Learning', 'Data_Analysis', 'Problem_Solving'],
        'moderate': ['C++', 'SQL', 'Teamwork', 'Leadership'],
        'interest': 'AI & Machine Learning'
    },
    'Software Developer': {
        'strong': ['Java', 'C++', 'Problem_Solving', 'SQL'],
        'moderate': ['C', 'Python', 'Teamwork', 'Communication'],
        'interest': 'Software Engineering'
    },
    'Database Administrator': {
        'strong': ['SQL', 'Problem_Solving'],
        'moderate': ['Python', 'Data_Analysis', 'Excel', 'Communication', 'Teamwork'],
        'interest': 'Database Administration'
    }
}


def generate_synthetic_dataset(num_samples_per_career=250, random_seed=42):
    """
    Generates a realistic, well-distributed dataset of student skill profiles.
    Returns a pandas DataFrame.
    """
    np.random.seed(random_seed)
    records = []

    for career, profile in CAREER_PROFILES.items():
        for _ in range(num_samples_per_career):
            row = {}
            for skill in SKILL_COLUMNS:
                if skill in profile['strong']:
                    # Strong skills predominantly rated 4 or 5, occasionally 3
                    row[skill] = int(np.random.choice([3, 4, 5], p=[0.10, 0.45, 0.45]))
                elif skill in profile['moderate']:
                    # Moderate skills typically rated 2, 3, or 4
                    row[skill] = int(np.random.choice([2, 3, 4], p=[0.25, 0.50, 0.25]))
                else:
                    # Other baseline skills rated 1, 2, or 3
                    row[skill] = int(np.random.choice([1, 2, 3], p=[0.60, 0.30, 0.10]))

            row['Career_Interest'] = profile['interest']
            row['Career_Path'] = career
            records.append(row)

    df = pd.DataFrame(records)
    # Shuffle dataset
    df = df.sample(frac=1, random_state=random_seed).reset_index(drop=True)
    return df


def train_and_save_model():
    print("=" * 60)
    print("AI-POWERED SKILL GAP ANALYZER - MODEL TRAINING")
    print("=" * 60)

    # 1. Dataset Generation or Loading
    if not os.path.exists(DATASET_PATH):
        print(f"Creating career skills dataset at: {DATASET_PATH}")
        df = generate_synthetic_dataset(num_samples_per_career=300, random_seed=42)
        df.to_csv(DATASET_PATH, index=False)
        print(f"Dataset created with {len(df)} samples across {len(CAREERS)} careers.")
    else:
        print(f"Loading existing dataset from: {DATASET_PATH}")
        df = pd.read_csv(DATASET_PATH)

    print(f"Dataset shape: {df.shape}")
    print(f"Target distribution:\n{df['Career_Path'].value_counts()}")

    # 2. Features and Target
    X = df[SKILL_COLUMNS]
    y = df['Career_Path']

    # 3. Train-Test Split (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Training set: {X_train.shape[0]} samples")
    print(f"Testing set: {X_test.shape[0]} samples")

    # 4. Model Training with Random Forest Classifier
    rf_model = RandomForestClassifier(
        n_estimators=150,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    print("\nTraining Random Forest Classifier...")
    rf_model.fit(X_train, y_train)

    # 5. Model Evaluation
    y_pred = rf_model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nModel Test Accuracy: {acc * 100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    # Feature Importances
    feature_importances = dict(zip(SKILL_COLUMNS, rf_model.feature_importances_))
    sorted_importances = sorted(feature_importances.items(), key=lambda x: x[1], reverse=True)
    print("\nTop 5 Influential Skills (Global Feature Importance):")
    for skill, imp in sorted_importances[:5]:
        print(f"  - {skill}: {imp * 100:.2f}%")

    # 6. Save Model Artifact
    artifact = {
        'model': rf_model,
        'feature_columns': SKILL_COLUMNS,
        'careers': rf_model.classes_.tolist(),
        'feature_importances': feature_importances,
        'accuracy': float(acc)
    }

    joblib.dump(artifact, MODEL_PATH)
    print(f"\nModel successfully saved to: {MODEL_PATH}")

    # 7. Test Top 3 Prediction Rationale
    sample_skills = {
        'Python': 5, 'Java': 2, 'C': 1, 'C++': 1, 'SQL': 4,
        'HTML': 2, 'CSS': 1, 'JavaScript': 2, 'Machine_Learning': 5,
        'Data_Analysis': 4, 'Excel': 3,
        'Communication': 4, 'Problem_Solving': 5, 'Teamwork': 3, 'Leadership': 2
    }
    sample_df = pd.DataFrame([sample_skills])
    probs = rf_model.predict_proba(sample_df)[0]
    top_indices = np.argsort(probs)[::-1][:3]
    
    print("\nSample Student Test Prediction:")
    for rank, idx in enumerate(top_indices, 1):
        career = rf_model.classes_[idx]
        confidence = probs[idx] * 100
        print(f"  #{rank}: {career} (Confidence: {confidence:.2f}%)")
    
    print("=" * 60)


if __name__ == '__main__':
    train_and_save_model()
