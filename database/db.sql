-- =========================================================
-- AI-POWERED SKILL GAP ANALYZER & CAREER PATH RECOMMENDATION SYSTEM
-- Database Initialization Script for MySQL
-- Database: ai_career_guidance
-- =========================================================

CREATE DATABASE IF NOT EXISTS `ai_career_guidance` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `ai_career_guidance`;

-- Disable foreign key checks during initialization
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `progress`;
DROP TABLE IF EXISTS `learning_roadmaps`;
DROP TABLE IF EXISTS `recommendations`;
DROP TABLE IF EXISTS `career_skills`;
DROP TABLE IF EXISTS `careers`;
DROP TABLE IF EXISTS `student_skills`;
DROP TABLE IF EXISTS `skills`;
DROP TABLE IF EXISTS `students`;

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

-- 1. Students Table
CREATE TABLE `students` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `full_name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(120) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `college_name` VARCHAR(150),
    `department` VARCHAR(100),
    `year_of_study` VARCHAR(20),
    `education_details` TEXT,
    `career_interests` TEXT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Skills Table
CREATE TABLE `skills` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `skill_name` VARCHAR(100) NOT NULL UNIQUE,
    `skill_type` ENUM('technical', 'soft') NOT NULL,
    `description` TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Student Skills Table
CREATE TABLE `student_skills` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `skill_id` INT NOT NULL,
    `rating` INT NOT NULL CHECK (`rating` BETWEEN 1 AND 5),
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_student_skills_student` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_student_skills_skill` FOREIGN KEY (`skill_id`) REFERENCES `skills` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `unique_student_skill` (`student_id`, `skill_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Careers Table
CREATE TABLE `careers` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `career_title` VARCHAR(100) NOT NULL UNIQUE,
    `description` TEXT NOT NULL,
    `avg_salary` VARCHAR(50),
    `industry_demand` VARCHAR(50),
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Career Skills Table (Required skill levels for each career)
CREATE TABLE `career_skills` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `career_id` INT NOT NULL,
    `skill_id` INT NOT NULL,
    `required_level` INT NOT NULL CHECK (`required_level` BETWEEN 1 AND 5),
    `importance_weight` DECIMAL(3,2) DEFAULT 1.00,
    CONSTRAINT `fk_career_skills_career` FOREIGN KEY (`career_id`) REFERENCES `careers` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_career_skills_skill` FOREIGN KEY (`skill_id`) REFERENCES `skills` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `unique_career_skill` (`career_id`, `skill_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Recommendations Table
CREATE TABLE `recommendations` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `career_id` INT NOT NULL,
    `match_score` DECIMAL(5,2) NOT NULL,
    `rank_order` INT NOT NULL,
    `explanation` TEXT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_recommendations_student` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_recommendations_career` FOREIGN KEY (`career_id`) REFERENCES `careers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. Learning Roadmaps Table
CREATE TABLE `learning_roadmaps` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `career_id` INT NOT NULL,
    `skill_id` INT NOT NULL,
    `topic_name` VARCHAR(150) NOT NULL,
    `proficiency_level` ENUM('Beginner', 'Intermediate', 'Advanced') NOT NULL,
    `resources_info` TEXT NOT NULL,
    `practice_project` TEXT NOT NULL,
    CONSTRAINT `fk_roadmaps_career` FOREIGN KEY (`career_id`) REFERENCES `careers` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_roadmaps_skill` FOREIGN KEY (`skill_id`) REFERENCES `skills` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. Progress Tracking Table
CREATE TABLE `progress` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `roadmap_id` INT NOT NULL,
    `is_completed` TINYINT(1) DEFAULT 0,
    `completed_at` TIMESTAMP NULL DEFAULT NULL,
    CONSTRAINT `fk_progress_student` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_progress_roadmap` FOREIGN KEY (`roadmap_id`) REFERENCES `learning_roadmaps` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `unique_student_roadmap` (`student_id`, `roadmap_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- SEED DATA
-- =========================================================

-- Seed 15 Skills (11 Technical, 4 Soft)
INSERT INTO `skills` (`id`, `skill_name`, `skill_type`, `description`) VALUES
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
(15, 'Leadership', 'soft', 'Inspiring others, taking initiative, managing project delivery, and mentoring peers.');

-- Seed 8 Target Careers
INSERT INTO `careers` (`id`, `career_title`, `description`, `avg_salary`, `industry_demand`) VALUES
(1, 'Data Analyst', 'Interprets complex datasets to help businesses make data-driven decisions using SQL, Excel, and visualization tools.', '$70,000 - $95,000 / yr', 'Very High'),
(2, 'Data Scientist', 'Combines advanced statistics, machine learning, and programming to extract deep predictive insights from big data.', '$110,000 - $145,000 / yr', 'Extremely High'),
(3, 'Python Developer', 'Designs and builds backend services, automation pipelines, APIs, and microservices using modern Python frameworks.', '$85,000 - $115,000 / yr', 'High'),
(4, 'Web Developer', 'Develops responsive, accessible, and high-performance client-facing websites using HTML, CSS, and modern JavaScript.', '$75,000 - $100,000 / yr', 'Very High'),
(5, 'Full Stack Developer', 'Masters both frontend interfaces and robust backend architectures, databases, and APIs for end-to-end web products.', '$95,000 - $130,000 / yr', 'Extremely High'),
(6, 'Machine Learning Engineer', 'Researches, builds, deploys, and optimizes production-ready AI models and machine learning pipelines at scale.', '$120,000 - $160,000 / yr', 'Extremely High'),
(7, 'Software Developer', 'Architects and engineers scalable desktop, mobile, or enterprise software applications using OOP principles and C++/Java.', '$90,000 - $125,000 / yr', 'Very High'),
(8, 'Database Administrator', 'Maintains, secures, optimizes, and tunes mission-critical relational database systems ensuring high availability.', '$85,000 - $115,000 / yr', 'High');

-- Seed Career Skills Benchmarks (Required Skill Levels 1-5 and Weights)
-- 1. Data Analyst
INSERT INTO `career_skills` (`career_id`, `skill_id`, `required_level`, `importance_weight`) VALUES
(1, 1, 3, 1.20), -- Python: 3
(1, 5, 5, 1.50), -- SQL: 5
(1, 10, 5, 1.50), -- Data Analysis: 5
(1, 11, 4, 1.30), -- Excel: 4
(1, 9, 2, 0.80), -- Machine Learning: 2
(1, 12, 4, 1.20), -- Communication: 4
(1, 13, 4, 1.20); -- Problem Solving: 4

-- 2. Data Scientist
INSERT INTO `career_skills` (`career_id`, `skill_id`, `required_level`, `importance_weight`) VALUES
(2, 1, 5, 1.50), -- Python: 5
(2, 5, 4, 1.20), -- SQL: 4
(2, 9, 5, 1.50), -- Machine Learning: 5
(2, 10, 5, 1.50), -- Data Analysis: 5
(2, 13, 5, 1.30), -- Problem Solving: 5
(2, 12, 4, 1.10), -- Communication: 4
(2, 11, 3, 0.80); -- Excel: 3

-- 3. Python Developer
INSERT INTO `career_skills` (`career_id`, `skill_id`, `required_level`, `importance_weight`) VALUES
(3, 1, 5, 1.50), -- Python: 5
(3, 5, 4, 1.30), -- SQL: 4
(3, 6, 3, 0.90), -- HTML: 3
(3, 7, 3, 0.90), -- CSS: 3
(3, 8, 3, 1.00), -- JavaScript: 3
(3, 13, 4, 1.20), -- Problem Solving: 4
(3, 14, 4, 1.10); -- Teamwork: 4

-- 4. Web Developer
INSERT INTO `career_skills` (`career_id`, `skill_id`, `required_level`, `importance_weight`) VALUES
(4, 6, 5, 1.50), -- HTML: 5
(4, 7, 5, 1.50), -- CSS: 5
(4, 8, 5, 1.50), -- JavaScript: 5
(4, 1, 2, 0.80), -- Python: 2
(4, 13, 4, 1.10), -- Problem Solving: 4
(4, 12, 3, 1.00), -- Communication: 3
(4, 14, 4, 1.00); -- Teamwork: 4

-- 5. Full Stack Developer
INSERT INTO `career_skills` (`career_id`, `skill_id`, `required_level`, `importance_weight`) VALUES
(5, 6, 5, 1.30), -- HTML: 5
(5, 7, 5, 1.30), -- CSS: 5
(5, 8, 5, 1.50), -- JavaScript: 5
(5, 1, 4, 1.40), -- Python: 4
(5, 5, 4, 1.40), -- SQL: 4
(5, 13, 5, 1.30), -- Problem Solving: 5
(5, 14, 4, 1.10); -- Teamwork: 4

-- 6. Machine Learning Engineer
INSERT INTO `career_skills` (`career_id`, `skill_id`, `required_level`, `importance_weight`) VALUES
(6, 1, 5, 1.50), -- Python: 5
(6, 9, 5, 1.50), -- Machine Learning: 5
(6, 10, 4, 1.30), -- Data Analysis: 4
(6, 4, 3, 1.00), -- C++: 3
(6, 5, 3, 1.00), -- SQL: 3
(6, 13, 5, 1.40), -- Problem Solving: 5
(6, 15, 3, 1.00); -- Leadership: 3

-- 7. Software Developer
INSERT INTO `career_skills` (`career_id`, `skill_id`, `required_level`, `importance_weight`) VALUES
(7, 2, 5, 1.50), -- Java: 5
(7, 4, 4, 1.30), -- C++: 4
(7, 3, 3, 1.00), -- C: 3
(7, 5, 4, 1.20), -- SQL: 4
(7, 13, 5, 1.40), -- Problem Solving: 5
(7, 14, 4, 1.20), -- Teamwork: 4
(7, 1, 3, 1.00); -- Python: 3

-- 8. Database Administrator
INSERT INTO `career_skills` (`career_id`, `skill_id`, `required_level`, `importance_weight`) VALUES
(8, 5, 5, 1.50), -- SQL: 5
(8, 1, 3, 1.10), -- Python: 3
(8, 10, 3, 1.10), -- Data Analysis: 3
(8, 11, 3, 0.90), -- Excel: 3
(8, 13, 4, 1.30), -- Problem Solving: 4
(8, 12, 3, 1.00), -- Communication: 3
(8, 14, 3, 1.00); -- Teamwork: 3

-- Seed Detailed Learning Roadmaps for Career-Skill Gaps (Beginner, Intermediate, Advanced)
INSERT INTO `learning_roadmaps` (`career_id`, `skill_id`, `topic_name`, `proficiency_level`, `resources_info`, `practice_project`) VALUES
-- Python for Data Analyst
(1, 1, 'Python Syntax, Data Structures & Control Flow', 'Beginner', 'Docs: docs.python.org/3/tutorial, Coursera: Python for Everybody', 'CLI Number Guessing Game & Contact Book'),
(1, 1, 'Pandas & NumPy Data Wrangling', 'Intermediate', 'Tutorial: pandas.pydata.org/docs, Book: Python for Data Analysis by Wes McKinney', 'Automated Sales Data Cleaning & CSV Merger'),
(1, 1, 'Exploratory Data Analysis with Matplotlib & Seaborn', 'Advanced', 'Kaggle Learn: Data Visualization, Real Python EDA Tutorials', 'Interactive Customer Segmentation Dashboard'),

-- SQL for Data Analyst
(1, 5, 'Relational Databases & Basic Queries (SELECT, WHERE, ORDER)', 'Beginner', 'W3Schools SQL Tutorial, Mode Analytics SQL Tutorial', 'Student Records Query Database'),
(1, 5, 'Joins, Grouping & Aggregations (INNER/LEFT JOIN, GROUP BY, HAVING)', 'Intermediate', 'SQLZoo, LeetCode SQL 50 Study Plan', 'E-commerce Orders & Customer Analytics Queries'),
(1, 5, 'Window Functions, CTEs & Index Optimization', 'Advanced', 'Mode SQL Advanced Guide, Brent Ozar Performance Tuning', 'Monthly Churn & Rolling Revenue Analysis System'),

-- Data Analysis for Data Analyst
(1, 10, 'Descriptive Statistics & Summary Metrics', 'Beginner', 'Khan Academy Statistics and Probability', 'Statistical Analysis of Housing Prices'),
(1, 10, 'Hypothesis Testing & Correlation Analysis', 'Intermediate', 'Coursera: Applied Data Science with Python', 'A/B Testing Analysis for Landing Page Conversions'),
(1, 10, 'Business Intelligence Reporting & Storytelling', 'Advanced', 'Tableau / PowerBI Guides, Storytelling with Data by Cole Nussbaumer', 'Executive Company Performance Dashboard'),

-- Excel for Data Analyst
(1, 11, 'Formulas, VLOOKUP/XLOOKUP & Conditional Formatting', 'Beginner', 'Microsoft Excel Video Training, ExcelJet Free Guides', 'Monthly Personal Budget & Expense Tracker'),
(1, 11, 'Pivot Tables, Slicers & Dynamic Charts', 'Intermediate', 'Chandoo.org Excel Tutorials', 'Retail Inventory & Sales Pivot Analysis'),
(1, 11, 'Advanced Excel: Power Query, Macros & What-If Analysis', 'Advanced', 'Excel Power Query Official Guide, Leila Gharani YouTube Tutorials', 'Automated Multi-Source Financial Model'),

-- Machine Learning for Data Scientist
(2, 9, 'Introduction to Supervised Learning (Linear & Logistic Regression)', 'Beginner', 'StatQuest with Josh Starmer, Scikit-learn Getting Started', 'Salary Prediction Model using Scikit-Learn'),
(2, 9, 'Decision Trees, Random Forests & Ensemble Methods', 'Intermediate', 'Coursera: Machine Learning by Andrew Ng, Scikit-learn Documentation', 'Customer Churn Predictor with Feature Importances'),
(2, 9, 'Model Tuning, Cross-Validation, ROC-AUC & Deployment', 'Advanced', 'Hands-On Machine Learning with Scikit-Learn, Keras and TensorFlow', 'End-to-End Real Estate Valuation API with Flask'),

-- Python for Data Scientist
(2, 1, 'NumPy Vectorization & Scientific Computing', 'Beginner', 'NumPy Quickstart Guide, Stanford CS231n Python/NumPy tutorial', 'Matrix Math Engine for Neural Operations'),
(2, 1, 'Advanced Feature Engineering & Scikit-learn Pipelines', 'Intermediate', 'Feature Engineering for Machine Learning by Alice Zheng', 'Automated ML Preprocessing Pipeline'),
(2, 1, 'Deep Learning Frameworks (PyTorch / TensorFlow)', 'Advanced', 'Fast.ai Practical Deep Learning, PyTorch Official Tutorials', 'Image Classification with Transfer Learning'),

-- HTML/CSS/JS for Web Developer
(4, 6, 'Semantic HTML5, Accessibility & SEO Best Practices', 'Beginner', 'MDN Web Docs: HTML basics, freeCodeCamp Responsive Web Design', 'Personal Portfolio Page Structure'),
(4, 7, 'Modern CSS Layouts (Flexbox, CSS Grid & Media Queries)', 'Intermediate', 'CSS-Tricks: Complete Guide to Flexbox/Grid, Kevin Powell YouTube', 'Fully Responsive Mobile-First Landing Page'),
(4, 8, 'JavaScript DOM Manipulation, Fetch API & Async/Await', 'Advanced', 'JavaScript.info, Eloquent JavaScript by Marijn Haverbeke', 'Dynamic Weather App with Live API Integration'),

-- Full Stack Developer
(5, 8, 'Modern ES6+ JavaScript & Component Frameworks', 'Beginner', 'Frontend Masters JS Path, React Official Docs (react.dev)', 'Task Manager Single Page App'),
(5, 1, 'Flask / Django RESTful API Development', 'Intermediate', 'Flask Mega-Tutorial by Miguel Grinberg', 'RESTful E-Commerce Product & Order API'),
(5, 5, 'Database Modeling, ORM & JWT Authentication', 'Advanced', 'SQLAlchemy Documentation, OWASP Top 10 Security Guide', 'Full Stack Social Blog with Secure Auth & Comments'),

-- Machine Learning Engineer
(6, 9, 'ML Math Foundations (Linear Algebra, Multivariable Calculus)', 'Beginner', '3Blue1Brown Essence of Linear Algebra', 'Gradient Descent Optimization Visualizer'),
(6, 9, 'Model Training, Hyperparameter Tuning & MLflow Tracking', 'Intermediate', 'MLflow Documentation, DeepLearning.AI MLOps Specialization', 'Experiment Tracking Pipeline for Image Classification'),
(6, 1, 'Production Model Serving with Docker & FastAPI', 'Advanced', 'FastAPI Documentation, Docker for Data Science Tutorials', 'High-Throughput Low-Latency Fraud Detection API'),

-- Software Developer (Java / C++)
(7, 2, 'Core Java OOP Principles (Inheritance, Polymorphism, Encapsulation)', 'Beginner', 'Oracle Java Tutorials, Mooc.fi Java Programming', 'Banking System Console Application'),
(7, 2, 'Java Collections Framework, Streams & Concurrency', 'Intermediate', 'Effective Java by Joshua Bloch, Baeldung Java Guides', 'Multi-threaded File Downloader & Indexer'),
(7, 4, 'Data Structures & Algorithms in C++ / Java', 'Advanced', 'NeetCode 150, Introduction to Algorithms (CLRS)', 'Custom High-Performance LRU Cache'),

-- Database Administrator
(8, 5, 'Database Normalization (1NF to 3NF/BCNF) & ER Modeling', 'Beginner', 'Database System Concepts by Silberschatz', 'Normalized Hospital Management System Schema'),
(8, 5, 'Query Profiling, B-Tree Indexes & Execution Plans', 'Intermediate', 'Use The Index, Luke! by Markus Winand', 'Slow Query Optimization Benchmark Report'),
(8, 5, 'Backup Strategies, Replication & High Availability Failover', 'Advanced', 'MySQL 8.0 Reference Manual: High Availability and Replication', 'Automated Disaster Recovery & Replication Cluster Script');
