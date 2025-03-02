-- 创建数据库（如果不存在）并切换
CREATE DATABASE IF NOT EXISTS ragnition;
USE ragnition;


-- 删除表（注意外键依赖顺序）
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
    reference          JSON, -- 使用反引号包裹保留字
    reference_links    JSON,
    rating             INT CHECK (rating BETWEEN 1 AND 10),
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (session_id, question_id),
    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
);


INSERT INTO sessions (session_id)
VALUES ('abcd123456'),
       ('efgh789012');

INSERT INTO questions (session_id, question_id, previous_questions, current_question, answer, reference,
                       reference_links, rating)
VALUES
-- 会话 abcd123456 的第一个问题
('abcd123456', '1700000000',
 '[
   "What are the thesis submission rules?",
   "What is the submission deadline?"
 ]',
 'Can I submit my thesis late?',
 'No, you cannot submit your thesis after the deadline.',
 '[
   "Reference 1: Content snippet from the Student Handbook.",
   "Reference 2: Content snippet from the Thesis Submission Rules."
 ]',
 '[
   "http://example.com/handbook#thesis",
   "http://example.com/rules#submission"
 ]',
 1),
-- 会话 abcd123456 的第二个问题
('abcd123456', '1700000001',
 '[
   "What are the thesis submission rules?",
   "What is the submission deadline?",
   "Can I submit my thesis late?"
 ]',
 'How to request an extension?',
 'You must apply for an extension at least one week before the deadline.',
 '[
   "Reference 3: Extension request guidelines from the Faculty page."
 ]',
 '[
   "http://example.com/faculty#extensions"
 ]',
 2),
-- 会话 efgh789012 的问题
('efgh789012', '1700000000',
 '[]',
 'Where is the library located?',
 'The main library is located at Building A, 2nd floor.',
 '[
   "Reference 4: Campus map description."
 ]',
 '[
   "http://example.com/campus#library"
 ]',
 3);