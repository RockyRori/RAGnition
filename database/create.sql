-- 创建数据库（如果不存在）并切换
CREATE DATABASE IF NOT EXISTS ragnition;
USE ragnition;


-- 删除表（注意外键依赖顺序）
DROP TABLE IF EXISTS files;
DROP TABLE IF EXISTS questions;
DROP TABLE IF EXISTS sessions;


-- 创建会话表
CREATE TABLE sessions
(
    session_id    VARCHAR(255) PRIMARY KEY,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- 创建问题表（使用反引号处理保留字）
CREATE TABLE questions
(
    session_id         VARCHAR(255),
    question_id        VARCHAR(255),
    previous_questions JSON, -- 存储历史问题列表
    current_question   TEXT,
    answer             TEXT,
    `references`       JSON, -- 更新字段名为 references
    rating             INT CHECK (rating BETWEEN 1 AND 10),
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (session_id, question_id),
    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
);


-- 创建文件表
CREATE TABLE files
(
    file_id          VARCHAR(255) PRIMARY KEY,
    file_name        VARCHAR(255) NOT NULL,
    file_description TEXT,
    file_content     LONGBLOB NOT NULL,
    uploaded_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_size        VARCHAR(50) NOT NULL -- 新增字段: 文件大小
);


-- 插入初始数据
INSERT INTO sessions (session_id)
VALUES ('abcd123456'),
       ('efgh789012');

INSERT INTO questions (session_id, question_id, previous_questions, current_question, answer, `references`, rating)
VALUES
('abcd123456', '1700000000',
 '["What are the thesis submission rules?", "What is the submission deadline?"]',
 'Can I submit my thesis late?',
 'No, you cannot submit your thesis after the deadline.',
 '[{
    "content": "4 At the end of the term in which the student on academic probation has cumulatively enrolled in 6 or more credits, if he/she obtains a Cumulative GPA of 2.",
    "source": "pieces\\\\MScDS_Student_Handbook_2024-25_segmented.txt",
    "similarity": "22%"
 }]',
 1),

('abcd123456', '1700000001',
 '["What are the thesis submission rules?", "What is the submission deadline?", "Can I submit my thesis late?"]',
 'How to request an extension?',
 'You must apply for an extension at least one week before the deadline.',
 '[{
    "content": "Reference 3: Extension request guidelines from the Faculty page.",
    "source": "faculty_page_guidelines.txt",
    "similarity": "85%"
 }]',
 2),

('efgh789012', '1700000000',
 '[]',
 'Where is the library located?',
 'The main library is located at Building A, 2nd floor.',
 '[{
    "content": "Reference 4: Campus map description.",
    "source": "campus_map.txt",
    "similarity": "90%"
 }]',
 3);

INSERT INTO files (file_id, file_name, file_description, file_content, file_size)
VALUES ('file-20231025001', 'document.pdf', 'Thesis submission guidelines', 0x255044462d312e340a25c7ec8fa2, '1.2MB'),
       ('file-20231025002', 'image.png', 'Campus Map', 0x89504e470d0a1a0a0000000d49484452, '500KB');