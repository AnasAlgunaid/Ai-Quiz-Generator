import streamlit as st
from PyPDF2 import PdfReader
import openai
import os
from dotenv import load_dotenv
import json

# Load environment variables.
load_dotenv()

# Set OpenAI API key.
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set template for the response.
TEMPLATE = """"questions":  [
    {
      "id": 1,
      "question": "What is the purpose of assembler directives?",
      "options": [
        "A. To define segments and allocate space for variables",
        "B. To represent specific machine instructions",
        "C. To simplify the programmer's task",
        "D. To provide information to the assembler"
      ],
      "correct_answer": "D. To provide information to the assembler"
    },
    {
      "id": 2,
      "question": "What are opcodes?",
      "options": [
        "A. Instructions for integer addition and subtraction",
        "B. Instructions for memory access",
        "C. Instructions for directing the assembler",
        "D. Mnemonic codes representing specific machine instructions"
      ],
      "correct_answer": "D. Mnemonic codes representing specific machine instructions"
    }]}"""


def extract_text_from_pdf(file):
    # Load PDF file and split into pages.
    reader = PdfReader(file)

    text = ""

    # Loop through each page and extract text.
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content

    return text


def get_questions(text, num_questions=5):
    prompt = f"""
            Act as a teacher and create a {num_questions} multiple-choice questions (MCQs) based on the text delimted by four backquotes,
            the response must be formatted in JSON. Each question contains id, question, options as list, correct_answer.
            this is an example of the response: {TEMPLATE}

            the text is : ````{text}````
            """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
        ],
    )

    return json.loads(response["choices"][0]["message"]["content"])


# Display questions function
def display_questions(questions):
    # Display questions
    for question in questions:
        # convert question id to string
        question_id = str(question["id"])

        st.write(
            f"## Q{question_id} \{question['question']}",
        )

        # Display options as bullet points
        options_text = ""
        options = question["options"]
        for option in options:
            options_text += f"- {option}\n"
        st.write(options_text)

        # Display answer in expander
        with st.expander("Show answer", expanded=False):
            st.write(question["correct_answer"])

        st.divider()

    st.subheader("End of questions")


def main():
    # Set page title and favicon.
    st.set_page_config(page_title="Quizlet app", page_icon="📚")

    # Set page layout.
    st.title("Quizlet app")
    st.write(" This app is a simple quizlet app.")
    st.divider()

    # Create a form to upload a PDF file.
    with st.form(key="upload_file"):
        uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

        number_of_questions = st.number_input(
            "Number of questions", min_value=1, max_value=10, value=5
        )

        submit_button = st.form_submit_button(
            label="Generate Questions", type="primary"
        )

    if submit_button:
        if uploaded_file:
            text = extract_text_from_pdf(uploaded_file)
            with st.spinner("Generating questions..."):
                questions = get_questions(text, number_of_questions)["questions"]

            display_questions(questions)

        else:
            st.error("Please upload a PDF file.")


if __name__ == "__main__":
    main()
