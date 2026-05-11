-- Yeh SQL pgAdmin Query Tool mein paste karke F5 dabao

-- Step 1: Purani table hatao
DROP TABLE IF EXISTS courses CASCADE;

-- Step 2: Naya table SERIAL id ke saath banao
CREATE TABLE courses (
    id               SERIAL PRIMARY KEY,
    title            VARCHAR(200) NOT NULL,
    instructor       VARCHAR(100) NOT NULL,
    category         VARCHAR(100) NOT NULL,
    price            FLOAT        NOT NULL,
    duration_hours   INTEGER      NOT NULL,
    is_published     BOOLEAN      NOT NULL DEFAULT false,
    discount_percent FLOAT                 DEFAULT 0.0
);

-- Step 3: Purana data wapas daalo
INSERT INTO courses (title, instructor, category, price, duration_hours, is_published, discount_percent) VALUES
('Python For Beginners',              'Aanya Sharma', 'programming',      499.0,  12, true,  10.0),
('Fastapi Full Course',               'Rohan Mehta',  'web development',  799.0,  20, true,  0.0),
('Data Structures And Algorithms',    'Priya Nair',   'computer science', 999.0,  35, true,  15.0),
('Machine Learning With Scikit-Learn','Karan Joshi',  'data science',    1299.0,  40, true,  20.0),
('React.Js Zero To Hero',             'Simran Kaur',  'web development',  849.0,  28, false, 0.0),
('Sql And Postgresql Mastery',        'Arjun Pillai', 'databases',        649.0,  18, true,  5.0),
('Docker And Kubernetes Basics',      'Neha Gupta',   'devops',          1099.0,  22, true,  0.0),
('Ui/Ux Design Fundamentals',         'Vikram Desai', 'design',           599.0,  15, false, 0.0),
('Deep Learning With Tensorflow',     'Priya Nair',   'data science',    1499.0,  50, true,  25.0),
('Linux Command Line For Developers', 'Aanya Sharma', 'devops',           399.0,  10, true,  0.0);

-- Verify karo
SELECT * FROM courses;