"""
Flask Application Core
AI-Powered Skill Gap Analyzer & Career Path Recommendation System
"""

import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config, get_db_connection, get_db_status, init_sqlite_if_needed
from utils.prediction import predict_top_careers, update_student_recommendations
from utils.skill_analyzer import analyze_skill_gap
from utils.roadmap_generator import get_or_create_student_roadmap, toggle_topic_progress

app = Flask(__name__)
app.config.from_object(Config)

# Ensure fallback DB and model directory are initialized on startup
init_sqlite_if_needed()


# =========================================================
# AUTHENTICATION HELPERS & DECORATORS
# =========================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.context_processor
def inject_global_context():
    """Injects student info and database status into all templates."""
    db_status = get_db_status()
    student = None
    if 'student_id' in session:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        try:
            sql = "SELECT id, full_name, email, college_name, department, year_of_study FROM students WHERE id = %s" if db_type == 'mysql' else "SELECT id, full_name, email, college_name, department, year_of_study FROM students WHERE id = ?"
            cursor.execute(sql, (session['student_id'],))
            student = cursor.fetchone()
        finally:
            conn.close()

    return {
        'current_student': student,
        'db_status': db_status
    }


# =========================================================
# PUBLIC ROUTES & AUTHENTICATION
# =========================================================

@app.route('/')
def index():
    """Landing Page"""
    if 'student_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Student Registration"""
    if 'student_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        college_name = request.form.get('college_name', '').strip()
        department = request.form.get('department', '').strip()
        year_of_study = request.form.get('year_of_study', '').strip()
        career_interests = request.form.get('career_interests', '').strip()

        # Validation
        if not full_name or not email or not password:
            flash('Full Name, Email, and Password are required fields.', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match. Please verify and re-enter.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')

        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        try:
            # Check duplicate email
            sql_check = "SELECT id FROM students WHERE email = %s" if db_type == 'mysql' else "SELECT id FROM students WHERE email = ?"
            cursor.execute(sql_check, (email,))
            if cursor.fetchone():
                flash('An account with this email address already exists. Please log in.', 'danger')
                return render_template('register.html')

            # Hash password and insert
            pwd_hash = generate_password_hash(password)
            sql_insert = """
                INSERT INTO students (full_name, email, password_hash, college_name, department, year_of_study, career_interests)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """ if db_type == 'mysql' else """
                INSERT INTO students (full_name, email, password_hash, college_name, department, year_of_study, career_interests)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(sql_insert, (full_name, email, pwd_hash, college_name, department, year_of_study, career_interests))
            conn.commit()

            # Retrieve inserted ID
            if db_type == 'mysql':
                student_id = cursor.lastrowid
            else:
                student_id = cursor.lastrowid

            # Set session
            session['student_id'] = student_id
            session['student_name'] = full_name
            session['student_email'] = email

            flash(f'Welcome aboard, {full_name}! Your account has been created. Start by taking your skill assessment.', 'success')
            return redirect(url_for('skills'))
        except Exception as e:
            flash(f'Registration error: {str(e)}', 'danger')
            return render_template('register.html')
        finally:
            conn.close()

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Student Login"""
    if 'student_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter both your email and password.', 'warning')
            return render_template('login.html')

        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        try:
            sql = "SELECT * FROM students WHERE email = %s" if db_type == 'mysql' else "SELECT * FROM students WHERE email = ?"
            cursor.execute(sql, (email,))
            student = cursor.fetchone()

            if student and check_password_hash(student['password_hash'], password):
                session['student_id'] = student['id']
                session['student_name'] = student['full_name']
                session['student_email'] = student['email']
                flash(f"Welcome back, {student['full_name']}!", 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email address or password. Please try again.', 'danger')
        finally:
            conn.close()

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))


# =========================================================
# STUDENT PROFILE MODULE
# =========================================================

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """View and update student profile"""
    student_id = session['student_id']
    conn, db_type = get_db_connection()
    cursor = conn.cursor()

    try:
        if request.method == 'POST':
            full_name = request.form.get('full_name', '').strip()
            college_name = request.form.get('college_name', '').strip()
            department = request.form.get('department', '').strip()
            year_of_study = request.form.get('year_of_study', '').strip()
            education_details = request.form.get('education_details', '').strip()
            career_interests = request.form.get('career_interests', '').strip()

            if not full_name:
                flash('Full Name is required.', 'danger')
            else:
                sql_update = """
                    UPDATE students 
                    SET full_name = %s, college_name = %s, department = %s, 
                        year_of_study = %s, education_details = %s, career_interests = %s
                    WHERE id = %s
                """ if db_type == 'mysql' else """
                    UPDATE students 
                    SET full_name = ?, college_name = ?, department = ?, 
                        year_of_study = ?, education_details = ?, career_interests = ?
                    WHERE id = ?
                """
                cursor.execute(sql_update, (full_name, college_name, department, year_of_study, education_details, career_interests, student_id))
                conn.commit()
                session['student_name'] = full_name
                flash('Profile updated successfully!', 'success')
                
                # Recalculate recommendations in case career interests updated
                update_student_recommendations(student_id)

        # Fetch current profile
        sql = "SELECT * FROM students WHERE id = %s" if db_type == 'mysql' else "SELECT * FROM students WHERE id = ?"
        cursor.execute(sql, (student_id,))
        student_data = cursor.fetchone()
        return render_template('profile.html', student=student_data)
    finally:
        conn.close()


# =========================================================
# SKILL ASSESSMENT MODULE
# =========================================================

@app.route('/skills', methods=['GET', 'POST'])
@login_required
def skills():
    """Skill Assessment Form (11 Technical, 4 Soft Skills rated 1-5)"""
    student_id = session['student_id']
    conn, db_type = get_db_connection()
    cursor = conn.cursor()

    try:
        if request.method == 'POST':
            # Fetch all skills from DB
            cursor.execute("SELECT id, skill_name FROM skills")
            all_skills = cursor.fetchall()

            for s in all_skills:
                skill_id = s['id']
                form_field = f"skill_{skill_id}"
                rating = request.form.get(form_field)

                if rating is not None:
                    try:
                        val = int(rating)
                        if 1 <= val <= 5:
                            # Upsert rating into student_skills
                            if db_type == 'mysql':
                                sql_upsert = """
                                    INSERT INTO student_skills (student_id, skill_id, rating)
                                    VALUES (%s, %s, %s)
                                    ON DUPLICATE KEY UPDATE rating = VALUES(rating), updated_at = CURRENT_TIMESTAMP
                                """
                                cursor.execute(sql_upsert, (student_id, skill_id, val))
                            else:
                                sql_upsert = """
                                    INSERT INTO student_skills (student_id, skill_id, rating)
                                    VALUES (?, ?, ?)
                                    ON CONFLICT(student_id, skill_id) DO UPDATE SET rating = excluded.rating, updated_at = CURRENT_TIMESTAMP
                                """
                                cursor.execute(sql_upsert, (student_id, skill_id, val))
                    except ValueError:
                        continue

            conn.commit()
            
            # Automatically invoke the Random Forest ML model to generate recommendations
            recs = update_student_recommendations(student_id)

            flash('Skill assessment saved successfully! AI career recommendations generated.', 'success')
            return redirect(url_for('recommendation'))

        # GET request: Load all skills with any previously submitted ratings
        sql_skills = """
            SELECT s.id, s.skill_name, s.skill_type, s.description, COALESCE(ss.rating, 1) as current_rating
            FROM skills s
            LEFT JOIN student_skills ss ON s.id = ss.skill_id AND ss.student_id = %s
            ORDER BY s.skill_type DESC, s.id ASC
        """ if db_type == 'mysql' else """
            SELECT s.id, s.skill_name, s.skill_type, s.description, COALESCE(ss.rating, 1) as current_rating
            FROM skills s
            LEFT JOIN student_skills ss ON s.id = ss.skill_id AND ss.student_id = ?
            ORDER BY s.skill_type DESC, s.id ASC
        """
        cursor.execute(sql_skills, (student_id,))
        skills_data = cursor.fetchall()

        tech_skills = [s for s in skills_data if s['skill_type'] == 'technical']
        soft_skills = [s for s in skills_data if s['skill_type'] == 'soft']

        return render_template('skills.html', tech_skills=tech_skills, soft_skills=soft_skills)
    finally:
        conn.close()


# =========================================================
# AI CAREER RECOMMENDATION MODULE
# =========================================================

@app.route('/recommendation')
@login_required
def recommendation():
    """Displays Top 3 AI Career Recommendations with Confidence Scores and Explanations"""
    student_id = session['student_id']
    conn, db_type = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if student has assessed skills
        sql_check = "SELECT COUNT(*) as cnt FROM student_skills WHERE student_id = %s" if db_type == 'mysql' else "SELECT COUNT(*) as cnt FROM student_skills WHERE student_id = ?"
        cursor.execute(sql_check, (student_id,))
        count_res = cursor.fetchone()
        has_assessed = (count_res['cnt'] > 0) if count_res else False

        if not has_assessed:
            flash('Please complete your skill assessment first to generate recommendations.', 'info')
            return redirect(url_for('skills'))

        # Fetch stored recommendations
        sql_recs = """
            SELECT r.id, r.career_id, r.match_score, r.rank_order, r.explanation,
                   c.career_title, c.description as career_desc, c.avg_salary, c.industry_demand
            FROM recommendations r
            JOIN careers c ON r.career_id = c.id
            WHERE r.student_id = %s
            ORDER BY r.rank_order ASC
        """ if db_type == 'mysql' else """
            SELECT r.id, r.career_id, r.match_score, r.rank_order, r.explanation,
                   c.career_title, c.description as career_desc, c.avg_salary, c.industry_demand
            FROM recommendations r
            JOIN careers c ON r.career_id = c.id
            WHERE r.student_id = ?
            ORDER BY r.rank_order ASC
        """
        cursor.execute(sql_recs, (student_id,))
        recs = cursor.fetchall()

        # If empty, generate now
        if not recs:
            update_student_recommendations(student_id)
            cursor.execute(sql_recs, (student_id,))
            recs = cursor.fetchall()

        return render_template('recommendation.html', recommendations=recs)
    finally:
        conn.close()


# =========================================================
# SKILL GAP ANALYSIS MODULE
# =========================================================

@app.route('/skill_gap')
@app.route('/skill_gap/<int:career_id>')
@login_required
def skill_gap(career_id=None):
    """Visualizes Skill Gap Analysis against a specific career"""
    student_id = session['student_id']
    
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    try:
        # Fetch all available careers for the dropdown selector
        cursor.execute("SELECT id, career_title FROM careers ORDER BY career_title ASC")
        all_careers = cursor.fetchall()
    finally:
        conn.close()

    gap_analysis = analyze_skill_gap(student_id, career_id)

    if not gap_analysis:
        flash('Please complete your skill assessment to unlock gap analysis.', 'warning')
        return redirect(url_for('skills'))

    return render_template('skill_gap.html', analysis=gap_analysis, all_careers=all_careers, selected_career_id=career_id)


# =========================================================
# PERSONALIZED LEARNING ROADMAP MODULE
# =========================================================

@app.route('/roadmap')
@app.route('/roadmap/<int:career_id>')
@login_required
def roadmap(career_id=None):
    """Personalized Learning Roadmap with Beginner, Intermediate, and Advanced topics"""
    student_id = session['student_id']

    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, career_title FROM careers ORDER BY career_title ASC")
        all_careers = cursor.fetchall()
    finally:
        conn.close()

    roadmap_data = get_or_create_student_roadmap(student_id, career_id)

    if not roadmap_data:
        flash('No roadmap topics found. Please complete your skill assessment first.', 'warning')
        return redirect(url_for('skills'))

    return render_template('roadmap.html', roadmap=roadmap_data, all_careers=all_careers, selected_career_id=career_id)


@app.route('/api/toggle_topic/<int:roadmap_id>', methods=['POST'])
@login_required
def api_toggle_topic(roadmap_id):
    """AJAX API to toggle completion status of a topic"""
    student_id = session['student_id']
    new_state = toggle_topic_progress(student_id, roadmap_id)
    
    # Resolve career_id for responsive metric calculation
    career_id = request.json.get('career_id') if request.is_json else None
    if not career_id:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        try:
            sql = "SELECT career_id FROM learning_roadmaps WHERE id = %s" if db_type == 'mysql' else "SELECT career_id FROM learning_roadmaps WHERE id = ?"
            cursor.execute(sql, (roadmap_id,))
            row = cursor.fetchone()
            if row:
                career_id = row['career_id']
        finally:
            conn.close()

    roadmap_data = get_or_create_student_roadmap(student_id, career_id)
    
    return jsonify({
        'success': True,
        'is_completed': new_state,
        'completed_topics': roadmap_data['completed_topics'] if roadmap_data else 0,
        'total_topics': roadmap_data['total_topics'] if roadmap_data else 0,
        'pending_topics': roadmap_data['pending_topics'] if roadmap_data else 0,
        'progress_percentage': roadmap_data['progress_percentage'] if roadmap_data else 0.0
    })


# =========================================================
# STUDENT DASHBOARD MODULE
# =========================================================

@app.route('/dashboard')
@login_required
def dashboard():
    """Main Student Dashboard with metrics and Chart.js visualizations"""
    student_id = session['student_id']
    conn, db_type = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Total assessed skills
        sql_cnt = "SELECT COUNT(*) as cnt FROM student_skills WHERE student_id = %s" if db_type == 'mysql' else "SELECT COUNT(*) as cnt FROM student_skills WHERE student_id = ?"
        cursor.execute(sql_cnt, (student_id,))
        total_assessed = cursor.fetchone()['cnt']

        # 2. Top recommendation
        sql_top_rec = """
            SELECT r.match_score, r.rank_order, c.id as career_id, c.career_title, c.avg_salary, c.industry_demand
            FROM recommendations r
            JOIN careers c ON r.career_id = c.id
            WHERE r.student_id = %s
            ORDER BY r.rank_order ASC LIMIT 3
        """ if db_type == 'mysql' else """
            SELECT r.match_score, r.rank_order, c.id as career_id, c.career_title, c.avg_salary, c.industry_demand
            FROM recommendations r
            JOIN careers c ON r.career_id = c.id
            WHERE r.student_id = ?
            ORDER BY r.rank_order ASC LIMIT 3
        """
        cursor.execute(sql_top_rec, (student_id,))
        top_recs = cursor.fetchall()
        top_career = top_recs[0] if top_recs else None

        # 3. Student assessed skills data for chart
        sql_skills = """
            SELECT s.skill_name, s.skill_type, ss.rating
            FROM student_skills ss
            JOIN skills s ON ss.skill_id = s.id
            WHERE ss.student_id = %s
            ORDER BY s.skill_type DESC, ss.rating DESC
        """ if db_type == 'mysql' else """
            SELECT s.skill_name, s.skill_type, ss.rating
            FROM student_skills ss
            JOIN skills s ON ss.skill_id = s.id
            WHERE ss.student_id = ?
            ORDER BY s.skill_type DESC, ss.rating DESC
        """
        cursor.execute(sql_skills, (student_id,))
        student_skills_rows = cursor.fetchall()

        skills_chart_labels = [row['skill_name'] for row in student_skills_rows]
        skills_chart_ratings = [row['rating'] for row in student_skills_rows]

        # 4. Roadmap progress metrics
        career_for_metrics = top_career['career_id'] if top_career else None
        roadmap_metrics = get_or_create_student_roadmap(student_id, career_for_metrics)

        # 5. Skill gap data for radar chart
        gap_data = analyze_skill_gap(student_id, career_for_metrics)

        return render_template(
            'dashboard.html',
            total_assessed=total_assessed,
            top_career=top_career,
            top_recs=top_recs,
            roadmap_metrics=roadmap_metrics,
            gap_data=gap_data,
            skills_chart_labels=skills_chart_labels,
            skills_chart_ratings=skills_chart_ratings
        )
    finally:
        conn.close()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
