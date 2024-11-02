import streamlit as st
import json
from datetime import datetime

def save_results(name, score):
    # Data to save
    result = {
        "name": name,
        "score": score,
        "timestamp": datetime.now().isoformat()
    }
    
    # Load existing results from JSON file if it exists
    try:
        with open("quiz_results.json", "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    
    # Add the new result
    data.append(result)
    
    # Save the updated results back to the JSON file
    with open("quiz_results.json", "w") as file:
        json.dump(data, file, indent=4)

def main():
    st.title("Taylor Swift Quiz")

    # Name input
    name = st.text_input("Enter your name")

    # Questions and answer choices
    questions = [
        {
            "question": "What is Taylor Swift's middle name?",
            "options": ["Alison", "Marie", "Elizabeth", "Anne"],
            "answer": "Alison"
        },
        {
            "question": "In which year was Taylor Swift born?",
            "options": ["1987", "1989", "1990", "1992"],
            "answer": "1989"
        },
        {
            "question": "What was the title of Taylor Swift's debut single?",
            "options": ["Love Story", "Tim McGraw", "Our Song", "Teardrops on My Guitar"],
            "answer": "Tim McGraw"
        },
        {
            "question": "Which Taylor Swift album includes the song 'Blank Space'?",
            "options": ["Red", "1989", "Fearless", "Speak Now"],
            "answer": "1989"
        },
        {
            "question": "Which of these movies did Taylor Swift appear in?",
            "options": ["Cats", "La La Land", "The Hunger Games", "Harry Potter"],
            "answer": "Cats"
        }
    ]

    score = 0

    # Loop through each question
    for i, q in enumerate(questions):
        st.subheader(f"Question {i + 1}")
        user_answer = st.radio(q["question"], q["options"], key=f"question_{i}")
        
        # Check answer and increment score if correct
        if st.session_state.get(f"question_{i}") == q["answer"]:
            score += 1

    # Display final score
    if st.button("Submit"):
        if name.strip() == "":
            st.error("Please enter your name before submitting.")
        else:
            st.write(f"Your Score: {score}/{len(questions)}")
            st.write("Thanks for playing!")
            
            # Save result to JSON file
            save_results(name, score)
            st.success("Your result has been saved!")

if __name__ == "__main__":
    main()
