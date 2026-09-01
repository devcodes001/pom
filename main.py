"""
main.py
FocusFlow entry point. Sets up logging, initializes the database, and
launches the CustomTkinter dashboard window.
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from core.database import Database, DEFAULT_DB_PATH
from ui.dashboard import Dashboard

LOG_DIR = Path(__file__).resolve().parent / "logs"


def configure_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / "focusflow.log"

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )

    file_handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARNING)

    root_logger = logging.getLogger("focusflow")
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


def main() -> None:
    configure_logging()
    logger = logging.getLogger("focusflow.main")
    logger.info("Starting FocusFlow")

    try:
        db = Database(DEFAULT_DB_PATH)
    except Exception:
        logger.exception("Failed to initialize database")
        raise

    try:
        app = Dashboard(db)
        app.mainloop()
    except Exception:
        logger.exception("Unhandled exception in main loop")
        raise
    finally:
        logger.info("FocusFlow shut down")


if __name__ == "__main__":
    main()Absolutely 👍 Below is complete Python/Jupyter Notebook code for all the programs shown in the images. I’ve kept it simple and practical for a lab exam, with separate cells you can copy directly into Jupyter Notebook/Google Colab.


---

PROGRAM 1 — Chipotle Dataset

Aim

Read a dataset of Chipotle orders into a DataFrame and perform the given operations.

Cell 1 — Import libraries and load dataset

import pandas as pd

# Load the Chipotle dataset
df = pd.read_csv("chipotle.csv")

# Display dataset
df.head()

> If your file has a different name, replace "chipotle.csv" with your CSV filename.




---

a) Display the first 5 rows

print(df.head(5))


---

b) Sort based on item_price in descending order and display first 5 rows

# Convert item_price to numeric
df["item_price"] = df["item_price"].str.replace("$", "", regex=False).astype(float)

# Sort in descending order
sorted_df = df.sort_values(by="item_price", ascending=False)

# Display first 5 rows
print(sorted_df.head(5))


---

c) Find records where item name contains "chicken"

chicken_items = df[df["item_name"].str.contains("chicken", case=False, na=False)]

print(chicken_items)


---

d) Remove square brackets from choice_description using regex

df["choice_description"] = df["choice_description"].str.replace(
    r"[\[\]]", "", regex=True
)

print(df.head())

If you want to remove both [ and ]:

df["choice_description"] = df["choice_description"].str.replace(
    r"[\[\]]", "", regex=True
)


---

e) Display datatype of each column

print(df.dtypes)

Alternative:

df.info()


---

f) Replace $ in item_price and convert to float

If you have not already done this in part b:

df["item_price"] = df["item_price"].str.replace("$", "", regex=False)

df["item_price"] = df["item_price"].astype(float)

print(df["item_price"].head())
print(df.dtypes)

Complete Program 1

import pandas as pd

# Load dataset
df = pd.read_csv("chipotle.csv")

# a) Display first 5 rows
print("First 5 rows:")
print(df.head(5))

# f) Remove $ and convert item_price to float
df["item_price"] = df["item_price"].str.replace("$", "", regex=False)
df["item_price"] = df["item_price"].astype(float)

# b) Sort item_price in descending order
print("\nTop 5 expensive items:")
print(df.sort_values(by="item_price", ascending=False).head(5))

# c) Find items containing chicken
print("\nItems containing chicken:")
print(df[df["item_name"].str.contains("chicken", case=False, na=False)])

# d) Remove square brackets
df["choice_description"] = df["choice_description"].str.replace(
    r"[\[\]]", "", regex=True
)

# e) Display datatypes
print("\nData types:")
print(df.dtypes)


---

PROGRAM 2 — Student Data Analysis

Aim

Create a DataFrame for student data containing:

Name

Department

Mark

Grade


and perform the required operations.


---

Cell 1 — Create/Load Dataset

If you already have a CSV file:

import pandas as pd

df = pd.read_csv("students.csv")

print(df.head())

If you need to create the dataset yourself, use:

import pandas as pd

data = {
    "Name": [
        "Arun", "Anu", "Rahul", "Meera", "Akhil",
        "Dev", "Amal", "Neha", "Vishnu", "Asha"
    ],
    "Department": [
        "MCA", "MBA", "MCA", "BCA", "MBA",
        "MCA", "BCA", "MBA", "MCA", "BCA"
    ],
    "Mark": [
        85, 72, 91, 68, 95,
        78, None, 88, 92, 75
    ]
}

df = pd.DataFrame(data)

print(df)


---

a) Display first 5 records and total number of students

print("First 5 records:")
print(df.head(5))

print("\nTotal number of students:")
print(len(df))

Another simple method:

print(df.shape[0])


---

b) Display count of students in each department

print(df["Department"].value_counts())

Or:

department_count = df.groupby("Department").size()

print(department_count)


---

c) Find students who scored more than 75 marks

students_above_75 = df[df["Mark"] > 75]

print(students_above_75)


---

d) Fill missing marks with average marks of the class

average_mark = df["Mark"].mean()

df["Mark"] = df["Mark"].fillna(average_mark)

print(df)

If you want to see the average:

print("Average mark:", average_mark)


---

e) Add a new Grade column based on marks

Example grading:

90 and above → A+

80–89 → A

70–79 → B

60–69 → C

Below 60 → D


def calculate_grade(mark):
    if mark >= 90:
        return "A+"
    elif mark >= 80:
        return "A"
    elif mark >= 70:
        return "B"
    elif mark >= 60:
        return "C"
    else:
        return "D"

df["Grade"] = df["Mark"].apply(calculate_grade)

print(df)


---

f) Display department-wise average marks

department_average = df.groupby("Department")["Mark"].mean()

print(department_average)

For rounded values:

department_average = df.groupby("Department")["Mark"].mean().round(2)

print(department_average)


---

g) Plot a bar chart showing number of students per department

import matplotlib.pyplot as plt

department_count = df["Department"].value_counts()

department_count.plot(kind="bar")

plt.xlabel("Department")
plt.ylabel("Number of Students")
plt.title("Number of Students per Department")

plt.show()


---

h) Export students with marks greater than or equal to 90 to CSV

top_students = df[df["Mark"] >= 90]

top_students.to_csv("students_90_and_above.csv", index=False)

print("Students with marks >= 90:")
print(top_students)

print("\nFile exported successfully.")


---

COMPLETE PROGRAM 2

You can use this as one complete notebook program:

import pandas as pd
import matplotlib.pyplot as plt

# Create student dataset
data = {
    "Name": [
        "Arun", "Anu", "Rahul", "Meera", "Akhil",
        "Dev", "Amal", "Neha", "Vishnu", "Asha"
    ],
    "Department": [
        "MCA", "MBA", "MCA", "BCA", "MBA",
        "MCA", "BCA", "MBA", "MCA", "BCA"
    ],
    "Mark": [
        85, 72, 91, 68, 95,
        78, None, 88, 92, 75
    ]
}

df = pd.DataFrame(data)

# a) First 5 records and total students
print("First 5 records:")
print(df.head())

print("\nTotal number of students:", len(df))

# b) Count students in each department
print("\nStudents in each department:")
print(df["Department"].value_counts())

# c) Students scoring more than 75
print("\nStudents scoring more than 75:")
print(df[df["Mark"] > 75])

# d) Fill missing marks with average
average_mark = df["Mark"].mean()
df["Mark"] = df["Mark"].fillna(average_mark)

print("\nAverage mark:", average_mark)

# e) Add Grade column
def calculate_grade(mark):
    if mark >= 90:
        return "A+"
    elif mark >= 80:
        return "A"
    elif mark >= 70:
        return "B"
    elif mark >= 60:
        return "C"
    else:
        return "D"

df["Grade"] = df["Mark"].apply(calculate_grade)

print("\nStudent data with grades:")
print(df)

# f) Department-wise average marks
print("\nDepartment-wise average marks:")
print(df.groupby("Department")["Mark"].mean().round(2))

# g) Bar chart
department_count = df["Department"].value_counts()

department_count.plot(kind="bar")

plt.xlabel("Department")
plt.ylabel("Number of Students")
plt.title("Number of Students per Department")
plt.show()

# h) Export students with marks >= 90
top_students = df[df["Mark"] >= 90]

top_students.to_csv("students_90_and_above.csv", index=False)

print("\nStudents with marks >= 90:")
print(top_students)

print("\nCSV file exported successfully.")


---

PROGRAM 3 — Matplotlib Graphs

Aim

Write a program using Matplotlib to analyze data using:

1. Bar chart


2. Box plot


3. Bubble chart


4. Line chart


5. Histogram


6. Scatter plot


7. Pie chart




---

Cell 1 — Import libraries and create data

import matplotlib.pyplot as plt

# Sample data
students = ["A", "B", "C", "D", "E"]
marks = [85, 72, 90, 65, 78]

subjects = ["Python", "Java", "DBMS", "Networks", "AI"]
scores = [85, 72, 90, 65, 78]


---

1. Bar Chart

plt.bar(students, marks)

plt.xlabel("Students")
plt.ylabel("Marks")
plt.title("Student Marks")

plt.show()


---

2. Box Plot

plt.boxplot(marks)

plt.ylabel("Marks")
plt.title("Marks Distribution")

plt.show()


---

3. Bubble Chart

A bubble chart is basically a scatter plot where the size of the points represents another value.

x = [1, 2, 3, 4, 5]
y = [85, 72, 90, 65, 78]
sizes = [500, 300, 700, 250, 450]

plt.scatter(x, y, s=sizes, alpha=0.6)

plt.xlabel("Student Number")
plt.ylabel("Marks")
plt.title("Bubble Chart")

plt.show()


---

4. Line Chart

plt.plot(subjects, scores, marker="o")

plt.xlabel("Subjects")
plt.ylabel("Marks")
plt.title("Subject-wise Marks")

plt.show()


---

5. Histogram

plt.hist(marks, bins=5)

plt.xlabel("Marks")
plt.ylabel("Frequency")
plt.title("Distribution of Marks")

plt.show()


---

6. Scatter Plot

study_hours = [2, 3, 4, 5, 6]
marks = [60, 65, 72, 85, 92]

plt.scatter(study_hours, marks)

plt.xlabel("Study Hours")
plt.ylabel("Marks")
plt.title("Study Hours vs Marks")

plt.show()


---

7. Pie Chart

departments = ["MCA", "MBA", "BCA"]
students_count = [40, 30, 20]

plt.pie(
    students_count,
    labels=departments,
    autopct="%1.1f%%"
)

plt.title("Students by Department")

plt.show()


---

COMPLETE PROGRAM 3

You can copy this entire thing into one Jupyter Notebook cell:

import matplotlib.pyplot as plt

# -----------------------------
# DATA
# -----------------------------

students = ["A", "B", "C", "D", "E"]
marks = [85, 72, 90, 65, 78]

subjects = ["Python", "Java", "DBMS", "Networks", "AI"]
scores = [85, 72, 90, 65, 78]


# -----------------------------
# 1. BAR CHART
# -----------------------------

plt.bar(students, marks)

plt.xlabel("Students")
plt.ylabel("Marks")
plt.title("Student Marks")

plt.show()


# -----------------------------
# 2. BOX PLOT
# -----------------------------

plt.boxplot(marks)

plt.ylabel("Marks")
plt.title("Marks Distribution")

plt.show()


# -----------------------------
# 3. BUBBLE CHART
# -----------------------------

x = [1, 2, 3, 4, 5]
y = [85, 72, 90, 65, 78]
sizes = [500, 300, 700, 250, 450]

plt.scatter(x, y, s=sizes, alpha=0.6)

plt.xlabel("Student Number")
plt.ylabel("Marks")
plt.title("Bubble Chart")

plt.show()


# -----------------------------
# 4. LINE CHART
# -----------------------------

plt.plot(subjects, scores, marker="o")

plt.xlabel("Subjects")
plt.ylabel("Marks")
plt.title("Subject-wise Marks")

plt.show()


# -----------------------------
# 5. HISTOGRAM
# -----------------------------

plt.hist(marks, bins=5)

plt.xlabel("Marks")
plt.ylabel("Frequency")
plt.title("Distribution of Marks")

plt.show()


# -----------------------------
# 6. SCATTER PLOT
# -----------------------------

study_hours = [2, 3, 4, 5, 6]
study_marks = [60, 65, 72, 85, 92]

plt.scatter(study_hours, study_marks)

plt.xlabel("Study Hours")
plt.ylabel("Marks")
plt.title("Study Hours vs Marks")

plt.show()


# -----------------------------
# 7. PIE CHART
# -----------------------------

departments = ["MCA", "MBA", "BCA"]
students_count = [40, 30, 20]

plt.pie(
    students_count,
    labels=departments,
    autopct="%1.1f%%"
)

plt.title("Students by Department")

plt.show()


---

⭐ Quick lab-exam version

Remember these 7 basic Matplotlib commands:

plt.bar(x, y)          # Bar chart

plt.boxplot(data)      # Box plot

plt.scatter(x, y)      # Scatter / Bubble chart

plt.plot(x, y)         # Line chart

plt.hist(data)         # Histogram

plt.pie(data, labels=labels)  # Pie chart

plt.show()             # Display graph

And the most important Pandas commands from the first two programs:

pd.read_csv("file.csv")

df.head()

df.sort_values()

df[df["column"] > value]

df["column"].str.contains("text")

df["column"].str.replace()

df.dtypes

df["column"].astype(float)

df["column"].fillna(df["column"].mean())

df.groupby("Department")["Mark"].mean()

df["Department"].value_counts()

df.to_csv("output.csv", index=False)

These cover essentially all the operations shown in your three uploaded question sheets.
