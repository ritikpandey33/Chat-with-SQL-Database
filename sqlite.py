import sqlite3

# Connect to SQLite database
connection = sqlite3.connect("student.db")
cursor = connection.cursor()

# Drop tables if they already exist (to recreate fresh)
cursor.executescript("""
DROP TABLE IF EXISTS STUDENT;
DROP TABLE IF EXISTS CLASS;
DROP TABLE IF EXISTS TEACHER;
DROP TABLE IF EXISTS SUBJECT;
DROP TABLE IF EXISTS MARKS;
""")

# Create tables
cursor.executescript("""
CREATE TABLE CLASS (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    section TEXT NOT NULL
);

CREATE TABLE STUDENT (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    dob TEXT,
    gender TEXT,
    class_id INTEGER,
    FOREIGN KEY(class_id) REFERENCES CLASS(id)
);

CREATE TABLE TEACHER (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    subject_specialization TEXT
);

CREATE TABLE SUBJECT (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    teacher_id INTEGER,
    FOREIGN KEY(teacher_id) REFERENCES TEACHER(id)
);

CREATE TABLE MARKS (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    subject_id INTEGER,
    marks INTEGER,
    FOREIGN KEY(student_id) REFERENCES STUDENT(id),
    FOREIGN KEY(subject_id) REFERENCES SUBJECT(id)
);
""")

# Insert sample data
# Classes
cursor.execute("INSERT INTO CLASS (name, section) VALUES ('Data Science', 'A')")
cursor.execute("INSERT INTO CLASS (name, section) VALUES ('Data Science', 'B')")
cursor.execute("INSERT INTO CLASS (name, section) VALUES ('DevOps', 'A')")

# Teachers
cursor.execute("INSERT INTO TEACHER (name, subject_specialization) VALUES ('Dr. Smith', 'ML')")
cursor.execute("INSERT INTO TEACHER (name, subject_specialization) VALUES ('Prof. Jane', 'Cloud')")
cursor.execute("INSERT INTO TEACHER (name, subject_specialization) VALUES ('Mr. Alan', 'Python')")

# Subjects
cursor.execute("INSERT INTO SUBJECT (name, teacher_id) VALUES ('Machine Learning', 1)")
cursor.execute("INSERT INTO SUBJECT (name, teacher_id) VALUES ('Cloud Computing', 2)")
cursor.execute("INSERT INTO SUBJECT (name, teacher_id) VALUES ('Python Programming', 3)")

# Students
cursor.execute("INSERT INTO STUDENT (name, dob, gender, class_id) VALUES ('Krish', '2002-01-10', 'M', 1)")
cursor.execute("INSERT INTO STUDENT (name, dob, gender, class_id) VALUES ('John', '2001-11-23', 'M', 2)")
cursor.execute("INSERT INTO STUDENT (name, dob, gender, class_id) VALUES ('Anita', '2003-05-16', 'F', 1)")
cursor.execute("INSERT INTO STUDENT (name, dob, gender, class_id) VALUES ('Jacob', '2000-09-02', 'M', 3)")
cursor.execute("INSERT INTO STUDENT (name, dob, gender, class_id) VALUES ('Priya', '2002-12-05', 'F', 1)")

# Marks
cursor.execute("INSERT INTO MARKS (student_id, subject_id, marks) VALUES (1, 1, 85)")
cursor.execute("INSERT INTO MARKS (student_id, subject_id, marks) VALUES (1, 2, 78)")
cursor.execute("INSERT INTO MARKS (student_id, subject_id, marks) VALUES (2, 1, 92)")
cursor.execute("INSERT INTO MARKS (student_id, subject_id, marks) VALUES (3, 3, 88)")
cursor.execute("INSERT INTO MARKS (student_id, subject_id, marks) VALUES (4, 2, 45)")
cursor.execute("INSERT INTO MARKS (student_id, subject_id, marks) VALUES (5, 1, 75)")

# Show sample output
print("Sample STUDENT records:")
for row in cursor.execute("SELECT * FROM STUDENT"):
    print(row)

# Commit and close
connection.commit()
connection.close()
