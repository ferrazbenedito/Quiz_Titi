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

# Main quiz function
def main():
    st.title("🎤 Valen's Taylor Swift Quiz 🎤")
    st.write("Let's test your knowledge about Taylor Swift!")

    # Name input
    name = st.text_input("Enter your name")

    # Quiz questions
    questions = [
        {"question": "What is Taylor Swift's middle name?", "options": ["Alison", "Marie", "Elizabeth", "Anne"], "answer": "Alison"},
        {"question": "In which year was Taylor Swift born?", "options": ["1987", "1989", "1990", "1992"], "answer": "1989"},
        {"question": "What was the title of Taylor Swift's debut single?", "options": ["Love Story", "Tim McGraw", "Our Song", "Teardrops on My Guitar"], "answer": "Tim McGraw"},
        {"question": "Which Taylor Swift album includes the song 'Blank Space'?", "options": ["Red", "1989", "Fearless", "Speak Now"], "answer": "1989"},
        {"question": "Which of these movies did Taylor Swift appear in?", "options": ["Cats", "La La Land", "The Hunger Games", "Harry Potter"], "answer": "Cats"},
        {"question": "Which film did Taylor make a song for?", "options": ["Inside Out", "Minions 2", "Hannah Montana: The Movie", "Shrek"], "answer": "Hannah Montana: The Movie"}
    ]

    # Quiz logic
    score = 0
    for i, q in enumerate(questions):
        st.subheader(f"Question {i + 1}")
        user_answer = st.radio(q["question"], q["options"], key=f"question_{i}")
        
        # Check if the answer is correct
        if user_answer == q["answer"]:
            score += 1

    # Submit button with scoring and saving
    if st.button("Submit Quiz"):
        if name.strip() == "":
            st.error("Please enter your name before submitting.")
        else:
            st.write(f"🎉 **{name}, your score is: {score}/{len(questions)}!** 🎉")
            st.write("Thank you for playing! 🎸")

            # Save the result to both the database and JSON file for demonstration
            save_quiz_result_db(name, score)
            save_results_file(name, score)
            st.success("Your result has been saved!")

    # Display results
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
