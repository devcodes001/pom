# 🍅 FocusFlow

A modern desktop Pomodoro timer and task manager, built with Python and CustomTkinter.
Features a Notion/Linear/Spotify-inspired UI with full **light and dark theme** support.

![Python](https://img.shields.io/badge/python-3.12+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Features

- **Pomodoro Timer** — animated circular progress ring, accurate wall-clock timing on a
  background thread (never freezes the UI), auto long-break every 4th session, fully
  configurable durations.
- **Task Manager** — add/edit/delete, priority levels, deadlines, estimated vs. completed
  Pomodoros, drag-to-reorder, search, and filtering (All / Pending / Completed).
- **Light & Dark Theme** — one-click toggle in the top bar (or `Ctrl+T`), persisted between
  launches, with a customizable accent color. Every screen — including the Matplotlib
  charts — repaints instantly to match.
- **Statistics** — today/weekly/monthly focus time, completed tasks & Pomodoros, current and
  longest streaks, plus daily/weekly/monthly productivity charts.
- **Desktop Notifications & Alarm Sound** — via `plyer` and `pygame`.
- **Daily Goal Tracker** — visual Pomodoro progress in the sidebar (e.g. `🍅🍅🍅🍅○○○○`).
- **SQLite Persistence** — tasks, sessions, and settings are saved automatically and restored
  on every launch.
- **Keyboard Shortcuts** — see below.

## Project Structure

```
FocusFlow/
├── main.py                  # entry point
├── ui/
│   ├── dashboard.py          # main window, navigation, wiring
│   ├── timer_widget.py       # circular Pomodoro timer
│   ├── task_widget.py        # task list + add/edit dialog
│   ├── statistics_widget.py  # stat cards + Matplotlib charts
│   ├── settings_widget.py    # settings panel
│   └── theme.py               # light/dark palettes + ThemeManager
├── core/
│   ├── pomodoro.py            # timer state machine (thread-safe, no UI deps)
│   ├── database.py            # SQLite access layer
│   ├── task_manager.py        # task CRUD/business logic
│   ├── settings.py            # typed settings wrapper
│   └── notifier.py            # desktop notification + alarm sound
├── assets/
│   ├── icon.png
│   └── notification.wav
├── database/
│   └── focusflow.db           # created automatically on first run
├── logs/
│   └── focusflow.log          # created automatically on first run
├── requirements.txt
└── README.md
```

## Installation

1. Install Python 3.12 or newer.
2. From the `FocusFlow/` directory, install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   > **Linux users:** if `tkinter` is not already installed, run
   > `sudo apt-get install python3-tk` first (it ships with the standard Python installer
   > on Windows and macOS).

3. Run the app:

   ```bash
   python main.py
   ```

On first launch, FocusFlow creates `database/focusflow.db` and `logs/focusflow.log`
automatically — no manual setup required.

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Space` | Start / Pause / Resume timer |
| `Ctrl+N` | New task |
| `Ctrl+T` | Toggle light/dark theme |
| `Ctrl+Q` | Quit |

## Building a Windows Executable

FocusFlow is PyInstaller-compatible. From the `FocusFlow/` directory:

```bash
pyinstaller --name FocusFlow ^
  --windowed ^
  --icon assets/icon.png ^
  --add-data "assets;assets" ^
  main.py
```

*(On macOS/Linux, replace `assets;assets` with `assets:assets` and drop the `^` line
continuations — use `\` instead, or put it all on one line.)*

The executable will be created at `dist/FocusFlow/FocusFlow.exe`. The `database/` and
`logs/` folders will be created next to the executable the first time it runs.

**Note:** because the SQLite database and log files are created relative to the
application at runtime, keep `FocusFlow.exe` inside its own `dist/FocusFlow/` folder
rather than moving just the `.exe` file elsewhere.

## Customization

All defaults (theme, accent color, durations, notifications, daily goal, etc.) live in
the **Settings** tab and are persisted to SQLite — no code changes needed for day-to-day
tweaks. Advanced defaults (e.g. the starting accent presets) can be edited in
`ui/settings_widget.py` (`ACCENT_PRESETS`) and `core/database.py` (`DEFAULT_SETTINGS`).

## Architecture Notes

- **`PomodoroEngine`** (`core/pomodoro.py`) has zero UI dependencies and runs on a daemon
  thread, computing remaining time from a `time.monotonic()` deadline rather than counting
  down an integer — so it never visibly drifts even under system load. UI callbacks are
  marshalled back onto the Tk main thread via `.after(0, ...)`.
- **`ThemeManager`** (`ui/theme.py`) is the single source of truth for colors. Every widget
  subscribes to it and repaints on theme change — no widget hardcodes a color.
- **`Database`** (`core/database.py`) is the only module that opens a SQLite connection;
  all other modules go through `TaskManager` or `SettingsManager`.

## License
Absolutely. Since this is your Data Science Lab viva, I’ll cover the viva questions from the programs you showed, starting from the basic Pandas/DataFrame programs and Matplotlib, then KNN → Naive Bayes → Decision Tree. I’ll keep the answers short, simple, and viva-friendly, so you can actually memorize them.

Your uploaded Cycle 2 record contains Program 10: KNN, Program 11: Naive Bayes, and Program 12: Decision Tree.   

DATA SCIENCE LAB VIVA — COMPLETE QUESTIONS & ANSWERS

PART 1 — BASIC PYTHON / DATA SCIENCE

1. What is Data Science?

Answer:
Data Science is the process of collecting, cleaning, analyzing and interpreting data to extract useful information and make decisions.

2. What are the main steps in Data Science?

Answer:

1. Data collection


2. Data cleaning


3. Data exploration


4. Data visualization


5. Model building


6. Model evaluation


7. Prediction/deployment



3. What is a dataset?

Answer:
A dataset is a collection of related data arranged in rows and columns.

4. What is a DataFrame?

Answer:
A DataFrame is a two-dimensional labeled data structure in Pandas consisting of rows and columns.

5. Which library is mainly used for DataFrame operations?

Answer:
Pandas.

6. How do you import Pandas?

import pandas as pd

7. How do you read a CSV file?

df = pd.read_csv("file.csv")

8. How do you display the first 5 rows?

df.head()

9. What does head() do?

Answer:
It displays the first few rows of a DataFrame. By default, it displays 5 rows.

10. How do you display the last 5 rows?

df.tail()

11. How do you find the number of rows and columns?

df.shape

12. What does shape return?

Answer:
It returns a tuple:

(number of rows, number of columns)

13. How do you display column names?

df.columns

14. How do you get information about a DataFrame?

df.info()

15. What does info() show?

Answer:
It shows:

Number of rows

Column names

Non-null values

Data types

Memory usage


16. How do you find statistical information?

df.describe()

17. What does describe() provide?

Answer:
It provides statistics such as:

Count

Mean

Standard deviation

Minimum

Maximum

Quartiles


18. How do you check missing values?

df.isnull().sum()

19. What is a missing value?

Answer:
A missing value is a value that is not present or recorded in the dataset.

20. How can missing values be handled?

Answer:

Remove them

Replace them with mean

Replace them with median

Replace them with mode



---

PART 2 — CHIPOTLE DATASET / PANDAS

Your first question involves reading a Chipotle orders dataset into a DataFrame and performing operations such as displaying rows, sorting item prices, filtering item names, regex replacement and checking data types.

21. How do you read the Chipotle dataset?

df = pd.read_csv("chipotle.csv")

22. How do you display the first 5 records?

print(df.head())

23. How do you sort the DataFrame according to item price?

df.sort_values("item_price")

24. How do you sort in descending order?

df.sort_values("item_price", ascending=False)

25. What is ascending=False?

Answer:
It sorts the values from largest to smallest.

26. How do you display the first 5 rows after sorting?

df.sort_values("item_price", ascending=False).head()

27. How do you filter records containing "chicken"?

df[df["item_name"].str.contains("chicken", case=False)]

28. What is str.contains()?

Answer:
It checks whether a string/column value contains a particular substring.

29. What does case=False do?

Answer:
It makes the search case-insensitive.

For example, it can match:

Chicken
chicken
CHICKEN

30. What is a substring?

Answer:
A substring is a smaller sequence of characters contained within a string.

31. What is regex?

Answer:
Regex means Regular Expression. It is used to search, match or replace patterns in text.

32. How do you remove square brackets using regex?

A possible Pandas approach is:

df["choice_description"] = df["choice_description"].str.replace(r"[\[\]]", "", regex=True)

33. Why do we use regex=True?

Answer:
It tells Pandas that the pattern should be interpreted as a regular expression.

34. Why are [ and ] special in regex?

Answer:
Square brackets have special meanings in regular expressions, so they are escaped or placed appropriately in a pattern when we want to match literal brackets.

35. How do you check the datatype of every column?

df.dtypes

36. What does dtypes return?

Answer:
It returns the data type of each column.

Example:

item_name             object
quantity               int64
item_price           float64

37. What is object in Pandas?

Answer:
It is commonly used for columns containing strings/text.

38. What is int64?

Answer:
It represents integer values.

39. What is float64?

Answer:
It represents decimal/floating-point values.

40. How do you convert a column to float?

df["item_price"] = df["item_price"].astype(float)

41. What does astype() do?

Answer:
It converts a column or Series from one data type to another.

42. Why might item price need conversion?

Answer:
If the price is stored as text/object, mathematical operations and numerical analysis require it to be converted to a numeric type.


---

PART 3 — STUDENT DATA ANALYSIS

Your second lab question involves a student dataset containing:

Name

Department

Mark

Grade


and asks for first 5 records, total students, department counts, students scoring above 75, missing-mark handling, grades, department-wise averages, a bar chart, and CSV export.

43. How do you find the total number of students?

len(df)

or

df.shape[0]

44. What does df.shape[0] mean?

Answer:
It gives the number of rows in the DataFrame.

45. How do you count students in each department?

df["Department"].value_counts()

46. What does value_counts() do?

Answer:
It counts the number of occurrences of each unique value.

Example:

MCA    20
BCA    15
MBA    10

47. How do you find students with marks greater than 75?

df[df["Mark"] > 75]

48. What is Boolean indexing?

Answer:
It is filtering a DataFrame using a condition that produces True or False.

49. How do you calculate average marks?

df["Mark"].mean()

50. What does mean() calculate?

Answer:
It calculates the arithmetic average.

51. How do you find the average department-wise?

df.groupby("Department")["Mark"].mean()

52. What does groupby() do?

Answer:
It groups data based on one or more columns so that operations such as mean, sum or count can be performed on each group.

53. How do you fill missing marks with the class average?

df["Mark"] = df["Mark"].fillna(df["Mark"].mean())

54. What does fillna() do?

Answer:
It replaces missing/NaN values with a specified value.

55. What is NaN?

Answer:
NaN means Not a Number and is commonly used to represent missing numerical data.

56. Why do we fill missing marks with the average?

Answer:
To handle missing data without simply deleting the student record.

57. How can grades be assigned based on marks?

Example:

def grade(mark):
    if mark >= 90:
        return "A+"
    elif mark >= 80:
        return "A"
    elif mark >= 70:
        return "B"
    else:
        return "C"

df["Grade"] = df["Mark"].apply(grade)

58. What does apply() do?

Answer:
It applies a function to values in a Series or DataFrame.

59. Why create a new Grade column?

Answer:
To classify students based on their marks.

60. How do you export students with marks ≥ 90 to CSV?

df[df["Mark"] >= 90].to_csv("high_scorers.csv", index=False)

61. What does to_csv() do?

Answer:
It saves a DataFrame as a CSV file.

62. Why use index=False?

Answer:
It prevents Pandas from writing the DataFrame index as an additional column.


---

PART 4 — MATPLOTLIB

Your graph program specifically asks for different types of graphs using Matplotlib:

Bar chart

Box plot

Bubble chart

Line chart

Histogram

Scatter plot

Pie chart


63. What is Matplotlib?

Answer:
Matplotlib is a Python library used for data visualization and plotting graphs.

64. How do you import Matplotlib?

import matplotlib.pyplot as plt

65. Why do we use pyplot?

Answer:
pyplot provides functions for creating and controlling plots.


---

LINE CHART

66. What is a line chart?

Answer:
A line chart represents data points connected by lines and is commonly used to show trends over time.

67. How do you create a line chart?

plt.plot(x, y)
plt.show()

68. What does plt.show() do?

Answer:
It displays the graph.


---

BAR CHART

69. What is a bar chart?

Answer:
A bar chart represents categorical data using rectangular bars.

70. How do you create a bar chart?

plt.bar(x, y)
plt.show()

71. When is a bar chart useful?

Answer:
For comparing values between different categories.

Example:

MCA → 40
BCA → 30
MBA → 20


---

HISTOGRAM

72. What is a histogram?

Answer:
A histogram shows the distribution of numerical data using intervals called bins.

73. How do you create a histogram?

plt.hist(data)
plt.show()

74. What is a bin?

Answer:
A bin is an interval or range used to group numerical values in a histogram.

75. Difference between bar chart and histogram?

Answer:

Bar Chart	Histogram

Categorical data	Numerical data
Bars represent categories	Bars represent intervals
Usually gaps between bars	Usually bars touch



---

SCATTER PLOT

76. What is a scatter plot?

Answer:
A scatter plot represents individual data points to show the relationship between two numerical variables.

77. How do you create it?

plt.scatter(x, y)
plt.show()

78. What can a scatter plot show?

Answer:
It can show relationships, patterns, clusters and possible correlation between variables.


---

PIE CHART

79. What is a pie chart?

Answer:
A pie chart represents data as parts of a whole using sectors.

80. How do you create a pie chart?

plt.pie(values, labels=labels)
plt.show()

81. When is a pie chart useful?

Answer:
When we want to show the proportion or percentage of categories relative to a whole.


---

BOX PLOT

82. What is a box plot?

Answer:
A box plot summarizes the distribution of numerical data using the minimum, Q1, median, Q3 and maximum, while also indicating possible outliers.

83. How do you create a box plot?

plt.boxplot(data)
plt.show()

84. What is an outlier?

Answer:
An outlier is a value that is unusually far from the other observations.


---

BUBBLE CHART

85. What is a bubble chart?

Answer:
A bubble chart is a scatter plot where the size of each point represents an additional variable.

86. How can you create a bubble chart?

plt.scatter(x, y, s=size)
plt.show()

87. What does s represent?

Answer:
It represents the size of the bubbles/markers.


---

PART 5 — K-NEAREST NEIGHBOR (KNN)

Your Cycle 2 Program 10 uses the Iris dataset, splits it into training and testing data, creates KNeighborsClassifier(n_neighbors=3), trains it, predicts test values, calculates accuracy, and predicts a sample. 

88. What is KNN?

Answer:
KNN stands for K-Nearest Neighbors. It is a supervised machine learning algorithm used mainly for classification.

89. Is KNN supervised or unsupervised?

Answer:
Supervised learning.

90. Why is it called K-Nearest Neighbors?

Answer:
Because it classifies a new data point based on its K closest training data points.

91. What is K?

Answer:
K is the number of nearest neighbors considered for prediction.

92. In your program, what is K?

K = 3

because:

KNeighborsClassifier(n_neighbors=3)

93. What happens when K = 3?

Answer:
The algorithm looks at the 3 nearest data points and uses them to determine the class.

94. How does KNN classify a new point?

Answer:

1. Calculate distance from the new point to training points.


2. Select K nearest points.


3. Check their classes.


4. Assign the majority class.



95. What distance is commonly used in KNN?

Answer:
Euclidean distance is commonly used.

96. What is Euclidean distance?

For two points:

\[
d=\sqrt{(x_1-x_2)^2+(y_1-y_2)^2}
\]

For multiple dimensions:

\[
d=\sqrt{\sum_{i=1}^{n}(x_i-y_i)^2}
\]

97. Why should features sometimes be scaled in KNN?

Answer:
Because KNN depends on distance. A feature with a much larger numerical scale can dominate the distance calculation.

98. Is KNN a lazy learning algorithm?

Answer:
Yes. KNN is called a lazy learner because it does not build an explicit model during training; it mainly stores the training data and performs computation during prediction.

99. What is the disadvantage of choosing a very small K?

Answer:
It can be sensitive to noise and may overfit.

100. What happens if K is very large?

Answer:
The model can become less sensitive to local patterns and may underfit.

101. What dataset is used in your KNN program?

Answer:
The Iris dataset.

102. What are the classes in the Iris dataset?

Answer:

Setosa

Versicolor

Virginica


103. How many features are in the Iris dataset?

Answer:
Four:

Sepal length

Sepal width

Petal length

Petal width


104. What does train_test_split() do?

Answer:
It divides the dataset into training and testing sets.

105. What is test_size=0.3?

Answer:
It means 30% of the data is used for testing and 70% for training.

106. What is random_state=1?

Answer:
It fixes the random split so that the same split can be reproduced.

107. What does fit() do?

c_knn.fit(x_train, y_train)

Answer:
It trains/prepares the KNN classifier using the training data.

108. What does predict() do?

y_pred = c_knn.predict(x_test)

Answer:
It predicts the class labels for new/test data.

109. What accuracy did your KNN program produce?

Answer:
The record shows:

0.9777777777777777, approximately 97.78%. 

110. What was predicted for the sample?

sample = [[2,2,3,3]]

Answer:
The program predicted versicolor. 


---

PART 6 — NAIVE BAYES

Your Program 11 uses a patient dataset with Chills, Running nose, Headache, Fever and Has flu, and uses CategoricalNB after encoding categorical variables. 

111. What is Naive Bayes?

Answer:
Naive Bayes is a supervised classification algorithm based on Bayes' theorem.

112. Why is it called "Naive"?

Answer:
Because it assumes that the features are conditionally independent given the class.

113. Is Naive Bayes supervised or unsupervised?

Answer:
Supervised.

114. What is Bayes' theorem?

\[
P(A|B)=\frac{P(B|A)P(A)}{P(B)}
\]

115. What does Bayes' theorem calculate?

Answer:
It calculates the probability of an event based on prior knowledge and observed evidence.

116. What is prior probability?

Answer:
Prior probability is the probability of a class before considering the current evidence.

117. What is posterior probability?

Answer:
Posterior probability is the probability of a class after considering the observed features.

118. What is likelihood?

Answer:
Likelihood is the probability of observing the features given a particular class.

119. What is evidence?

Answer:
Evidence is the overall probability of the observed features.

120. What is the main assumption of Naive Bayes?

Answer:
Features are assumed to be conditionally independent given the class.

121. Which Naive Bayes classifier is used in your program?

Answer:

CategoricalNB()

It is suitable for categorical features. 

122. Why do we encode the categorical data?

Answer:
Machine learning algorithms generally require numerical input, so categorical values such as Y, N, mild, etc. are converted into numbers.

123. Which encoder is used?

LabelEncoder()

124. What does LabelEncoder do?

Answer:
It converts categorical labels into numerical values.

For example:

N → 0
Y → 1

125. What is the target variable in this problem?

Answer:
Has flu.

126. What are the input features?

Answer:

Chills

Running nose

Headache

Fever


127. What is the test case?

Chills = Y
Running nose = N
Headache = mild
Fever = Y

The record explicitly uses this test instance. 

128. What was the prediction in the program?

Answer:
The program's output shows:

Prediction: Y

meaning the classifier predicted that the person has flu. 

129. What accuracy is shown in the record?

Answer:
0.75, or 75%. 

130. What is predict_proba()?

Answer:
It returns the predicted probability for each class.

131. Difference between predict() and predict_proba()?

Answer:

predict() → gives the predicted class.

predict_proba() → gives the probability of each class.


---

PART 7 — DECISION TREE

Your Program 12 implements Decision Tree classification using the Iris dataset and compares Gini, Entropy, and Entropy + min_samples_split=50. 

132. What is a Decision Tree?

Answer:
A Decision Tree is a supervised machine learning algorithm that makes decisions using a tree-like structure of nodes, branches and leaves.

133. Is Decision Tree supervised or unsupervised?

Answer:
Supervised learning.

134. What are the main components of a Decision Tree?

Answer:

1. Root node


2. Internal/decision nodes


3. Branches


4. Leaf nodes



135. What is the root node?

Answer:
The root is the first/topmost decision node in the tree.

136. What is an internal node?

Answer:
An internal node represents a decision or test on a feature.

137. What is a leaf node?

Answer:
A leaf node represents the final prediction/class.

138. What is a branch?

Answer:
A branch represents the outcome of a decision.


---

GINI INDEX

139. What is Gini Index?

Answer:
Gini Index measures the impurity of a node.

140. What is impurity?

Answer:
Impurity indicates how mixed the classes are in a node.

141. Formula for Gini Index?

\[
Gini = 1-\sum_{i=1}^{n}p_i^2
\]

where \(p_i\) is the probability of class \(i\).

142. What does Gini = 0 mean?

Answer:
The node is pure; all observations belong to one class.

143. What is the default criterion in your Decision Tree code?

Answer:
The code uses:

DecisionTreeClassifier()

which uses the default criterion in scikit-learn for this classifier. The program then explicitly compares it with entropy. 


---

ENTROPY

144. What is Entropy?

Answer:
Entropy is a measure of impurity or uncertainty in a dataset.

145. Formula for entropy?

\[
Entropy=-\sum p_i\log_2(p_i)
\]

146. What does entropy = 0 mean?

Answer:
The node is completely pure.

147. What does high entropy mean?

Answer:
It means the classes are more mixed or uncertain.

148. What is Information Gain?

Answer:
Information Gain measures how much a split reduces entropy.

149. Formula for Information Gain?

\[
IG = Entropy(parent) - Weighted\ Entropy(children)
\]

150. Which split is preferred?

Answer:
A split that gives higher information gain is preferred when using entropy.


---

GINI VS ENTROPY

151. Difference between Gini and Entropy?

Gini	Entropy

Measures impurity	Measures uncertainty
\(1-\sum p_i^2\)	\(-\sum p_i\log_2p_i\)
Computationally simpler	Uses logarithm
Commonly used in Decision Trees	Used when criterion is set to entropy


152. How do you use entropy in sklearn?

DecisionTreeClassifier(criterion='entropy')

Your lab program uses exactly this approach. 


---

DECISION TREE PARAMETERS

153. What is criterion?

Answer:
It specifies the function used to measure the quality of a split, such as Gini impurity or entropy.

154. What is min_samples_split?

Answer:
It specifies the minimum number of samples required to split an internal node.

155. What does this mean?

min_samples_split=50

Answer:
A node must have at least 50 samples to be considered for splitting.

156. Why do we use min_samples_split?

Answer:
It can restrict unnecessary splitting and help control overfitting.

157. What is overfitting?

Answer:
Overfitting occurs when a model learns the training data too closely and performs poorly on unseen data.

158. What is underfitting?

Answer:
Underfitting occurs when a model is too simple to capture the important patterns in the data.


---

DECISION TREE CODE VIVA

159. Which dataset is used?

Answer:
Iris dataset. 

160. How many records are there in Iris?

Answer:
150 records.

The program output shows:

Data shape: (150, 4)



161. How many features are there?

Answer:
4 features.

162. What are the four features?

Answer:

1. Sepal length


2. Sepal width


3. Petal length


4. Petal width





163. How many classes?

Answer:
3 classes:

Setosa

Versicolor

Virginica


164. What is the target?

Answer:
The Iris species/class.

165. What is test_size=0.25?

Answer:
25% of the dataset is used for testing and 75% for training. 

166. What is random_state=50?

Answer:
It makes the random train-test split reproducible.

167. Why are there three Decision Tree models in your program?

Answer:
To compare:

1. Gini


2. Entropy


3. Entropy with min_samples_split=50





168. What was the test accuracy using Gini?

Answer:
0.9473684210526315, approximately 94.74%. 

169. What was the test accuracy using Entropy?

Answer:
0.9473684210526315, approximately 94.74%. 

170. What was the test accuracy with entropy and min_samples_split=50?

Answer:
0.9473684210526315, approximately 94.74%. 

171. Why was training accuracy 1.0 for the first two models?

Answer:
The unrestricted Decision Trees were able to classify the training samples perfectly, resulting in 100% training accuracy. The test accuracy was lower, which illustrates the difference between training and unseen data performance. 

172. What does plot_tree() do?

plot_tree(clf_entropy)

Answer:
It visualizes the trained Decision Tree.

173. Why are feature_names used?

feature_names=data.feature_names

Answer:
They display meaningful feature names in the tree instead of generic feature numbers.

174. Why are class_names used?

class_names=data.target_names

Answer:
They display the actual class names in the tree.


---

VERY IMPORTANT "WHY" QUESTIONS

These are the questions examiners often ask after you explain your program.

175. Why do we split data into training and testing data?

Answer:
Training data is used to train the model, while test data is used to evaluate how well the model performs on unseen data.

176. Why do we calculate accuracy?

Answer:
To measure how many predictions are correct.

177. What is accuracy?

\[
Accuracy=\frac{Correct\ Predictions}{Total\ Predictions}
\]

178. What is classification?

Answer:
Classification is predicting a categorical class/label.

Example:

Flower → Setosa
Patient → Flu

179. What is regression?

Answer:
Regression predicts a continuous numerical value.

Example:

House price = ₹50 lakh

180. Difference between classification and regression?

Answer:

Classification → category

Regression → numerical value


---

MACHINE LEARNING GENERAL VIVA

181. What is Machine Learning?

Answer:
Machine Learning is a method where computers learn patterns from data and use them to make predictions or decisions.

182. What are the main types of Machine Learning?

Answer:

1. Supervised learning


2. Unsupervised learning


3. Reinforcement learning



183. What is supervised learning?

Answer:
Learning using data that has input features and known target labels.

184. Give examples of supervised algorithms.

Answer:

KNN

Naive Bayes

Decision Tree

SVM

Linear Regression


185. What is unsupervised learning?

Answer:
Learning patterns from data without predefined target labels.

186. Give examples.

Answer:

K-Means clustering

Hierarchical clustering


187. What is a feature?

Answer:
A feature is an input variable used by a machine learning model.

Example:

Age
Income
Height

188. What is a target?

Answer:
The target is the output variable that the model tries to predict.

189. What is training data?

Answer:
Data used to train the machine learning model.

190. What is testing data?

Answer:
Data used to evaluate the trained model.


---

SCIKIT-LEARN VIVA

191. What is Scikit-learn?

Answer:
Scikit-learn is a Python machine learning library containing algorithms and tools for data preprocessing, training and evaluation.

192. Why do we use sklearn?

Answer:
It provides ready-to-use machine learning algorithms and evaluation functions.

193. What is train_test_split()?

Answer:
It splits data into training and testing subsets.

194. What is fit()?

Answer:
It trains the model using the training data.

195. What is predict()?

Answer:
It generates predictions for new data.

196. What is accuracy_score()?

Answer:
It calculates the proportion of correctly predicted samples.

197. What is metrics?

Answer:
It is a Scikit-learn module containing functions for evaluating machine learning models.


---

🔥 MOST LIKELY 25 VIVA QUESTIONS TO MEMORIZE FIRST

If your teacher gives you only 2–5 minutes, concentrate on these:

1. What is Data Science?


2. What is a DataFrame?


3. What is Pandas?


4. What does head() do?


5. What does shape return?


6. What does groupby() do?


7. What does value_counts() do?


8. What is Matplotlib?


9. Difference between bar chart and histogram?


10. What is a scatter plot?


11. What is KNN?


12. Why is KNN called lazy learning?


13. What is K in KNN?


14. What happens if K is too small/large?


15. What is Naive Bayes?


16. Why is it called Naive?


17. State Bayes' theorem.


18. What is LabelEncoder?


19. What is a Decision Tree?


20. What is Gini Index?


21. What is Entropy?


22. Difference between Gini and Entropy?


23. What is min_samples_split?


24. What is overfitting?


25. What is the difference between training and testing data?



⭐ One-line memory sheet

Pandas → Data manipulation
DataFrame → Rows + columns
head() → First 5 rows
shape → Rows, columns
dtypes → Data types
groupby() → Group data
value_counts() → Count categories
fillna() → Fill missing values
to_csv() → Export CSV
Matplotlib → Visualization
Histogram → Distribution
Scatter → Relationship
Bar → Category comparison
Pie → Proportion
Box plot → Distribution + outliers
KNN → Nearest neighbours
Naive Bayes → Bayes theorem + independence assumption
Decision Tree → Tree-based decisions
Gini → Impurity
Entropy → Uncertainty
Information Gain → Reduction in entropy
min_samples_split → Minimum samples needed to split
fit() → Train
predict() → Predict
accuracy_score() → Accuracy

Most important for your viva: be ready to explain every line of your program, especially train_test_split, fit, predict, n_neighbors, LabelEncoder, CategoricalNB, criterion, min_samples_split, groupby, fillna, and the different Matplotlib functions.
MIT — use it, fork it, ship it.
