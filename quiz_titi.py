import streamlit as st
import json
from datetime import datetime
import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Get the DATABASE_URL from the environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Database functions
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

def get_all_results():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM quiz_results ORDER BY timestamp DESC;")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def save_quiz_result_db(user_id, score):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO quiz_results (user_id, score, timestamp) VALUES (%s, %s, %s);"
    cursor.execute(query, (user_id, score, datetime.now()))
    conn.commit()
    cursor.close()
    conn.close()

# File-based storage for local testing
def save_results_file(name, score):
    result = {
        "name": name,
        "score": score,
        "timestamp": datetime.now().isoformat()
    }
    try:
        with open("quiz_results.json", "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append(result)

    with open("quiz_results.json", "w") as file:
        json.dump(data, file, indent=4)

# Initialize session state
if "score" not in st.session_state:
    st.session_state.score = 0
if "qualified_for_bonus" not in st.session_state:
    st.session_state.qualified_for_bonus = False
if "bonus_score" not in st.session_state:
    st.session_state.bonus_score = 0

# Main quiz function
def main():
    st.title("🎤 Valen's Taylor Swift Quiz 🎤")
    st.write("Let's test your knowledge about Taylor Swift!")

    # Name input
    name = st.text_input("Enter your name")

    # First set of questions
    questions_set1 = [
        {"question": "What is Taylor Swift's middle name?", "options": ["Alison", "Marie", "Elizabeth", "Anne"], "answer": "Alison"},
        {"question": "In which year was Taylor Swift born?", "options": ["1987", "1989", "1990", "1992"], "answer": "1989"},
        {"question": "What was the title of Taylor Swift's debut single?", "options": ["Love Story", "Tim McGraw", "Our Song", "Teardrops on My Guitar"], "answer": "Tim McGraw"},
        {"question": "Which Taylor Swift album includes the song 'Blank Space'?", "options": ["Red", "1989", "Fearless", "Speak Now"], "answer": "1989"},
        {"question": "Which of these movies did Taylor Swift appear in?", "options": ["Cats", "La La Land", "The Hunger Games", "Harry Potter"], "answer": "Cats"},
        {"question": "Which film did Taylor make a song for?", "options": ["Inside Out", "Minions 2", "Hannah Montana: The Movie", "Shrek"], "answer": "Hannah Montana: The Movie"}
    ]

    # Second set of questions
    questions_set2 = [
        {"question": "What instrument did Taylor Swift first learn to play?", "options": ["Piano", "Guitar", "Violin", "Drums"], "answer": "Guitar"},
        {"question": "Which song earned Taylor her first Grammy award?", "options": ["You Belong With Me", "Love Story", "White Horse", "Fearless"], "answer": "White Horse"},
        {"question": "What is the name of Taylor's 2017 album?", "options": ["Red", "1989", "Reputation", "Lover"], "answer": "Reputation"},
        {"question": "Which song did Taylor Swift re-record in 2021?", "options": ["Love Story", "Shake It Off", "Delicate", "Bad Blood"], "answer": "Love Story"},
        {"question": "Taylor Swift won Album of the Year Grammy for which album?", "options": ["Speak Now", "Red", "Folklore", "Lover"], "answer": "Folklore"},
        {"question": "In which city was Taylor Swift born?", "options": ["Nashville", "New York", "Los Angeles", "Reading"], "answer": "Reading"},
        {"question": "Which Taylor Swift music video features a wedding scene?", "options": ["Speak Now", "Mine", "Love Story", "You Belong With Me"], "answer": "Mine"},
        {"question": "Which song is NOT on the 'Fearless' album?", "options": ["You Belong With Me", "Fifteen", "Red", "The Best Day"], "answer": "Red"},
        {"question": "What color dress does Taylor Swift wear in the 'Begin Again' music video?", "options": ["Blue", "White", "Red", "Green"], "answer": "Red"},
        {"question": "Which artist collaborated with Taylor on 'Everything Has Changed'?", "options": ["Ed Sheeran", "Justin Bieber", "Shawn Mendes", "Adele"], "answer": "Ed Sheeran"}
    ]

    # Quiz logic for the first set of questions
    for i, q in enumerate(questions_set1):
        st.subheader(f"Question {i + 1}")
        user_answer = st.radio(q["question"], q["options"], key=f"question1_{i}")
        
        # Check if the answer is correct
        if user_answer == q["answer"]:
            st.session_state.score += 1

    # Display score and conditionally show the second set of questions
    if st.button("Submit First Set"):
        if name.strip() == "":
            st.error("Please enter your name before submitting.")
        else:
            st.write(f"🎉 **{name}, your score for the first set is: {st.session_state.score}/{len(questions_set1)}!** 🎉")
            
            # Check if the user qualifies for the bonus round
            if st.session_state.score >= 5:
                st.session_state.qualified_for_bonus = True
            else:
                st.write("Good try! Score 5 or more to unlock the bonus round.")

    # Display bonus questions if qualified
    if st.session_state.qualified_for_bonus:
        st.write("Great job! You scored 5 or higher, so here's a bonus round! 🎉")
        
        # Quiz logic for the second set of questions
        for i, q in enumerate(questions_set2):
            st.subheader(f"Bonus Question {i + 1}")
            user_answer = st.radio(q["question"], q["options"], key=f"question2_{i}")
            
            # Check if the answer is correct
            if user_answer == q["answer"]:
                st.session_state.bonus_score += 1

        # Display score for the second set
        if st.button("Submit Bonus Round"):
            total_score = st.session_state.score + st.session_state.bonus_score
            st.write(f"🎉 **{name}, your total score is: {total_score}/{len(questions_set1) + len(questions_set2)}!** 🎉")
            st.write("Thank you for playing! 🎸")

            # Save result to database and JSON file
            save_quiz_result_db(name, total_score)
            save_results_file(name, total_score)
            st.success("Your result has been saved!")

    # Display all results
    if st.button("Show All Results"):
        results = get_all_results()
        
        if results:
            st.write("📜 **All Quiz Results** 📜")
            for res in results:
                st.write(f"**Name**: {res['user_id']}, **Score**: {res['score']}, **Date**: {res['timestamp']}")
        else:
            st.write("No results to display yet.")

if __name__ == "__main__":
    main()
