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
    session_id    VARCHAR(28) PRIMARY KEY,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- 创建问题表（使用反引号处理保留字）
CREATE TABLE questions
(
    session_id         VARCHAR(28),
    question_id        VARCHAR(28),
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
    base             VARCHAR(28)  NOT NULL DEFAULT 'lingnan' COMMENT '文件来源于哪个知识库',
    file_name        VARCHAR(255) NOT NULL COMMENT '文件名称',
    file_description TEXT COMMENT '文件简介',
    file_path        VARCHAR(512) NOT NULL COMMENT '文件在存储系统里的路径或URL',
    file_size        VARCHAR(28)  NOT NULL COMMENT '文件大小',
    uploaded_at      TIMESTAMP             DEFAULT CURRENT_TIMESTAMP COMMENT '上传/更新文件时间',
    PRIMARY KEY (base, file_name),
    KEY idx_base (base)
);


-- 插入初始数据
INSERT INTO sessions (session_id)
VALUES ('abcd123456'),
       ('efgh789012');

INSERT INTO questions (session_id, question_id, previous_questions, current_question, answer, `references`, rating)
VALUES ('abcd123456', '1700000000',
        '[
          "What are the thesis submission rules?",
          "What is the submission deadline?"
        ]',
        'Can I submit my thesis late?',
        'No, you cannot submit your thesis after the deadline.',
        '[
          {
            "content": "4 At the end of the term in which the student on academic probation has cumulatively enrolled in 6 or more credits, if he/she obtains a Cumulative GPA of 2.",
            "source": "pieces\\\\MScDS_Student_Handbook_2024-25_segmented.txt",
            "similarity": "22%"
          }
        ]',
        1),

       ('abcd123456', '1700000001',
        '[
          "What are the thesis submission rules?",
          "What is the submission deadline?",
          "Can I submit my thesis late?"
        ]',
        'How to request an extension?',
        'You must apply for an extension at least one week before the deadline.',
        '[
          {
            "content": "Reference 3: Extension request guidelines from the Faculty page.",
            "source": "faculty_page_guidelines.txt",
            "similarity": "85%"
          }
        ]',
        2),

       ('efgh789012', '1700000000',
        '[]',
        'Where is the library located?',
        'The main library is located at Building A, 2nd floor.',
        '[
          {
            "content": "Reference 4: Campus map description.",
            "source": "campus_map.txt",
            "similarity": "90%"
          }
        ]',
        3);

insert into ragnition.files (base, file_name, file_description, file_path, file_size, uploaded_at)
values ('base_DS', 'Acceptance Form.pdf', 'hk Fax: (852) 2892 -2442 ACCEPTANCE FORM I, ______________________',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/Acceptance Form.pdf', '112.0KB',
        '2025-05-02 13:26:30'),
       ('base_DS', 'MScDS - Course Schedule of AY 2024-25 (Term 1).pdf',
        'Sunday Monday Tuesday Wednesday Thursday Friday Saturday 01-Sep-20',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/MScDS - Course Schedule of AY 2024-25 (Term 1).pdf',
        '114.5KB', '2025-05-02 13:24:16'),
       ('base_DS', 'MScDS - Course Schedule of AY 2024-25 (Term 2).pdf',
        'Sunday Monday Tuesday Wednesday Thursday Friday Saturday 05-Jan-20',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/MScDS - Course Schedule of AY 2024-25 (Term 2).pdf',
        '110.3KB', '2025-05-02 13:24:20'),
       ('base_DS', 'MScDS_Student_Handbook_2024-25.pdf',
        '1 Master of Science in Data Science PROGRAMME HANDBOOK 2024 -2025 ',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/MScDS_Student_Handbook_2024-25.pdf', '919.4KB',
        '2025-05-02 13:25:31'),
       ('lingnan', '2024-2025_LUStudentMedical_Medinet_Leaflet.pdf',
        'Lingnan University Student Medical Scheme 2024-2025 Period of Cove',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/2024-2025_LUStudentMedical_Medinet_Leaflet.pdf',
        '812.4KB', '2025-05-02 13:24:11'),
       ('lingnan', 'A_Guide_to_Residential_Life_2024.pdf',
        '1 • Liberal Arts Education and Residential Education 2 • Living-Le',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/A_Guide_to_Residential_Life_2024.pdf', '9.5MB',
        '2025-05-02 13:25:18'),
       ('lingnan', 'Admission Requirements.docx', 'Admission Information Minimum Admission Requirements For a Doctora',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/Admission Requirements.docx', '16.7KB',
        '2025-05-02 13:18:29'),
       ('lingnan', 'BUDDIES SCHEME.pdf', 'BUDDIES SCHEME MEET THE TEAM SESSION SPRING 2025 S A M P L E F O O',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/BUDDIES SCHEME.pdf', '1.7MB', '2025-05-02 13:26:35'),
       ('lingnan', 'CampusMap_Colour_2022-02.pdf', 'Legend ɹLegend Pedestrian Path Footpath Footpath Footbridge Drivew',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/CampusMap_Colour_2022-02.pdf', '236.9KB',
        '2025-05-02 13:26:38'),
       ('lingnan', 'Community Service.docx', 'Students are given many chances to engage in various service proje',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/Community Service.docx', '10.9KB',
        '2025-05-02 13:18:57'),
       ('lingnan', 'Consolidated Ordinance.pdf', 'Powers of the University 2-4 Part III The Court 7.',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/Consolidated Ordinance.pdf', '1.3MB',
        '2025-05-02 13:20:09'),
       ('lingnan', 'Cultural Heritage.docx', 'Promoting SDG 11: Preserving Local Cultural Heritage at Lingnan Un',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/Cultural Heritage.docx', '12.7KB',
        '2025-05-02 13:20:11'),
       ('lingnan', 'Global Collaborations.docx', 'Global Collaborations of Lingnan University Introduction Founded i',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/Global Collaborations.docx', '13.3KB',
        '2025-05-02 13:20:14'),
       ('lingnan', 'History.docx', 'From its early days in Guangzhou to its modern incarnation in Hong',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/History.docx', '12.3KB', '2025-05-02 13:20:30'),
       ('lingnan', 'Internationalisation.md', '# Internationalisation **Education for Service** 作育英才 服务社会 --- ## ',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/Internationalisation.md', '2.4KB',
        '2025-05-02 13:20:32'),
       ('lingnan', 'JULAC.docx', 'JULAC Library Card Information Overview To broaden your reach to l',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/JULAC.docx', '13.1KB', '2025-05-02 13:20:34'),
       ('lingnan', 'Letter to Lingnanians.docx', 'As we begin this new academic year, I am excited to see our vibran',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/Letter to Lingnanians.docx', '12.9KB',
        '2025-05-02 13:20:37'),
       ('lingnan', 'LINGNAN UNIVERSITY STATUTES.pdf',
        'The Council may by regulation provide for a ll matters which by th',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/LINGNAN UNIVERSITY STATUTES.pdf', '303.0KB',
        '2025-05-02 13:21:44'),
       ('lingnan', 'Lingnan_Brand.docx', 'Our robust alumni network and We are enhancing our research intens',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/Lingnan_Brand.docx', '37.4KB', '2025-05-02 13:21:46'),
       ('lingnan', 'Lingnan-University-Sports-Day-2025.pdf',
        'Lingnan University Sports Day 2025 Helpers Briefing About Sports D',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/Lingnan-University-Sports-Day-2025.pdf', '777.1KB',
        '2025-05-02 13:25:22'),
       ('lingnan', 'Payment Method outside Hong Kong.pdf',
        'Via Flywire Use Flywire • Lingnan University accepts International',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/Payment Method outside Hong Kong.pdf', '368.2KB',
        '2025-05-02 13:26:44'),
       ('lingnan', 'Payment Methods in Hong Kong.pdf',
        'You may pay your fees at any branch of Bank of East Asia by Cash /',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/Payment Methods in Hong Kong.pdf', '584.2KB',
        '2025-05-02 13:26:47'),
       ('lingnan', 'Programmes list.md', '# Programmes on Offer (2025-26 Intake) ## Faculty of Arts 文学院 | Pr',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/Programmes list.md', '4.5KB', '2025-05-02 13:21:47'),
       ('lingnan', 'Quality Assurance.md', '# Quality Assurance **Education for Service** 作育英才 服务社会 --- ## Com',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/Quality Assurance.md', '3.7KB', '2025-05-02 13:21:50'),
       ('lingnan', 'Rich campus life.md', '--- ## Lingnan University’s Distinctive Campus Life Lingnan Univer',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/Rich campus life.md', '2.3KB', '2025-05-02 13:21:52'),
       ('lingnan', 'selected.docx', 'They are expected to be Independent and Critical Scholars with in ',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/selected.docx', '18.0KB', '2025-05-02 13:25:37'),
       ('lingnan', 'Strategic Brand Pillars.md', 'Optimising Quality Education for the Digital Age We prioritize equ',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/Strategic Brand Pillars.md', '1.9KB',
        '2025-05-02 13:22:49'),
       ('lingnan', 'Syllabus of Elective Courses (AY 2024-25).pdf',
        ': Required course Discipline : Business Prerequisite(s) : Nil Co-r',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/Syllabus of Elective Courses (AY 2024-25).pdf',
        '658.2KB', '2025-05-02 13:27:03'),
       ('lingnan', 'teaching and learning.md', 'We focus on **interactive teaching methods** that encourage studen',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/teaching and learning.md', '2.7KB',
        '2025-05-02 13:22:51'),
       ('lingnan', 'TenancyGuideForNonLocalStudentsInHongKong.md',
        '# Guidelines for renting a building in Hong Kong by non-local stud',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/TenancyGuideForNonLocalStudentsInHongKong.md', '3.9KB',
        '2025-05-02 13:22:55'),
       ('lingnan', 'TPg_Student_Handbook_2024-25.pdf',
        'Student Handbook for Taught Postgraduate Programmes 2024 -25 Table',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/TPg_Student_Handbook_2024-25.pdf', '6.0MB',
        '2025-05-02 13:26:07'),
       ('lingnan', 'UK Programme Itinerary 2025.pdf',
        'Lingnan Universit y At Hertford College, Oxfor d Postgraduate Summ',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/UK Programme Itinerary 2025.pdf', '743.3KB',
        '2025-05-02 13:23:28'),
       ('lingnan', 'Useful Contacts.docx', 'Useful Contacts Admissions and Scholarships Undergraduate Programm',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/Useful Contacts.docx', '12.3KB',
        '2025-05-02 13:22:58'),
       ('lingnan', 'Vision, Mission and Core Values.md',
        '# Lingnan University **作育英才，服务社会** **Education for Service** --- #',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/Vision, Mission and Core Values.md', '2.9KB',
        '2025-05-02 13:23:01'),
       ('lingnan', 'Visual Identity.docx', 'This identity must always be used in its approved form and protect',
        '/RAGnition/code/backend/knowledge_base/lingnan/policies/Visual Identity.docx', '11.9KB',
        '2025-05-02 13:23:04');