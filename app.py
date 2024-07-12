from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
import csv
import json
import plotly.graph_objs as go
import plotly.offline as pyo
import random
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from mcqs import get_random_questions_bio
from mcqs import get_random_questions_chem
from mcqs import get_random_questions_phy
from mcqs import get_random_questions_logical
from mcqs import get_random_questions_eng

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
db = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="123",
    database="e"
)
cursor = db.cursor(dictionary=True)

# Path to the CSV files
CSV_FILE_PATH_bio = 'CSV/biology.csv'
CSV_FILE_PATH_chem = 'CSV/chemistry.csv'
CSV_FILE_PATH_eng = 'CSV/english.csv'
CSV_FILE_PATH_logical = 'CSV/logical.csv'
CSV_FILE_PATH_phy = 'CSV/physics.csv'

#*************************************************************************************
@app.route('/')
def home():
    if 'username' in session:
        return render_template('Dashboard.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/Refresh')
def dashboard():
    return render_template('dashboard.html', username=session['username'])

@app.route('/back')
def dash():
    return render_template('dashboard.html', username=session['username'])
#*********************************LOGIN/SIGNUP*********************************************************
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM user WHERE username=%s", (username,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            session['user_id'] = user['ID']  # Assuming 'ID' is the column name for the user ID
            return redirect(url_for('home'))
        return "Invalid credentials"
    return render_template('LOGIN/login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        
        try:
            cursor.execute("INSERT INTO user (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
            db.commit()
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            return f"Error: {err}"
    
    return render_template('LOGIN/signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('login'))



#*******************************************************************************************************
#*********************************BIOLOGY**************************************************************
@app.route('/BiologyQuiz')
def BIO():
    return render_template('MCQS/BiologyQuiz.html')

@app.route('/BIO_questions', methods=['GET'])
def BIO_get_questions():
    random_questions = get_random_questions_bio(CSV_FILE_PATH_bio, 20)
    return jsonify(random_questions)

@app.route('/BIO_submit', methods=['POST'])
def BIO_submit_answer():
    data = request.json
    current_question_index = data['currentQuestionIndex']
    selected_answer = data['selectedAnswer']

    questions = get_random_questions_bio(CSV_FILE_PATH_bio, 20)  # Get the same set of random questions
    is_correct = any(answer['text'] == selected_answer and answer['correct'] for answer in questions[current_question_index]['answers'])
    
    response = {"correct": is_correct}
    if current_question_index + 1 < len(questions):
        next_question = questions[current_question_index + 1]
        response["nextQuestion"] = next_question
    else:
        response["end"] = True
    return jsonify(response)

@app.route('/save_score', methods=['POST'])
def bio_save_score():
    if 'user_id' in session:
        user_id = session['user_id']
        data = request.json
        new_score = data.get('score')
        print(f"Adding Biology score for user {user_id}: {new_score}")  # Debug print

        try:
            # Check if the user already has a record in SubjScore
            cursor.execute("SELECT Biology FROM SubjScore WHERE ID=%s", (user_id,))
            result = cursor.fetchone()

            if result:
                # Retrieve the current Biology score
                current_score = result['Biology'] if result['Biology'] is not None else 0
                updated_score = current_score + new_score

                # Update the existing Biology score by adding the new score
                cursor.execute(
                    "UPDATE SubjScore SET Biology=%s WHERE ID=%s",
                    (updated_score, user_id)
                )
            else:
                # Insert a new record with the initial Biology score
                cursor.execute(
                    "INSERT INTO SubjScore (ID, Biology) VALUES (%s, %s)",
                    (user_id, new_score)
                )
            # Update the Total field to sum all subjects for the user
            cursor.execute(
                "UPDATE SubjScore SET Total = COALESCE(Logical, 0) + COALESCE(English, 0) + COALESCE(Physics, 0) + COALESCE(Biology, 0) + COALESCE(Chemistry, 0) WHERE ID=%s",
                (user_id,)
            )
            db.commit()
            return jsonify({"message": "Biology score updated successfully"})
        except mysql.connector.Error as err:
            print(f"Database error: {err}")  # Debug print
            return jsonify({"error": str(err)}), 500
    else:
        print("User not logged in")  # Debug print
        return jsonify({"error": "User not logged in"}), 401


#*********************************CHEMISTRY************************************************************
@app.route('/ChemistryQuiz')
def CHEM():
    return render_template('MCQS/ChemistryQuiz.html')

@app.route('/CHEM_questions', methods=['GET'])
def CHEM_get_questions():
    random_questions = get_random_questions_chem(CSV_FILE_PATH_chem, 20)
    return jsonify(random_questions)

@app.route('/CHEM_submit', methods=['POST'])
def CHEM_submit_answer():
    data = request.json
    current_question_index = data['currentQuestionIndex']
    selected_answer = data['selectedAnswer']
    
    questions = get_random_questions_chem(CSV_FILE_PATH_chem, 20)  # Get the same set of random questions
    is_correct = any(answer['text'] == selected_answer and answer['correct'] for answer in questions[current_question_index]['answers'])
    
    response = {"correct": is_correct}
    if current_question_index + 1 < len(questions):
        next_question = questions[current_question_index + 1]
        response["nextQuestion"] = next_question
    else:
        response["end"] = True
    return jsonify(response)

@app.route('/save_chemistry_score', methods=['POST'])
def chemistry_save_score():
    if 'user_id' in session:
        user_id = session['user_id']
        data = request.json
        new_score = data.get('score')
        print(f"Adding Chemistry score for user {user_id}: {new_score}")  # Debug print

        try:
            # Check if the user already has a record in SubjScore
            cursor.execute("SELECT Chemistry FROM SubjScore WHERE ID=%s", (user_id,))
            result = cursor.fetchone()

            if result:
                # Retrieve the current Chemistry score
                current_score = result['Chemistry'] if result['Chemistry'] is not None else 0
                updated_score = current_score + new_score

                # Update the existing Chemistry score by adding the new score
                cursor.execute(
                    "UPDATE SubjScore SET Chemistry=%s WHERE ID=%s",
                    (updated_score, user_id)
                )
            else:
                # Insert a new record with the initial Chemistry score
                cursor.execute(
                    "INSERT INTO SubjScore (ID, Chemistry) VALUES (%s, %s)",
                    (user_id, new_score)
                )

            # Update the Total field to sum all subjects for the user
            cursor.execute(
                "UPDATE SubjScore SET Total = COALESCE(Logical, 0) + COALESCE(English, 0) + COALESCE(Physics, 0) + COALESCE(Biology, 0) + COALESCE(Chemistry, 0) WHERE ID=%s",
                (user_id,)
            )

            db.commit()
            return jsonify({"message": "Chemistry score updated successfully"})
        except mysql.connector.Error as err:
            print(f"Database error: {err}")  # Debug print
            return jsonify({"error": str(err)}), 500
    else:
        print("User not logged in")  # Debug print
        return jsonify({"error": "User not logged in"}), 401


#*********************************PHYSICS**************************************************************
@app.route('/PhysicsQuiz')
def PHY():
    return render_template('MCQS/PhysicsQuiz.html')

@app.route('/PHY_questions', methods=['GET'])
def PHY_get_questions():
    random_questions = get_random_questions_phy(CSV_FILE_PATH_phy, 20)
    return jsonify(random_questions)

@app.route('/PHY_submit', methods=['POST'])
def PHY_submit_answer():
    data = request.json
    current_question_index = data['currentQuestionIndex']
    selected_answer = data['selectedAnswer']
    
    questions = get_random_questions_phy(CSV_FILE_PATH_phy, 20)  # Get the same set of random questions
    is_correct = any(answer['text'] == selected_answer and answer['correct'] for answer in questions[current_question_index]['answers'])
    
    response = {"correct": is_correct}
    if current_question_index + 1 < len(questions):
        next_question = questions[current_question_index + 1]
        response["nextQuestion"] = next_question
    else:
        response["end"] = True
    return jsonify(response)

@app.route('/save_physics_score', methods=['POST'])
def save_physics_score():
    if 'user_id' in session:
        user_id = session['user_id']
        data = request.json
        new_score = data.get('score')
        print(f"Adding Physics score for user {user_id}: {new_score}")  # Debug print

        try:
            # Check if the user already has a record in SubjScore
            cursor.execute("SELECT Physics FROM SubjScore WHERE ID=%s", (user_id,))
            result = cursor.fetchone()

            if result:
                # Retrieve the current Physics score
                current_score = result['Physics'] if result['Physics'] is not None else 0
                updated_score = current_score + new_score

                # Update the existing Physics score by adding the new score
                cursor.execute(
                    "UPDATE SubjScore SET Physics=%s WHERE ID=%s",
                    (updated_score, user_id)
                )
            else:
                # Insert a new record with the initial Physics score
                cursor.execute(
                    "INSERT INTO SubjScore (ID, Physics) VALUES (%s, %s)",
                    (user_id, new_score)
                )

            # Update the Total field to sum all subjects for the user
            cursor.execute(
                "UPDATE SubjScore SET Total = COALESCE(Logical, 0) + COALESCE(English, 0) + COALESCE(Physics, 0) + COALESCE(Biology, 0) + COALESCE(Chemistry, 0) WHERE ID=%s",
                (user_id,)
            )

            db.commit()
            return jsonify({"message": "Physics score updated successfully"})
        except mysql.connector.Error as err:
            print(f"Database error: {err}")  # Debug print
            return jsonify({"error": str(err)}), 500
    else:
        print("User not logged in")  # Debug print
        return jsonify({"error": "User not logged in"}), 401


#******************************************************************************************************
#*********************************LOGICAL**************************************************************
@app.route('/LogicalQuiz')
def LOGICAL():
    return render_template('MCQS/LogicalQuiz.html')

# API endpoint to get a random set of questions
@app.route('/LOGICAL_questions', methods=['GET'])
def LOGICAL_get_questions():
    random_questions = get_random_questions_chem(CSV_FILE_PATH_logical, 20)
    return jsonify(random_questions)

# API endpoint to submit an answer and get the next question or score
@app.route('/submit', methods=['POST'])
def LOGICAL_submit_answer():
    data = request.json
    current_question_index = data['currentQuestionIndex']
    selected_answer = data['selectedAnswer']
    
    questions = get_random_questions_chem(CSV_FILE_PATH_logical, 20)  # Get the same set of random questions
    is_correct = any(answer['text'] == selected_answer and answer['correct'] for answer in questions[current_question_index]['answers'])
    
    if is_correct:
        response = {"correct": True}
    else:
        response = {"correct": False}
    if current_question_index + 1 < len(questions):
        next_question = questions[current_question_index + 1]
        response["nextQuestion"] = next_question
    else:
        response["end"] = True
    return jsonify(response)

#---------------
@app.route('/save_logical_score', methods=['POST'])
def save_logical_score():
    if 'user_id' in session:
        user_id = session['user_id']
        data = request.json
        new_score = data.get('score')
        print(f"Adding Logical score for user {user_id}: {new_score}")  # Debug print

        try:
            # Check if the user already has a record in SubjScore
            cursor.execute("SELECT Logical FROM SubjScore WHERE ID=%s", (user_id,))
            result = cursor.fetchone()

            if result:
                current_score = result['Logical'] if result['Logical'] is not None else 0
                updated_score = current_score + new_score
                
                # Update the existing Logical score by adding the new score
                cursor.execute(
                    "UPDATE SubjScore SET Logical=%s WHERE ID=%s",
                    (updated_score, user_id)
                )
            else:
                # Insert a new record with the initial Logical score
                cursor.execute(
                    "INSERT INTO SubjScore (ID, Logical) VALUES (%s, %s)",
                    (user_id, new_score)
                )
            # Update the Total field to sum all subjects for the user
            cursor.execute(
                "UPDATE SubjScore SET Total = COALESCE(Logical, 0) + COALESCE(English, 0) + COALESCE(Physics, 0) + COALESCE(Biology, 0) + COALESCE(Chemistry, 0) WHERE ID=%s",
                (user_id,)
            )
            db.commit()
            return jsonify({"message": "Logical score updated successfully"})
        except mysql.connector.Error as err:
            print(f"Database error: {err}")  # Debug print
            return jsonify({"error": str(err)}), 500
    else:
        print("User not logged in")  # Debug print
        return jsonify({"error": "User not logged in"}), 401


#******************************************************************************************************
#*********************************ENGLISH**************************************************************
# Serve the HTML page
@app.route('/EnglishQuiz')
def ENG():
    return render_template('MCQS/EnglishQuiz.html')

# API endpoint to get a random set of questions
@app.route('/ENG_questions', methods=['GET'])
def ENG_get_questions():
    random_questions = get_random_questions_chem(CSV_FILE_PATH_eng, 20)
    return jsonify(random_questions)

# API endpoint to submit an answer and get the next question or score
@app.route('/submit', methods=['POST'])
def ENG_submit_answer():
    data = request.json
    current_question_index = data['currentQuestionIndex']
    selected_answer = data['selectedAnswer']
    
    questions = get_random_questions_chem(CSV_FILE_PATH_eng, 20)  # Get the same set of random questions
    is_correct = any(answer['text'] == selected_answer and answer['correct'] for answer in questions[current_question_index]['answers'])
    
    if is_correct:
        response = {"correct": True}
    else:
        response = {"correct": False}
    if current_question_index + 1 < len(questions):
        next_question = questions[current_question_index + 1]
        response["nextQuestion"] = next_question
    else:
        response["end"] = True
    return jsonify(response)
#-------------
@app.route('/save_english_score', methods=['POST'])
def save_english_score():
    if 'user_id' in session:
        user_id = session['user_id']
        data = request.json
        new_score = data.get('score')
        print(f"Adding English score for user {user_id}: {new_score}")  # Debug print

        try:
            # Check if the user already has a record in SubjScore
            cursor.execute("SELECT English FROM SubjScore WHERE ID=%s", (user_id,))
            result = cursor.fetchone()

            if result:
                current_score = result['English'] if result['English'] is not None else 0
                updated_score = current_score + new_score
                
                # Update the existing English score by adding the new score
                cursor.execute(
                    "UPDATE SubjScore SET English=%s WHERE ID=%s",
                    (updated_score, user_id)
                )
            else:
                # Insert a new record with the initial English score
                cursor.execute(
                    "INSERT INTO SubjScore (ID, English) VALUES (%s, %s)",
                    (user_id, new_score)
                )

            # Update the Total field to sum all subjects for the user
            cursor.execute(
                "UPDATE SubjScore SET Total = COALESCE(Logical, 0) + COALESCE(English, 0) + COALESCE(Physics, 0) + COALESCE(Biology, 0) + COALESCE(Chemistry, 0) WHERE ID=%s",
                (user_id,)
            )
            db.commit()
            return jsonify({"message": "English score updated successfully"})
        except mysql.connector.Error as err:
            print(f"Database error: {err}")  # Debug print
            return jsonify({"error": str(err)}), 500
    else:
        print("User not logged in")  # Debug print
        return jsonify({"error": "User not logged in"}), 401


#******************************************************************************************************
#*********************************MATHS**************************************************************
# Serve the HTML page
@app.route('/MathsQuiz')
def MATH():
    return render_template('MCQS/MathsQuiz.html')
#*********************************SCOREBOARD***********************************************************
@app.route('/scores')
def show_scores():
    # Get the user ID from session or request parameters
    user_id = session.get('user_id')  # Example: retrieving from session
    cursor = db.cursor()
    # Fetch subject scores
    cursor.execute("SELECT Biology, Chemistry, Physics, English, Logical, Total FROM SubjScore WHERE ID = %s", (user_id,))
    scores = cursor.fetchone()  # Assuming only one record per user
    # Fetch mock test results (fetch the latest entry)
    cursor.execute("SELECT Marks, Timestamp FROM MockTests WHERE ID = %s ORDER BY Timestamp DESC LIMIT 1", (user_id,))
    mock_test = cursor.fetchone()
    cursor.close()
    if not scores:
        scores = [0, 0, 0, 0, 0, 0]  # Default values if no scores are found
    if not mock_test:
        mock_test = (0, None)  # Default values if no mock test results are found

    return render_template('scores.html', scores=scores, mock_test=mock_test)

#********************************************************************************************
@app.route('/profile')
def profile():
    if 'username' in session:
        user_id = session['user_id']
        cursor.execute("SELECT * FROM user WHERE ID=%s", (user_id,))
        user = cursor.fetchone()
        return render_template('profile.html', user=user)
    return redirect(url_for('login'))
#----------------------------------------------
@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'username' in session:
        user_id = session['user_id']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Update the database
        try:
            if password:
                hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
                cursor.execute("UPDATE user SET username=%s, email=%s, password=%s WHERE ID=%s",
                               (username, email, hashed_password, user_id))
            else:
                cursor.execute("UPDATE user SET username=%s, email=%s WHERE ID=%s",
                               (username, email, user_id))
            db.commit()
            return redirect(url_for('profile'))
        except mysql.connector.Error as err:
            return f"Error: {err}"
    return redirect(url_for('login'))

#***********************************************************************************
#TOP SCORERS
@app.route('/top-users')
def top_users():
    try:
        # Fetch top 10 users based on Total score
        cursor.execute("SELECT user.username, SubjScore.Total FROM user JOIN SubjScore ON user.ID = SubjScore.ID ORDER BY SubjScore.Total DESC LIMIT 10")
        top_users = cursor.fetchall()
        # Fetch top 10 users based on highest marks in mock tests
        cursor.execute("SELECT user.username, MockTests.Marks FROM user JOIN MockTests ON user.ID = MockTests.ID ORDER BY MockTests.Marks DESC LIMIT 10")
        top_mock_test_users = cursor.fetchall()

        return render_template('top_users.html', top_users=top_users, top_mock_test_users=top_mock_test_users)
    except mysql.connector.Error as err:
        return f"Error: {err}"

#*************************************************************************************
#BIO ONE SHOT ROUTES
@app.route('/Bio_Oneshot')
def BIOONESHOT():
    return render_template('ONESHOT/bio.html')

@app.route('/BIO_oneshot_questions', methods=['GET'])
def BIO_oneshot_get_questions():
    random_questions = get_random_questions_bio(CSV_FILE_PATH_bio, 50)
    return jsonify(random_questions)

@app.route('/BIO_oneshot_submit', methods=['POST'])
def BIO_oneshot_submit_answer():
    data = request.json
    current_question_index = data['currentQuestionIndex']
    selected_answer = data['selectedAnswer']

    questions = get_random_questions_bio(CSV_FILE_PATH_bio, 50)  # Get the same set of random questions
    is_correct = any(answer['text'] == selected_answer and answer['correct'] for answer in questions[current_question_index]['answers'])
    
    response = {"correct": is_correct}
    if current_question_index + 1 < len(questions):
        next_question = questions[current_question_index + 1]
        response["nextQuestion"] = next_question
    else:
        response["end"] = True
    return jsonify(response)

@app.route('/bio_oneshot_save_score', methods=['POST'])
def bio_oneshot_save_score():
    if 'user_id' in session:
        user_id = session['user_id']
        data = request.json
        new_score = data.get('score')
        print(f"Adding Biology score for user {user_id}: {new_score}")  # Debug print

        try:
            # Check if the user already has a record in SubjScore
            cursor.execute("SELECT Biology FROM SubjScore WHERE ID=%s", (user_id,))
            result = cursor.fetchone()

            if result:
                # Retrieve the current Biology score
                current_score = result['Biology'] if result['Biology'] is not None else 0
                updated_score = current_score + new_score

                # Update the existing Biology score by adding the new score
                cursor.execute(
                    "UPDATE SubjScore SET Biology=%s WHERE ID=%s",
                    (updated_score, user_id)
                )
            else:
                # Insert a new record with the initial Biology score
                cursor.execute(
                    "INSERT INTO SubjScore (ID, Biology) VALUES (%s, %s)",
                    (user_id, new_score)
                )
            # Update the Total field to sum all subjects for the user
            cursor.execute(
                "UPDATE SubjScore SET Total = COALESCE(Logical, 0) + COALESCE(English, 0) + COALESCE(Physics, 0) + COALESCE(Biology, 0) + COALESCE(Chemistry, 0) WHERE ID=%s",
                (user_id,)
            )
            db.commit()
            return jsonify({"message": "Biology score updated successfully"})
        except mysql.connector.Error as err:
            print(f"Database error: {err}")  # Debug print
            return jsonify({"error": str(err)}), 500
    else:
        print("User not logged in")  # Debug print
        return jsonify({"error": "User not logged in"}), 401

#*************************************************************************************
#MOCK TEST
@app.route('/MOCKEXAM')
def MOCKEXAM():
    if 'username' in session:
        return render_template('MOCKEXAM/MDCAT.html', username=session['username'])
    else:
        return redirect(url_for('index'))

@app.route('/MDCAT', methods=['GET', 'POST'])
def MDCATEXAM():
    if request.method == 'POST':
        if 'user_id' not in session:
            flash('Session expired. Please log in again.')
            return redirect(url_for('index'))

        user_id = session['user_id']
        all_mcqs = get_all_random_mcqs()

        for mcq in all_mcqs:
            user_answer = request.form.get(mcq['Question'])
            correct_answer = mcq['Correct Answer']
            mcq['is_correct'] = user_answer == correct_answer
            mcq['user_answer'] = user_answer if not mcq['is_correct'] else None

        total_mcqs, total_correct, subject_wise_correct = calculate_results(all_mcqs)
        bar_chart_div = generate_bar_chart(subject_wise_correct)
        pie_chart_div = generate_pie_chart(total_mcqs, total_correct)
        subject_pie_chart_div = generate_subject_pie_chart(subject_wise_correct)

        insert_quiz_result(user_id, total_correct)

        # Storing the result data in the session
        session['result_data'] = {
            'total_mcqs': total_mcqs,
            'total_correct': total_correct,
            'subject_wise_correct': subject_wise_correct,
            'bar_chart_div': bar_chart_div,
            'pie_chart_div': pie_chart_div,
            'subject_pie_chart_div': subject_pie_chart_div
        }

        return render_template('MOCKEXAM/result.html', all_mcqs=all_mcqs, total_correct=total_correct, 
                               subject_wise_correct=subject_wise_correct, bar_chart_div=bar_chart_div, 
                               pie_chart_div=pie_chart_div, subject_pie_chart_div=subject_pie_chart_div)

    all_mcqs = get_all_random_mcqs()
    return render_template('MOCKEXAM/MDCATEXAM.html', all_mcqs=all_mcqs, username=session['username'])

@app.route('/result')
def result():
    if 'user_id' not in session:
        flash('Session expired. Please log in again.')
        return redirect(url_for('index'))

    user_id = session['user_id']
    result_data = session.get('result_data')
    # print(session[])

    if not result_data:
        flash('Session expired. Please start the quiz again.')
        return redirect(url_for('MOCKEXAM'))

    return render_template('MOCKEXAM/result.html', **result_data)

def insert_quiz_result(user_id, total_correct):
    date = datetime.now().date()  # Get the current date without time
    try:
        cursor.execute(
            """
            INSERT INTO MockTests (ID, Marks, Timestamp)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
            Marks = %s, Timestamp = %s
            """,
            (user_id, total_correct, date, total_correct, date)
        )
        db.commit()
    except mysql.connector.Error as err:
        print(f"Database error: {err}")

def get_user_result(user_id):
    try:
        cursor.execute("SELECT Marks, Timestamp FROM MockTests WHERE ID = %s", (user_id,))
        result = cursor.fetchone()
        if result:
            total_correct, timestamp = result
            return {
                'total_correct': total_correct,
                'timestamp': timestamp.strftime("%Y-%m-%d")  # Convert timestamp to string in desired format
            }
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    return None

# Function to read all MCQs from CSV file
def read_mcqs(filename):
    mcqs = []
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            mcq = {
                'Question': row['Questions'],
                'Option A': row['A'],
                'Option B': row['B'],
                'Option C': row['C'],
                'Option D': row['D'],
                'Correct Answer': row['Correct Option'],
                'is_correct': None
            }
            mcqs.append(mcq)
    return mcqs

# Read all MCQs from each CSV file
biology_mcqs = read_mcqs('CSV/biology.csv')
chemistry_mcqs = read_mcqs('CSV/chemistry.csv')
physics_mcqs = read_mcqs('CSV/physics.csv')
english_mcqs = read_mcqs('CSV/english.csv')
logical_reasoning_mcqs = read_mcqs('CSV/logical.csv')

# Function to select a specified number of random MCQs
def select_random_mcqs(mcqs, num):
    return random.sample(mcqs, num)

# Function to get all 200 random MCQs
def get_all_random_mcqs():
    selected_biology = select_random_mcqs(biology_mcqs, 68)
    selected_chemistry = select_random_mcqs(chemistry_mcqs, 54)
    selected_physics = select_random_mcqs(physics_mcqs, 54)
    selected_english = select_random_mcqs(english_mcqs, 18)
    selected_logical = select_random_mcqs(logical_reasoning_mcqs, 6)

    all_selected_mcqs = selected_biology + selected_chemistry + selected_physics + selected_english + selected_logical
    random.shuffle(all_selected_mcqs)
    return all_selected_mcqs

# Function to calculate results
def calculate_results(mcqs):
    total_mcqs = len(mcqs)
    total_correct = 0
    subject_wise_correct = {'Biology': 0, 'Chemistry': 0, 'Physics': 0, 'English': 0, 'Logical Reasoning': 0}

    for mcq in mcqs:
        if mcq['is_correct']:
            total_correct += 1
            if mcq in biology_mcqs:
                subject_wise_correct['Biology'] += 1
            elif mcq in chemistry_mcqs:
                subject_wise_correct['Chemistry'] += 1
            elif mcq in physics_mcqs:
                subject_wise_correct['Physics'] += 1
            elif mcq in english_mcqs:
                subject_wise_correct['English'] += 1
            elif mcq in logical_reasoning_mcqs:
                subject_wise_correct['Logical Reasoning'] += 1

    return total_mcqs, total_correct, subject_wise_correct

# Generate bar chart using Plotly
def generate_bar_chart(subject_wise_correct):
    subjects = list(subject_wise_correct.keys())
    correct_counts = list(subject_wise_correct.values())

    bar_data = [go.Bar(x=subjects, y=correct_counts, marker=dict(color=['blue', 'green', 'orange', 'red', 'purple']))]
    layout = go.Layout(title='Subject-wise Correct MCQs', xaxis=dict(title='Subjects'), yaxis=dict(title='Number of Correct MCQs'))
    fig = go.Figure(data=bar_data, layout=layout)
    bar_chart_div = pyo.plot(fig, output_type='div', include_plotlyjs=False)
    return bar_chart_div

# Generate pie chart using Plotly
def generate_pie_chart(total_mcqs, total_correct):
    incorrect_count = total_mcqs - total_correct
    labels = ['Correct MCQs', 'Incorrect MCQs']
    sizes = [total_correct, incorrect_count]
    colors = ['green', 'red']

    pie_data = [go.Pie(labels=labels, values=sizes, marker=dict(colors=colors))]
    layout = go.Layout(title='Correct vs Incorrect MCQs')
    fig = go.Figure(data=pie_data, layout=layout)
    pie_chart_div = pyo.plot(fig, output_type='div', include_plotlyjs=False)
    return pie_chart_div

# Generate pie chart for subject-wise distribution using Plotly
def generate_subject_pie_chart(subject_wise_correct):
    labels = list(subject_wise_correct.keys())
    values = list(subject_wise_correct.values())
    colors = ['blue', 'green', 'orange', 'red', 'purple']

    pie_data = [go.Pie(labels=labels, values=values, marker=dict(colors=colors))]
    layout = go.Layout(title='Subject-wise Correct MCQs Distribution')
    fig = go.Figure(data=pie_data, layout=layout)
    subject_pie_chart_div = pyo.plot(fig, output_type='div', include_plotlyjs=False)
    return subject_pie_chart_div

@app.route('/random_questions', methods=['GET'])
def get_random_questions():
    try:
        random_questions = get_all_random_mcqs()
        return jsonify(random_questions)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
