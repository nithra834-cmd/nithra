"""
Skill Analyzer Module
Performs comprehensive gap analysis between a student's assessed skill levels
and the industry benchmark required for any target career path.
"""

from config import get_db_connection

def analyze_skill_gap(student_id, career_id=None):
    """
    Computes detailed skill gap metrics for a student against a specific career.
    If career_id is None, it targets the student's #1 top recommended career.
    
    Returns a dictionary:
    {
        'career': {'id': 1, 'title': 'Data Analyst', ...},
        'overall_match_score': 78.5,
        'overall_gap_score': 21.5,
        'total_benchmarks': 7,
        'meeting_count': 4,
        'weak_count': 2,
        'missing_count': 1,
        'skill_comparisons': [
            {
                'skill_id': 1,
                'skill_name': 'Python',
                'skill_type': 'technical',
                'current_level': 2,
                'required_level': 3,
                'gap': 1,
                'status': 'Weak', # 'Proficient', 'Weak', 'Missing'
                'importance_weight': 1.2,
                'suggestion': 'Raise proficiency from level 2 to 3 by building data automation scripts.'
            }, ...
        ],
        'chart_data': {
            'labels': ['Python', 'SQL', ...],
            'current': [2, 5, ...],
            'required': [3, 5, ...]
        }
    }
    """
    conn, db_type = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Determine career if not supplied
        if career_id is None:
            # Query top recommendation
            sql_top = """
                SELECT r.career_id 
                FROM recommendations r 
                WHERE r.student_id = %s 
                ORDER BY r.rank_order ASC LIMIT 1
            """ if db_type == 'mysql' else """
                SELECT r.career_id 
                FROM recommendations r 
                WHERE r.student_id = ? 
                ORDER BY r.rank_order ASC LIMIT 1
            """
            cursor.execute(sql_top, (student_id,))
            top_rec = cursor.fetchone()
            if top_rec:
                career_id = top_rec['career_id']
            else:
                # Fallback to first career in DB
                cursor.execute("SELECT id FROM careers ORDER BY id ASC LIMIT 1")
                first_c = cursor.fetchone()
                if first_c:
                    career_id = first_c['id']
                else:
                    return None

        # 2. Fetch career details
        sql_career = "SELECT * FROM careers WHERE id = %s" if db_type == 'mysql' else "SELECT * FROM careers WHERE id = ?"
        cursor.execute(sql_career, (career_id,))
        career = cursor.fetchone()
        if not career:
            return None

        # 3. Fetch career required skills
        sql_benchmarks = """
            SELECT cs.skill_id, cs.required_level, cs.importance_weight, s.skill_name, s.skill_type, s.description
            FROM career_skills cs
            JOIN skills s ON cs.skill_id = s.id
            WHERE cs.career_id = %s
            ORDER BY cs.importance_weight DESC, cs.required_level DESC
        """ if db_type == 'mysql' else """
            SELECT cs.skill_id, cs.required_level, cs.importance_weight, s.skill_name, s.skill_type, s.description
            FROM career_skills cs
            JOIN skills s ON cs.skill_id = s.id
            WHERE cs.career_id = ?
            ORDER BY cs.importance_weight DESC, cs.required_level DESC
        """
        cursor.execute(sql_benchmarks, (career_id,))
        benchmarks = cursor.fetchall()

        # 4. Fetch student's current skill ratings
        sql_student_skills = """
            SELECT skill_id, rating 
            FROM student_skills 
            WHERE student_id = %s
        """ if db_type == 'mysql' else """
            SELECT skill_id, rating 
            FROM student_skills 
            WHERE student_id = ?
        """
        cursor.execute(sql_student_skills, (student_id,))
        student_skills = {row['skill_id']: row['rating'] for row in cursor.fetchall()}

        # 5. Calculate gaps and compile metrics
        skill_comparisons = []
        labels = []
        current_series = []
        required_series = []

        total_weighted_required = 0.0
        total_weighted_current = 0.0
        meeting_count = 0
        weak_count = 0
        missing_count = 0

        for b in benchmarks:
            s_id = b['skill_id']
            s_name = b['skill_name']
            s_type = b['skill_type']
            req_lvl = b['required_level']
            weight = float(b['importance_weight'] or 1.0)
            
            cur_lvl = student_skills.get(s_id, 0)
            gap = max(0, req_lvl - cur_lvl)

            total_weighted_required += (req_lvl * weight)
            total_weighted_current += (min(cur_lvl, req_lvl) * weight)

            if cur_lvl == 0 or cur_lvl <= 1:
                status = 'Missing'
                missing_count += 1
                suggestion = f"Critical foundation missing. Start with Beginner concepts in {s_name} to build baseline competency."
            elif cur_lvl < req_lvl:
                status = 'Weak'
                weak_count += 1
                suggestion = f"Moderate gap of {gap} level(s). Complete intermediate hands-on projects to reach industry standard of {req_lvl}/5."
            else:
                status = 'Proficient'
                meeting_count += 1
                suggestion = f"Benchmark achieved! Keep your {s_name} edge sharp with advanced real-world portfolio projects."

            skill_comparisons.append({
                'skill_id': s_id,
                'skill_name': s_name,
                'skill_type': s_type,
                'current_level': cur_lvl,
                'required_level': req_lvl,
                'gap': gap,
                'status': status,
                'importance_weight': weight,
                'suggestion': suggestion
            })

            labels.append(s_name)
            current_series.append(cur_lvl)
            required_series.append(req_lvl)

        # Match score calculation
        if total_weighted_required > 0:
            match_percentage = round((total_weighted_current / total_weighted_required) * 100, 1)
        else:
            match_percentage = 0.0

        gap_percentage = round(100.0 - match_percentage, 1)

        return {
            'career': dict(career),
            'overall_match_score': match_percentage,
            'overall_gap_score': gap_percentage,
            'total_benchmarks': len(benchmarks),
            'meeting_count': meeting_count,
            'weak_count': weak_count,
            'missing_count': missing_count,
            'skill_comparisons': skill_comparisons,
            'chart_data': {
                'labels': labels,
                'current': current_series,
                'required': required_series
            }
        }
    finally:
        conn.close()
