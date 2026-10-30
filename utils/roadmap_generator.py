"""
Roadmap Generator and Progress Tracker Module
Generates personalized, tiered learning pathways (Beginner, Intermediate, Advanced)
and tracks student completion state.
"""

from datetime import datetime
from config import get_db_connection

def get_or_create_student_roadmap(student_id, career_id=None):
    """
    Fetches the curriculum roadmap for the given career (or student's top recommendation).
    Returns grouped topics across Beginner, Intermediate, and Advanced tiers,
    along with completion tracking info and statistics.
    """
    conn, db_type = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Resolve target career
        if career_id is None:
            sql_top = """
                SELECT career_id FROM recommendations 
                WHERE student_id = %s ORDER BY rank_order ASC LIMIT 1
            """ if db_type == 'mysql' else """
                SELECT career_id FROM recommendations 
                WHERE student_id = ? ORDER BY rank_order ASC LIMIT 1
            """
            cursor.execute(sql_top, (student_id,))
            top_rec = cursor.fetchone()
            if top_rec:
                career_id = top_rec['career_id']
            else:
                cursor.execute("SELECT id FROM careers ORDER BY id ASC LIMIT 1")
                first_c = cursor.fetchone()
                if first_c:
                    career_id = first_c['id']
                else:
                    return None

        # 2. Fetch career info
        sql_career = "SELECT * FROM careers WHERE id = %s" if db_type == 'mysql' else "SELECT * FROM careers WHERE id = ?"
        cursor.execute(sql_career, (career_id,))
        career = cursor.fetchone()
        if not career:
            return None

        # 3. Fetch all roadmap topics for this career
        sql_roadmaps = """
            SELECT lr.id, lr.career_id, lr.skill_id, lr.topic_name, lr.proficiency_level,
                   lr.resources_info, lr.practice_project,
                   s.skill_name, s.skill_type,
                   COALESCE(p.is_completed, 0) as is_completed,
                   p.completed_at
            FROM learning_roadmaps lr
            JOIN skills s ON lr.skill_id = s.id
            LEFT JOIN progress p ON p.roadmap_id = lr.id AND p.student_id = %s
            WHERE lr.career_id = %s
            ORDER BY 
                CASE lr.proficiency_level 
                    WHEN 'Beginner' THEN 1 
                    WHEN 'Intermediate' THEN 2 
                    WHEN 'Advanced' THEN 3 
                    ELSE 4 
                END,
                s.skill_name ASC,
                lr.id ASC
        """ if db_type == 'mysql' else """
            SELECT lr.id, lr.career_id, lr.skill_id, lr.topic_name, lr.proficiency_level,
                   lr.resources_info, lr.practice_project,
                   s.skill_name, s.skill_type,
                   COALESCE(p.is_completed, 0) as is_completed,
                   p.completed_at
            FROM learning_roadmaps lr
            JOIN skills s ON lr.skill_id = s.id
            LEFT JOIN progress p ON p.roadmap_id = lr.id AND p.student_id = ?
            WHERE lr.career_id = ?
            ORDER BY 
                CASE lr.proficiency_level 
                    WHEN 'Beginner' THEN 1 
                    WHEN 'Intermediate' THEN 2 
                    WHEN 'Advanced' THEN 3 
                    ELSE 4 
                END,
                s.skill_name ASC,
                lr.id ASC
        """
        cursor.execute(sql_roadmaps, (student_id, career_id))
        topic_rows = cursor.fetchall()

        # Group by level
        roadmap_by_level = {
            'Beginner': [],
            'Intermediate': [],
            'Advanced': []
        }

        total_topics = len(topic_rows)
        completed_topics = 0

        for r in topic_rows:
            is_comp = bool(r['is_completed'])
            if is_comp:
                completed_topics += 1

            topic_data = {
                'id': r['id'],
                'skill_name': r['skill_name'],
                'topic_name': r['topic_name'],
                'proficiency_level': r['proficiency_level'],
                'resources_info': r['resources_info'],
                'practice_project': r['practice_project'],
                'is_completed': is_comp,
                'completed_at': r['completed_at']
            }

            lvl = r['proficiency_level']
            if lvl in roadmap_by_level:
                roadmap_by_level[lvl].append(topic_data)
            else:
                roadmap_by_level.setdefault('Intermediate', []).append(topic_data)

        pending_topics = total_topics - completed_topics
        progress_percentage = round((completed_topics / total_topics * 100), 1) if total_topics > 0 else 0.0

        return {
            'career': dict(career),
            'total_topics': total_topics,
            'completed_topics': completed_topics,
            'pending_topics': pending_topics,
            'progress_percentage': progress_percentage,
            'roadmap_by_level': roadmap_by_level
        }
    finally:
        conn.close()


def toggle_topic_progress(student_id, roadmap_id):
    """
    Toggles the completion status of a roadmap topic for a student in MySQL/SQLite.
    Returns: new status (True/False)
    """
    conn, db_type = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check current status
        sql_check = "SELECT id, is_completed FROM progress WHERE student_id = %s AND roadmap_id = %s" if db_type == 'mysql' else "SELECT id, is_completed FROM progress WHERE student_id = ? AND roadmap_id = ?"
        cursor.execute(sql_check, (student_id, roadmap_id))
        row = cursor.fetchone()

        if row:
            current_status = bool(row['is_completed'])
            new_status = 0 if current_status else 1
            completed_at = datetime.now() if new_status else None

            sql_update = """
                UPDATE progress 
                SET is_completed = %s, completed_at = %s 
                WHERE student_id = %s AND roadmap_id = %s
            """ if db_type == 'mysql' else """
                UPDATE progress 
                SET is_completed = ?, completed_at = ? 
                WHERE student_id = ? AND roadmap_id = ?
            """
            cursor.execute(sql_update, (new_status, completed_at, student_id, roadmap_id))
        else:
            new_status = 1
            completed_at = datetime.now()
            sql_insert = """
                INSERT INTO progress (student_id, roadmap_id, is_completed, completed_at)
                VALUES (%s, %s, %s, %s)
            """ if db_type == 'mysql' else """
                INSERT INTO progress (student_id, roadmap_id, is_completed, completed_at)
                VALUES (?, ?, ?, ?)
            """
            cursor.execute(sql_insert, (student_id, roadmap_id, new_status, completed_at))

        conn.commit()
        return bool(new_status)
    finally:
        conn.close()
