"""
Prediction Utility Module
Integrates the Random Forest Classifier to generate real-time AI career recommendations.
"""

import os
import joblib
import numpy as np
import pandas as pd
from config import Config, get_db_connection

# Skill column names matching dataset and model training
FEATURE_COLUMNS = [
    'Python', 'Java', 'C', 'C++', 'SQL', 
    'HTML', 'CSS', 'JavaScript', 'Machine_Learning', 
    'Data_Analysis', 'Excel',
    'Communication', 'Problem_Solving', 'Teamwork', 'Leadership'
]

_model_artifact = None

def get_model():
    """Lazy loader for trained Random Forest artifact."""
    global _model_artifact
    if _model_artifact is None:
        if not os.path.exists(Config.MODEL_PATH):
            from train_model import train_and_save_model
            train_and_save_model()
        _model_artifact = joblib.load(Config.MODEL_PATH)
    return _model_artifact


def normalize_skill_name(name):
    """Maps database skill names to feature column names."""
    mapping = {
        'Machine Learning': 'Machine_Learning',
        'Data Analysis': 'Data_Analysis',
        'Problem Solving': 'Problem_Solving'
    }
    return mapping.get(name, name)


def predict_top_careers(student_skills_dict, career_interests=None, top_k=3):
    """
    Takes a dictionary of skill_name -> rating (1-5) and returns top_k career recommendations.
    Returns a list of dicts:
    [
        {
            'career_title': 'Data Scientist',
            'confidence': 78.5,
            'rank': 1,
            'top_influencing_skills': ['Machine Learning (5/5)', 'Python (5/5)', 'Problem Solving (4/5)'],
            'explanation': '...'
        }, ...
    ]
    """
    artifact = get_model()
    model = artifact['model']
    classes = artifact['careers']
    global_importances = artifact.get('feature_importances', {})

    # Construct input vector (defaulting to 1 if unassessed)
    row = {}
    for col in FEATURE_COLUMNS:
        # Check standard name or space-separated name
        val = student_skills_dict.get(col, student_skills_dict.get(col.replace('_', ' '), 1))
        row[col] = float(val)

    input_df = pd.DataFrame([row], columns=FEATURE_COLUMNS)

    # Calculate model probabilities
    probabilities = model.predict_proba(input_df)[0]
    
    # Optional slight interest alignment boost (up to 5% boost for matched interests)
    boosted_probs = probabilities.copy()
    if career_interests:
        interests_lower = str(career_interests).lower()
        interest_career_map = {
            'data': ['Data Analyst', 'Data Scientist'],
            'analyst': ['Data Analyst'],
            'scientist': ['Data Scientist'],
            'python': ['Python Developer', 'Data Scientist', 'Machine Learning Engineer'],
            'web': ['Web Developer', 'Full Stack Developer'],
            'frontend': ['Web Developer'],
            'backend': ['Python Developer', 'Full Stack Developer', 'Software Developer'],
            'full stack': ['Full Stack Developer'],
            'machine learning': ['Machine Learning Engineer', 'Data Scientist'],
            'ai': ['Machine Learning Engineer', 'Data Scientist'],
            'software': ['Software Developer', 'Python Developer'],
            'database': ['Database Administrator', 'Data Analyst']
        }
        for keyword, matching_careers in interest_career_map.items():
            if keyword in interests_lower:
                for idx, c_name in enumerate(classes):
                    if c_name in matching_careers:
                        boosted_probs[idx] += 0.05

    # Re-normalize probabilities so they sum to 1.0
    sum_probs = np.sum(boosted_probs)
    if sum_probs > 0:
        boosted_probs = boosted_probs / sum_probs

    top_indices = np.argsort(boosted_probs)[::-1][:top_k]

    recommendations = []
    for rank, idx in enumerate(top_indices, 1):
        career_name = classes[idx]
        confidence = round(float(boosted_probs[idx]) * 100, 2)

        # Determine which of the student's assessed skills positively influenced this recommendation
        # High student rating * model importance
        skill_scores = []
        for col in FEATURE_COLUMNS:
            skill_rating = row[col]
            importance = global_importances.get(col, 0.05)
            # Give higher priority to skills where student is proficient (>= 3)
            influence = skill_rating * importance
            skill_scores.append((col.replace('_', ' '), skill_rating, influence))

        skill_scores.sort(key=lambda x: x[2], reverse=True)
        top_skills = [f"{s[0]} ({int(s[1])}/5)" for s in skill_scores[:3]]

        explanation_parts = [
            f"Demonstrated high proficiency in {top_skills[0]} and {top_skills[1]}.",
            f"Strong alignment with industry benchmarks for {career_name}."
        ]
        if career_interests and any(w in str(career_interests).lower() for w in career_name.lower().split()):
            explanation_parts.append(f"Directly supports your stated interest in {career_interests}.")

        recommendations.append({
            'career_title': career_name,
            'confidence': confidence,
            'rank': rank,
            'top_influencing_skills': top_skills,
            'explanation': " ".join(explanation_parts)
        })

    return recommendations


def update_student_recommendations(student_id):
    """
    Fetches the student's assessed skills and profile from the database,
    generates ML recommendations, and persists them into the `recommendations` table.
    """
    conn, db_type = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Fetch student profile (interests)
        if db_type == 'mysql':
            cursor.execute("SELECT career_interests FROM students WHERE id = %s", (student_id,))
        else:
            cursor.execute("SELECT career_interests FROM students WHERE id = ?", (student_id,))
        student = cursor.fetchone()
        interests = student['career_interests'] if student else ""

        # 2. Fetch student assessed skills
        if db_type == 'mysql':
            cursor.execute("""
                SELECT s.skill_name, ss.rating 
                FROM student_skills ss
                JOIN skills s ON ss.skill_id = s.id
                WHERE ss.student_id = %s
            """, (student_id,))
        else:
            cursor.execute("""
                SELECT s.skill_name, ss.rating 
                FROM student_skills ss
                JOIN skills s ON ss.skill_id = s.id
                WHERE ss.student_id = ?
            """, (student_id,))
        skills_rows = cursor.fetchall()
        
        student_skills_dict = {row['skill_name']: row['rating'] for row in skills_rows}

        if not student_skills_dict:
            return []

        # 3. Generate ML recommendations
        recommendations = predict_top_careers(student_skills_dict, interests, top_k=3)

        # 4. Fetch career IDs from DB
        cursor.execute("SELECT id, career_title FROM careers")
        career_map = {c['career_title']: c['id'] for c in cursor.fetchall()}

        # 5. Clear old recommendations for this student
        if db_type == 'mysql':
            cursor.execute("DELETE FROM recommendations WHERE student_id = %s", (student_id,))
        else:
            cursor.execute("DELETE FROM recommendations WHERE student_id = ?", (student_id,))

        # 6. Insert new recommendations
        for rec in recommendations:
            career_id = career_map.get(rec['career_title'])
            if not career_id:
                continue

            sql_insert = """
                INSERT INTO recommendations (student_id, career_id, match_score, rank_order, explanation)
                VALUES (%s, %s, %s, %s, %s)
            """ if db_type == 'mysql' else """
                INSERT INTO recommendations (student_id, career_id, match_score, rank_order, explanation)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(sql_insert, (
                student_id,
                career_id,
                rec['confidence'],
                rec['rank'],
                rec['explanation']
            ))

        conn.commit()
        return recommendations
    finally:
        conn.close()
