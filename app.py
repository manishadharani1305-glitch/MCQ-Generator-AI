import streamlit as st
from huggingface_hub import InferenceClient
import re

st.set_page_config(
    page_title="MCQ Generator AI",
    page_icon="📝",
    layout="centered"
)

st.title("📝 MCQ Generator AI")
st.write("Generate Multiple Choice Questions using AI")

st.divider()

topic = st.text_input(
    "📚 Enter Topic",
    placeholder="Example: Python Programming"
)

number = st.selectbox(
    "🔢 Number of Questions",
    [5, 10, 15]
)

difficulty = st.selectbox(
    "📊 Difficulty Level",
    ["Easy", "Medium", "Hard"]
)

st.divider()

if st.button("🚀 Generate MCQs"):

    if topic == "":
        st.warning("Please enter a topic.")
        st.stop()

    try:
        token = st.secrets["HF_TOKEN"]

        client = InferenceClient(
            api_key=token
        )

        prompt = f"""
Generate exactly {number} multiple-choice questions about {topic}.

Difficulty level: {difficulty}

For every question use this exact format:

Question: <question>

A) <option A>
B) <option B>
C) <option C>
D) <option D>

Answer: <A, B, C, or D>

Explanation: <short explanation>

Rules:
- Generate exactly {number} questions.
- Each question must have exactly four options.
- Only one option must be correct.
- The correct answer must be A, B, C, or D.
- Make all questions relevant to {topic}.
"""

        with st.spinner("🤖 Generating MCQs..."):

            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an educational MCQ generator."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=4000
            )

        result = response.choices[0].message.content

        st.success("✅ MCQs generated successfully!")

        st.subheader("📋 Generated MCQs")

        questions = re.split(
            r"(?=Question:)",
            result
        )

        question_number = 0

        for question in questions:

            if "Question:" not in question:
                continue

            question_number += 1

            question_match = re.search(
                r"Question:\s*(.*?)(?=\nA\))",
                question,
                re.DOTALL
            )

            options = {}

            for letter in ["A", "B", "C", "D"]:

                match = re.search(
                    rf"{letter}\)\s*(.*)",
                    question
                )

                if match:
                    options[letter] = match.group(1).strip()

            answer_match = re.search(
                r"Answer:\s*([ABCD])",
                question,
                re.IGNORECASE
            )

            explanation_match = re.search(
                r"Explanation:\s*(.*)",
                question,
                re.DOTALL
            )

            if not question_match:
                continue

            question_text = question_match.group(1).strip()

            correct_answer = ""

            if answer_match:
                correct_answer = answer_match.group(1).upper()

            explanation = ""

            if explanation_match:
                explanation = explanation_match.group(1).strip()

            st.markdown(
                f"### Q{question_number}. {question_text}"
            )

            option_list = []

            for letter in ["A", "B", "C", "D"]:

                if letter in options:
                    option_list.append(
                        f"{letter}) {options[letter]}"
                    )

            user_answer = st.radio(
                "Choose your answer:",
                option_list,
                key=f"question_{question_number}"
            )

            if st.button(
                f"Show Answer for Q{question_number}",
                key=f"answer_{question_number}"
            ):

                selected_letter = user_answer[0]

                if selected_letter == correct_answer:

                    st.success(
                        f"✅ Correct! Answer: {correct_answer}"
                    )

                else:

                    st.error(
                        f"❌ Incorrect. Correct Answer: {correct_answer}"
                    )

                if explanation:

                    st.info(
                        f"💡 Explanation: {explanation}"
                    )

            st.divider()

    except Exception as e:

        st.error("❌ Error while generating MCQs")

        st.write(str(e))