# AI-POWERED SKILL GAP ANALYZER & CAREER PATH RECOMMENDATION SYSTEM

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Random%20Forest-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://mysql.com)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.0-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white)](https://www.chartjs.org/)

---

## 📌 Project Overview

The **AI-Powered Skill Gap Analyzer & Career Path Recommendation System** is a full-stack, machine learning-driven web application tailored for college students and aspiring software professionals. The platform assesses a student's proficiency across **11 core technical skills** and **4 essential soft skills**, runs the profile through a trained **Random Forest Classifier**, predicts the **Top 3 best-fit career roles** with real confidence scores, performs an exhaustive **Skill Gap Analysis** against industry benchmarks, and generates a tiered **Personalized Learning Roadmap** with interactive progress tracking.

---

## 🚀 Key Features

1. **User Authentication & Session Management**:
   - Secure student registration and login with SHA-256 password hashing.
   - Session validation, duplicate email prevention, and protected routes.

2. **Student Profile Management**:
   - Maintain academic details: College, Department, Year of Study, Education details, and Career Interests.
   - Dynamic real-time recommendation fine-tuning based on stated career interests.

3. **Interactive Skill Assessment**:
   - Interactive rating scale (1 to 5) across 15 skills:
     - **11 Technical Skills**: Python, Java, C, C++, SQL, HTML, CSS, JavaScript, Machine Learning, Data Analysis, Excel.
     - **4 Soft Skills**: Communication, Problem Solving, Teamwork, Leadership.
   - Instant database persistence.

4. **AI-Driven Career Recommendation Engine**:
   - Supervised **Random Forest Classifier** trained on 2,400 structured student profiles achieving **98.3% test accuracy**.
   - Outputs top 3 career paths with confidence percentages and explainable feature influence.
   - Supported Careers:
     - *Data Analyst*
     - *Data Scientist*
     - *Python Developer*
     - *Web Developer*
     - *Full Stack Developer*
     - *Machine Learning Engineer*
     - *Software Developer*
     - *Database Administrator*

5. **Skill Gap Analytics**:
   - Side-by-side comparison of student proficiency against target role benchmarks.
   - Classification of skills into **Proficient**, **Weak**, or **Missing**.
   - Interactive **Chart.js Radar** and **Bar Charts** comparing current vs. required proficiency.

6. **Tiered Learning Roadmap**:
   - Customized milestones broken down into **Beginner**, **Intermediate**, and **Advanced** tiers.
   - Curated learning resources (documentation, tutorials, books) and practice project briefs.
   - Interactive AJAX checkboxes to mark topics completed and persist progress in the database.

7. **Student Analytics Dashboard**:
   - Profile summary, total assessed skills, top career match, and benchmark gap score.
   - Dynamic **Chart.js visualizations**:
     - *Student Skills Bar Chart*
     - *Curriculum Completion Doughnut Chart*
     - *Skill Gap Radar Chart*
     - *Progress Tracking Bar*

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | HTML5, CSS3, Bootstrap 5.3, JavaScript (ES6+), Chart.js, Font Awesome 6 |
| **Backend** | Python 3.11, Flask 3.1, Werkzeug |
| **Machine Learning** | Scikit-learn (RandomForestClassifier), Pandas, NumPy, Joblib |
| **Database** | MySQL 8.0 (with automatic seamless SQLite3 fallback for zero-configuration testing) |
| **Development** | Git, GitHub, VS Code / Antigravity |

---

## 📂 Project Folder Structure

```
AI_Career_Guidance/
│
├── app.py                      # Flask Application Server & Routing
├── config.py                   # Configuration & Hybrid DB Connection (MySQL / SQLite)
├── train_model.py              # ML Dataset Generation, Training & Evaluation Script
├── requirements.txt            # Python Dependencies
├── README.md                   # Comprehensive Project Documentation
├── .gitignore                  # Git Ignore Rules
│
├── dataset/
│   └── career_skills.csv       # Training Dataset (2,400 samples across 8 careers)
│
├── model/
│   └── career_model.pkl        # Serialized Random Forest Model & Metadata
│
├── database/
│   └── db.sql                  # Complete MySQL Database Schema and Seed Script
│
├── templates/
│   ├── base.html               # Master Layout (Navbar, Footer, Notifications)
│   ├── index.html              # Landing Page
│   ├── login.html              # Student Login Form
│   ├── register.html           # Student Registration Form
│   ├── dashboard.html          # Student Analytics Dashboard with Chart.js
│   ├── profile.html            # Profile View & Update Form
│   ├── skills.html             # 1-5 Skill Assessment Form
│   ├── recommendation.html     # Top 3 Career Prediction Cards
│   ├── skill_gap.html          # Radar & Bar Skill Gap Visualizer
│   └── roadmap.html            # Tiered Learning Milestones with AJAX Progress Checkboxes
│
├── static/
│   ├── css/
│   │   └── style.css           # Custom Blue/Purple Theme & Responsive Styling
│   └── js/
│       └── script.js           # AJAX Topic Toggle & Interactive UI Logic
│
└── utils/
    ├── __init__.py             # Utils Package Initializer
    ├── prediction.py           # Random Forest Inference & Rationale Engine
    ├── skill_analyzer.py       # Gap Calculator & Chart Data Formatter
    └── roadmap_generator.py    # Learning Roadmap & Progress Tracker
```

---

## 🗄️ Database Design (8 Core Tables)

The database schema `ai_career_guidance` is defined in `database/db.sql`:

1. `students`: Stores credentials, hashed passwords, college details, and career interests.
2. `skills`: Master list of 15 technical and soft skills with descriptions.
3. `student_skills`: Stores 1-5 rating per student per skill with unique composite key.
4. `careers`: Master list of 8 tech roles with salary ranges and industry demand ratings.
5. `career_skills`: Benchmark required ratings (1-5) and importance weights per career.
6. `recommendations`: Top 3 AI recommendations, confidence scores, ranks, and explanations.
7. `learning_roadmaps`: Tiered topics (Beginner/Intermediate/Advanced), resources, and projects.
8. `progress`: Tracks completed topics and timestamps per student.

> **Zero-Configuration SQLite Fallback:** The application includes a self-healing hybrid connection layer in `config.py`. If a local MySQL server is not running, the application automatically initializes and operates using an integrated local SQLite database with identical schema and seed data so you can test immediately without any database setup errors.

---

## ⚙️ Installation & Setup Instructions

### 1. Prerequisites
- Python 3.9+ installed.
- Git installed.
- MySQL Server 8.0 installed (optional; SQLite fallback runs automatically if MySQL is unavailable).

### 2. Clone the Repository
```bash
git clone https://github.com/your-username/AI_Career_Guidance.git
cd AI_Career_Guidance
```

### 3. Create and Activate a Virtual Environment
```bash
# Windows:
python -m venv venv
venv\Scripts\activate

# macOS / Linux:
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. MySQL Database Setup (Optional)
If using MySQL:
1. Start your MySQL Server (e.g. through XAMPP, MySQL Workbench, or service).
2. Open terminal or MySQL CLI:
   ```sql
   mysql -u root -p < database/db.sql
   ```
3. Create a `.env` file in the project root:
   ```env
   SECRET_KEY=your-secret-key-here
   MYSQL_HOST=localhost
   MYSQL_USER=root
   MYSQL_PASSWORD=your_password
   MYSQL_DB=ai_career_guidance
   MYSQL_PORT=3306
   ```

### 6. Train the Machine Learning Model
Generate the dataset and train the Random Forest model:
```bash
python train_model.py
```
*Output: Saves `dataset/career_skills.csv` and `model/career_model.pkl` with 98.3%+ test accuracy.*

### 7. Run the Flask Web Application
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Testing the Application

1. **Register**: Click **Register Free**, fill in name, college, email, password, and target interests.
2. **Skill Assessment**: Rate your skills from 1 to 5. Click **Save & Generate Recommendations**.
3. **AI Recommendations**: View your Top 3 career matches with confidence bars and AI reasoning.
4. **Skill Gap Analysis**: Click **Analyze Skill Gaps** to view the interactive Radar and Bar charts showing where you meet or lag behind role benchmarks.
5. **Learning Roadmap**: Check off completed learning topics. Notice how the completion percentage and counters update in real-time without reloading the page.
6. **Dashboard**: Navigate to the Dashboard to review the full suite of live charts and summaries.

---

## 📤 GitHub Upload Instructions

```bash
git init
git add .
git commit -m "feat: complete AI-powered skill gap analyzer and career recommendation system"
git branch -M main
git remote add origin https://github.com/<your-username>/AI_Career_Guidance.git
git push -u origin main
```

---

## 📄 License
This project is open-source and available under the **MIT License**.
"# nithra" 
