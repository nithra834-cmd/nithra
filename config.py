import os
import sqlite3
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ai-career-guidance-super-secret-key-2026')
    
    # MySQL Database Settings
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'ai_career_guidance')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    
    # SQLite Fallback File
    SQLITE_DB_PATH = os.path.join(BASE_DIR, 'ai_career_guidance.db')
    
    # Dataset and Model Paths
    DATASET_PATH = os.path.join(BASE_DIR, 'dataset', 'career_skills.csv')
    MODEL_PATH = os.path.join(BASE_DIR, 'model', 'career_model.pkl')


def get_db_connection():
    """
    Attempts to connect to MySQL first.
    If MySQL server is unavailable or fails, gracefully falls back to local SQLite database.
    Returns: (connection, db_type) where db_type is 'mysql' or 'sqlite'
    """
    # 1. Try MySQL via PyMySQL
    try:
        import pymysql
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            port=Config.MYSQL_PORT,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=2
        )
        return conn, 'mysql'
    except Exception:
        # 2. Graceful fallback to SQLite
        conn = sqlite3.connect(Config.SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn, 'sqlite'


def get_db_status():
    """Returns database type string and details for system status display."""
    conn = None
    try:
        conn, db_type = get_db_connection()
        if db_type == 'mysql':
            return {
                'type': 'MySQL',
                'name': Config.MYSQL_DB,
                'host': f"{Config.MYSQL_HOST}:{Config.MYSQL_PORT}",
                'connected': True
            }
        else:
            return {
                'type': 'SQLite (Fallback/Integrated)',
                'name': os.path.basename(Config.SQLITE_DB_PATH),
                'host': 'Local Disk',
                'connected': True
            }
    except Exception as e:
        return {
            'type': 'Unknown',
            'name': 'None',
            'host': 'Error',
            'connected': False,
            'error': str(e)
        }
    finally:
        if conn:
            conn.close()


def init_sqlite_if_needed():
    """
    Initializes SQLite schema and seed data if SQLite is used and tables don't exist yet.
    Ensures the web app functions instantly out of the box without manual SQL script execution.
    """
    conn = sqlite3.connect(Config.SQLITE_DB_PATH)
    cursor = conn.cursor()
    
    # Check if students table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='students';")
    if cursor.fetchone():
        conn.close()
        return

    # Create Tables
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        college_name TEXT,
        department TEXT,
        year_of_study TEXT,
        education_details TEXT,
        career_interests TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        skill_name TEXT NOT NULL UNIQUE,
        skill_type TEXT NOT NULL,
        description TEXT
    );

    CREATE TABLE IF NOT EXISTS student_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        skill_id INTEGER NOT NULL,
        rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
        FOREIGN KEY (skill_id) REFERENCES skills (id) ON DELETE CASCADE,
        UNIQUE (student_id, skill_id)
    );

    CREATE TABLE IF NOT EXISTS careers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        career_title TEXT NOT NULL UNIQUE,
        description TEXT NOT NULL,
        avg_salary TEXT,
        industry_demand TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS career_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        career_id INTEGER NOT NULL,
        skill_id INTEGER NOT NULL,
        required_level INTEGER NOT NULL CHECK (required_level BETWEEN 1 AND 5),
        importance_weight REAL DEFAULT 1.00,
        FOREIGN KEY (career_id) REFERENCES careers (id) ON DELETE CASCADE,
        FOREIGN KEY (skill_id) REFERENCES skills (id) ON DELETE CASCADE,
        UNIQUE (career_id, skill_id)
    );

    CREATE TABLE IF NOT EXISTS recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        career_id INTEGER NOT NULL,
        match_score REAL NOT NULL,
        rank_order INTEGER NOT NULL,
        explanation TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
        FOREIGN KEY (career_id) REFERENCES careers (id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS learning_roadmaps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        career_id INTEGER NOT NULL,
        skill_id INTEGER NOT NULL,
        topic_name TEXT NOT NULL,
        proficiency_level TEXT NOT NULL,
        resources_info TEXT NOT NULL,
        practice_project TEXT NOT NULL,
        FOREIGN KEY (career_id) REFERENCES careers (id) ON DELETE CASCADE,
        FOREIGN KEY (skill_id) REFERENCES skills (id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        roadmap_id INTEGER NOT NULL,
        is_completed INTEGER DEFAULT 0,
        completed_at TIMESTAMP DEFAULT NULL,
        FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
        FOREIGN KEY (roadmap_id) REFERENCES learning_roadmaps (id) ON DELETE CASCADE,
        UNIQUE (student_id, roadmap_id)
    );
    """)

    # Seed Skills
    cursor.executemany("""
    INSERT OR IGNORE INTO skills (id, skill_name, skill_type, description) VALUES (?, ?, ?, ?)
    """, [
        (1, 'Python', 'technical', 'High-level programming language widely used in AI, web development, data analysis, and scripting.'),
        (2, 'Java', 'technical', 'Object-oriented programming language widely used in enterprise software, Android apps, and distributed systems.'),
        (3, 'C', 'technical', 'Foundational systems programming language focusing on memory management, hardware control, and performance.'),
        (4, 'C++', 'technical', 'Powerful general-purpose language with OOP and low-level memory control used in games and high-performance apps.'),
        (5, 'SQL', 'technical', 'Standard relational database query language for data manipulation, schema definition, and reporting.'),
        (6, 'HTML', 'technical', 'HyperText Markup Language that forms the structural backbone of web pages.'),
        (7, 'CSS', 'technical', 'Cascading Style Sheets for designing, styling, and laying out responsive web pages.'),
        (8, 'JavaScript', 'technical', 'Core web scripting language enabling dynamic interactive client-side and full-stack web applications.'),
        (9, 'Machine Learning', 'technical', 'Algorithms and statistical models allowing computers to learn patterns from data and make predictions.'),
        (10, 'Data Analysis', 'technical', 'Inspecting, cleansing, transforming, and modeling data with statistical tools and visualizations to discover insights.'),
        (11, 'Excel', 'technical', 'Spreadsheet tool used for business analytics, data manipulation, pivot tables, and statistical calculations.'),
        (12, 'Communication', 'soft', 'Ability to convey technical ideas clearly in speech and writing to technical and non-technical stakeholders.'),
        (13, 'Problem Solving', 'soft', 'Analytical mindset to deconstruct complex challenges, diagnose root causes, and engineer viable solutions.'),
        (14, 'Teamwork', 'soft', 'Collaborative capacity to operate effectively within agile and cross-functional engineering teams.'),
        (15, 'Leadership', 'soft', 'Inspiring others, taking initiative, managing project delivery, and mentoring peers.')
    ])

    # Seed Careers
    cursor.executemany("""
    INSERT OR IGNORE INTO careers (id, career_title, description, avg_salary, industry_demand) VALUES (?, ?, ?, ?, ?)
    """, [
        (1, 'Data Analyst', 'Interprets complex datasets to help businesses make data-driven decisions using SQL, Excel, and visualization tools.', '$70,000 - $95,000 / yr', 'Very High'),
        (2, 'Data Scientist', 'Combines advanced statistics, machine learning, and programming to extract deep predictive insights from big data.', '$110,000 - $145,000 / yr', 'Extremely High'),
        (3, 'Python Developer', 'Designs and builds backend services, automation pipelines, APIs, and microservices using modern Python frameworks.', '$85,000 - $115,000 / yr', 'High'),
        (4, 'Web Developer', 'Develops responsive, accessible, and high-performance client-facing websites using HTML, CSS, and modern JavaScript.', '$75,000 - $100,000 / yr', 'Very High'),
        (5, 'Full Stack Developer', 'Masters both frontend interfaces and robust backend architectures, databases, and APIs for end-to-end web products.', '$95,000 - $130,000 / yr', 'Extremely High'),
        (6, 'Machine Learning Engineer', 'Researches, builds, deploys, and optimizes production-ready AI models and machine learning pipelines at scale.', '$120,000 - $160,000 / yr', 'Extremely High'),
        (7, 'Software Developer', 'Architects and engineers scalable desktop, mobile, or enterprise software applications using OOP principles and C++/Java.', '$90,000 - $125,000 / yr', 'Very High'),
        (8, 'Database Administrator', 'Maintains, secures, optimizes, and tunes mission-critical relational database systems ensuring high availability.', '$85,000 - $115,000 / yr', 'High')
    ])

    # Seed Career Skills
    career_skills = [
        # Data Analyst
        (1, 1, 3, 1.20), (1, 5, 5, 1.50), (1, 10, 5, 1.50), (1, 11, 4, 1.30), (1, 9, 2, 0.80), (1, 12, 4, 1.20), (1, 13, 4, 1.20),
        # Data Scientist
        (2, 1, 5, 1.50), (2, 5, 4, 1.20), (2, 9, 5, 1.50), (2, 10, 5, 1.50), (2, 13, 5, 1.30), (2, 12, 4, 1.10), (2, 11, 3, 0.80),
        # Python Developer
        (3, 1, 5, 1.50), (3, 5, 4, 1.30), (3, 6, 3, 0.90), (3, 7, 3, 0.90), (3, 8, 3, 1.00), (3, 13, 4, 1.20), (3, 14, 4, 1.10),
        # Web Developer
        (4, 6, 5, 1.50), (4, 7, 5, 1.50), (4, 8, 5, 1.50), (4, 1, 2, 0.80), (4, 13, 4, 1.10), (4, 12, 3, 1.00), (4, 14, 4, 1.00),
        # Full Stack Developer
        (5, 6, 5, 1.30), (5, 7, 5, 1.30), (5, 8, 5, 1.50), (5, 1, 4, 1.40), (5, 5, 4, 1.40), (5, 13, 5, 1.30), (5, 14, 4, 1.10),
        # Machine Learning Engineer
        (6, 1, 5, 1.50), (6, 9, 5, 1.50), (6, 10, 4, 1.30), (6, 4, 3, 1.00), (6, 5, 3, 1.00), (6, 13, 5, 1.40), (6, 15, 3, 1.00),
        # Software Developer
        (7, 2, 5, 1.50), (7, 4, 4, 1.30), (7, 3, 3, 1.00), (7, 5, 4, 1.20), (7, 13, 5, 1.40), (7, 14, 4, 1.20), (7, 1, 3, 1.00),
        # Database Administrator
        (8, 5, 5, 1.50), (8, 1, 3, 1.10), (8, 10, 3, 1.10), (8, 11, 3, 0.90), (8, 13, 4, 1.30), (8, 12, 3, 1.00), (8, 14, 3, 1.00)
    ]
    cursor.executemany("""
    INSERT OR IGNORE INTO career_skills (career_id, skill_id, required_level, importance_weight) VALUES (?, ?, ?, ?)
    """, career_skills)

    # Seed Roadmaps
    roadmaps = [
        # Python for Data Analyst
        (1, 1, 'Python Syntax, Data Structures & Control Flow', 'Beginner', 'Docs: docs.python.org/3/tutorial, Coursera: Python for Everybody', 'CLI Number Guessing Game & Contact Book'),
        (1, 1, 'Pandas & NumPy Data Wrangling', 'Intermediate', 'Tutorial: pandas.pydata.org/docs, Book: Python for Data Analysis by Wes McKinney', 'Automated Sales Data Cleaning & CSV Merger'),
        (1, 1, 'Exploratory Data Analysis with Matplotlib & Seaborn', 'Advanced', 'Kaggle Learn: Data Visualization, Real Python EDA Tutorials', 'Interactive Customer Segmentation Dashboard'),

        # SQL for Data Analyst
        (1, 5, 'Relational Databases & Basic Queries (SELECT, WHERE, ORDER)', 'Beginner', 'W3Schools SQL Tutorial, Mode Analytics SQL Tutorial', 'Student Records Query Database'),
        (1, 5, 'Joins, Grouping & Aggregations (INNER/LEFT JOIN, GROUP BY, HAVING)', 'Intermediate', 'SQLZoo, LeetCode SQL 50 Study Plan', 'E-commerce Orders & Customer Analytics Queries'),
        (1, 5, 'Window Functions, CTEs & Index Optimization', 'Advanced', 'Mode SQL Advanced Guide, Brent Ozar Performance Tuning', 'Monthly Churn & Rolling Revenue Analysis System'),

        # Data Analysis for Data Analyst
        (1, 10, 'Descriptive Statistics & Summary Metrics', 'Beginner', 'Khan Academy Statistics and Probability', 'Statistical Analysis of Housing Prices'),
        (1, 10, 'Hypothesis Testing & Correlation Analysis', 'Intermediate', 'Coursera: Applied Data Science with Python', 'A/B Testing Analysis for Landing Page Conversions'),
        (1, 10, 'Business Intelligence Reporting & Storytelling', 'Advanced', 'Tableau / PowerBI Guides, Storytelling with Data by Cole Nussbaumer', 'Executive Company Performance Dashboard'),

        # Excel for Data Analyst
        (1, 11, 'Formulas, VLOOKUP/XLOOKUP & Conditional Formatting', 'Beginner', 'Microsoft Excel Video Training, ExcelJet Free Guides', 'Monthly Personal Budget & Expense Tracker'),
        (1, 11, 'Pivot Tables, Slicers & Dynamic Charts', 'Intermediate', 'Chandoo.org Excel Tutorials', 'Retail Inventory & Sales Pivot Analysis'),
        (1, 11, 'Advanced Excel: Power Query, Macros & What-If Analysis', 'Advanced', 'Excel Power Query Official Guide, Leila Gharani YouTube Tutorials', 'Automated Multi-Source Financial Model'),

        # Machine Learning for Data Scientist
        (2, 9, 'Introduction to Supervised Learning (Linear & Logistic Regression)', 'Beginner', 'StatQuest with Josh Starmer, Scikit-learn Getting Started', 'Salary Prediction Model using Scikit-Learn'),
        (2, 9, 'Decision Trees, Random Forests & Ensemble Methods', 'Intermediate', 'Coursera: Machine Learning by Andrew Ng, Scikit-learn Documentation', 'Customer Churn Predictor with Feature Importances'),
        (2, 9, 'Model Tuning, Cross-Validation, ROC-AUC & Deployment', 'Advanced', 'Hands-On Machine Learning with Scikit-Learn, Keras and TensorFlow', 'End-to-End Real Estate Valuation API with Flask'),

        # Python for Data Scientist
        (2, 1, 'NumPy Vectorization & Scientific Computing', 'Beginner', 'NumPy Quickstart Guide, Stanford CS231n Python/NumPy tutorial', 'Matrix Math Engine for Neural Operations'),
        (2, 1, 'Advanced Feature Engineering & Scikit-learn Pipelines', 'Intermediate', 'Feature Engineering for Machine Learning by Alice Zheng', 'Automated ML Preprocessing Pipeline'),
        (2, 1, 'Deep Learning Frameworks (PyTorch / TensorFlow)', 'Advanced', 'Fast.ai Practical Deep Learning, PyTorch Official Tutorials', 'Image Classification with Transfer Learning'),

        # HTML/CSS/JS for Web Developer
        (4, 6, 'Semantic HTML5, Accessibility & SEO Best Practices', 'Beginner', 'MDN Web Docs: HTML basics, freeCodeCamp Responsive Web Design', 'Personal Portfolio Page Structure'),
        (4, 7, 'Modern CSS Layouts (Flexbox, CSS Grid & Media Queries)', 'Intermediate', 'CSS-Tricks: Complete Guide to Flexbox/Grid, Kevin Powell YouTube', 'Fully Responsive Mobile-First Landing Page'),
        (4, 8, 'JavaScript DOM Manipulation, Fetch API & Async/Await', 'Advanced', 'JavaScript.info, Eloquent JavaScript by Marijn Haverbeke', 'Dynamic Weather App with Live API Integration'),

        # Full Stack Developer
        (5, 8, 'Modern ES6+ JavaScript & Component Frameworks', 'Beginner', 'Frontend Masters JS Path, React Official Docs (react.dev)', 'Task Manager Single Page App'),
        (5, 1, 'Flask / Django RESTful API Development', 'Intermediate', 'Flask Mega-Tutorial by Miguel Grinberg', 'RESTful E-Commerce Product & Order API'),
        (5, 5, 'Database Modeling, ORM & JWT Authentication', 'Advanced', 'SQLAlchemy Documentation, OWASP Top 10 Security Guide', 'Full Stack Social Blog with Secure Auth & Comments'),

        # Machine Learning Engineer
        (6, 9, 'ML Math Foundations (Linear Algebra, Multivariable Calculus)', 'Beginner', '3Blue1Brown Essence of Linear Algebra', 'Gradient Descent Optimization Visualizer'),
        (6, 9, 'Model Training, Hyperparameter Tuning & MLflow Tracking', 'Intermediate', 'MLflow Documentation, DeepLearning.AI MLOps Specialization', 'Experiment Tracking Pipeline for Image Classification'),
        (6, 1, 'Production Model Serving with Docker & FastAPI', 'Advanced', 'FastAPI Documentation, Docker for Data Science Tutorials', 'High-Throughput Low-Latency Fraud Detection API'),

        # Software Developer (Java / C++)
        (7, 2, 'Core Java OOP Principles (Inheritance, Polymorphism, Encapsulation)', 'Beginner', 'Oracle Java Tutorials, Mooc.fi Java Programming', 'Banking System Console Application'),
        (7, 2, 'Java Collections Framework, Streams & Concurrency', 'Intermediate', 'Effective Java by Joshua Bloch, Baeldung Java Guides', 'Multi-threaded File Downloader & Indexer'),
        (7, 4, 'Data Structures & Algorithms in C++ / Java', 'Advanced', 'NeetCode 150, Introduction to Algorithms (CLRS)', 'Custom High-Performance LRU Cache'),

        # Database Administrator
        (8, 5, 'Database Normalization (1NF to 3NF/BCNF) & ER Modeling', 'Beginner', 'Database System Concepts by Silberschatz', 'Normalized Hospital Management System Schema'),
        (8, 5, 'Query Profiling, B-Tree Indexes & Execution Plans', 'Intermediate', 'Use The Index, Luke! by Markus Winand', 'Slow Query Optimization Benchmark Report'),
        (8, 5, 'Backup Strategies, Replication & High Availability Failover', 'Advanced', 'MySQL 8.0 Reference Manual: High Availability and Replication', 'Automated Disaster Recovery & Replication Cluster Script')
    ]
    cursor.executemany("""
    INSERT OR IGNORE INTO learning_roadmaps (career_id, skill_id, topic_name, proficiency_level, resources_info, practice_project) VALUES (?, ?, ?, ?, ?, ?)
    """, roadmaps)

    conn.commit()
    conn.close()
