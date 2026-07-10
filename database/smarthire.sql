CREATE DATABASE smarthire_db;

USE smarthire_db;

SHOW DATABASES;
SELECT DATABASE();

CREATE TABLE users (

    id INT AUTO_INCREMENT PRIMARY KEY,

    full_name VARCHAR(100) NOT NULL,

    email VARCHAR(100) NOT NULL UNIQUE,

    phone VARCHAR(15) NOT NULL,

    password VARCHAR(255) NOT NULL,

    role ENUM('user','admin') DEFAULT 'user',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

SHOW TABLES;

DESCRIBE users;

INSERT INTO users
(full_name,email,phone,password)

VALUES

(
'Bishal Kumar',
'bishal@gmail.com',
'9876543210',
'123456'
);
SELECT * FROM users;

CREATE TABLE categories (

    id INT AUTO_INCREMENT PRIMARY KEY,

    category_name VARCHAR(100) NOT NULL UNIQUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);
SHOW TABLES;
DESCRIBE categories;
INSERT INTO categories(category_name)
VALUES

('Software Development'),
('Artificial Intelligence'),
('Data Science'),
('Cloud Computing'),
('Cyber Security'),
('UI/UX Design'),
('Digital Marketing'),
('Database');

CREATE TABLE companies (

    id INT AUTO_INCREMENT PRIMARY KEY,

    company_name VARCHAR(100) NOT NULL UNIQUE,

    company_logo VARCHAR(255),

    website VARCHAR(255),

    email VARCHAR(100),

    location VARCHAR(100),

    description TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);
SHOW TABLES;
DESCRIBE companies;

INSERT INTO companies
(company_name, website, email, location, description)

VALUES

(
'Google',
'https://www.google.com',
'careers@google.com',
'Bengaluru',
'Global technology company specializing in search, cloud and AI.'
),

(
'Microsoft',
'https://www.microsoft.com',
'careers@microsoft.com',
'Hyderabad',
'Leading software and cloud solutions provider.'
),

(
'Amazon',
'https://www.amazon.com',
'jobs@amazon.com',
'Pune',
'Global e-commerce and cloud computing company.'
);
SELECT * FROM companies;

CREATE TABLE jobs (

    id INT AUTO_INCREMENT PRIMARY KEY,

    company_id INT NOT NULL,

    category_id INT NOT NULL,

    job_title VARCHAR(150) NOT NULL,

    location VARCHAR(100) NOT NULL,

    salary VARCHAR(50),

    experience VARCHAR(50),

    job_type ENUM(
        'Full Time',
        'Part Time',
        'Internship',
        'Remote',
        'Hybrid'
    ) DEFAULT 'Full Time',

    description TEXT,

    deadline DATE,

    status ENUM(
        'Active',
        'Closed'
    ) DEFAULT 'Active',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (company_id)
        REFERENCES companies(id),

    FOREIGN KEY (category_id)
        REFERENCES categories(id)

);
SHOW TABLES;
DESCRIBE jobs;
INSERT INTO jobs
(
company_id,
category_id,
job_title,
location,
salary,
experience,
job_type,
description,
deadline
)

VALUES

(
1,
1,
'Python Backend Developer',
'Bengaluru',
'12 LPA',
'2+ Years',
'Full Time',
'Develop scalable backend applications using Python and MySQL.',
'2026-08-15'
);

SELECT * FROM jobs;
SELECT

jobs.job_title,

companies.company_name,

categories.category_name,

jobs.salary,

jobs.location

FROM jobs

JOIN companies

ON jobs.company_id = companies.id

JOIN categories

ON jobs.category_id = categories.id;

-- MODULE 3.6
CREATE TABLE applications (

    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,

    job_id INT NOT NULL,

    resume VARCHAR(255),

    cover_letter TEXT,

    application_status ENUM(
        'Pending',
        'Shortlisted',
        'Rejected',
        'Selected'
    ) DEFAULT 'Pending',

    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY (job_id)
        REFERENCES jobs(id)
        ON DELETE CASCADE,

    UNIQUE(user_id, job_id)

);

INSERT INTO applications
(
user_id,
job_id,
resume,
cover_letter
)

VALUES

(
1,
1,
'bishal_resume.pdf',
'I am interested in this position.'
);

SELECT * FROM applications;

SELECT

users.full_name,

jobs.job_title,

companies.company_name,

applications.application_status,

applications.applied_at

FROM applications

JOIN users
ON applications.user_id = users.id

JOIN jobs
ON applications.job_id = jobs.id

JOIN companies
ON jobs.company_id = companies.id;

-- MODULE 3.7

CREATE TABLE saved_jobs (

    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,

    job_id INT NOT NULL,

    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY (job_id)
        REFERENCES jobs(id)
        ON DELETE CASCADE,

    UNIQUE(user_id, job_id)

);

INSERT INTO saved_jobs
(
user_id,
job_id
)

VALUES

(
1,
1
);
SELECT * FROM saved_jobs;

SELECT

users.full_name,

jobs.job_title,

companies.company_name,

saved_jobs.saved_at

FROM saved_jobs

JOIN users
ON saved_jobs.user_id = users.id

JOIN jobs
ON saved_jobs.job_id = jobs.id

JOIN companies
ON jobs.company_id = companies.id;


-- MODULE 3.8
CREATE TABLE newsletter (

    id INT AUTO_INCREMENT PRIMARY KEY,

    email VARCHAR(100) NOT NULL UNIQUE,

    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);
SHOW TABLES;
DESCRIBE newsletter;

INSERT INTO newsletter (email)

VALUES

('bishal@gmail.com'),

('demo@gmail.com');

SELECT * FROM newsletter;

ALTER TABLE users
ADD resume VARCHAR(255);

INSERT INTO users
(full_name,email,phone,password,role)

VALUES
(
'Admin',
'admin@smarthire.com',
'9999999999',
'admin123',
'admin'
);

UPDATE users
SET role='admin'
WHERE email='admin2@smarthire.com';

SELECT * FROM companies;

DELETE FROM companies
WHERE company_name='Google'
LIMIT 1;

SHOW CREATE TABLE companies;

DELETE FROM companies
WHERE company_name='Google';

DESCRIBE jobs;
SHOW CREATE TABLE jobs;

INSERT INTO categories (category_name)
VALUES
('Software Development'),
('Data Science'),
('Artificial Intelligence'),
('Cyber Security'),
('Cloud Computing');

SELECT * FROM categories;

CREATE TABLE job_requests (

    id INT AUTO_INCREMENT PRIMARY KEY,

    company_name VARCHAR(100) NOT NULL,

    hr_name VARCHAR(100) NOT NULL,

    email VARCHAR(100) NOT NULL,

    phone VARCHAR(20) NOT NULL,

    job_title VARCHAR(150) NOT NULL,

    location VARCHAR(100) NOT NULL,

    salary VARCHAR(50),

    experience VARCHAR(50),

    job_type ENUM(
        'Full Time',
        'Part Time',
        'Internship',
        'Remote',
        'Hybrid'
    ) DEFAULT 'Full Time',

    description TEXT,

    deadline DATE,

    status ENUM(
        'Pending',
        'Approved',
        'Rejected'
    ) DEFAULT 'Pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

SELECT * FROM job_requests;

CREATE TABLE contact_messages (

    id INT AUTO_INCREMENT PRIMARY KEY,

    name VARCHAR(100) NOT NULL,

    email VARCHAR(100) NOT NULL,

    subject VARCHAR(150) NOT NULL,

    message TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

SELECT * FROM contact_messages;

DESCRIBE companies;
DESCRIBE applications;
ALTER TABLE companies
ADD password VARCHAR(255) NOT NULL;