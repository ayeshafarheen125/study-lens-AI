import os
import tempfile

import streamlit as st

from document_agent import DocumentProcessingAgent
from member3_service import Member3Service


st.set_page_config(
    page_title="StudyLens AI — Member 3",
    page_icon="📚",
    layout="wide",
)

st.title("📚 StudyLens AI")
st.caption("Member 3 — Tutor/Understanding Agent + Question Agent")

st.info(
    "Upload your study material, then choose whether you want tutoring "
    "or an interactive quiz."
)

with st.sidebar:
    st.header("⚙️ Settings")

    model = st.text_input(
        "Groq Model",
        value=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
    )

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.1,
    )

    chunk_size = st.slider(
        "Document Chunk Size",
        min_value=300,
        max_value=2500,
        value=1000,
        step=50,
    )

    chunk_overlap = st.slider(
        "Chunk Overlap",
        min_value=50,
        max_value=500,
        value=150,
        step=25,
    )

uploaded_file = st.file_uploader(
    "Upload a PDF study material",
    type=["pdf"],
)

if uploaded_file:
    if not os.getenv("GROQ_API_KEY"):
        st.error(
            "GROQ_API_KEY is missing. Add it to Streamlit Secrets "
            "before running the app."
        )
        st.stop()

    if chunk_overlap >= chunk_size:
        st.error("Chunk overlap must be smaller than chunk size.")
        st.stop()

    # Store results so Streamlit reruns do not call Groq repeatedly.
    if "member3_result" not in st.session_state:
        st.session_state.member3_result = None
    if "processed_content" not in st.session_state:
        st.session_state.processed_content = None
    if "document_result" not in st.session_state:
        st.session_state.document_result = None
    if "uploaded_file_name" not in st.session_state:
        st.session_state.uploaded_file_name = None
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False

    # Reset the previous result when a different PDF is uploaded.
    if st.session_state.uploaded_file_name != uploaded_file.name:
        st.session_state.member3_result = None
        st.session_state.processed_content = None
        st.session_state.document_result = None
        st.session_state.uploaded_file_name = uploaded_file.name
        st.session_state.quiz_submitted = False

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.getvalue())
        pdf_path = tmp.name

    try:
        # ---------------------------------------------------------------
        # MEMBER 2 — DOCUMENT PROCESSING
        # ---------------------------------------------------------------
        if st.session_state.processed_content is None:
            with st.spinner("Member 2: processing the PDF..."):
                document_agent = DocumentProcessingAgent(
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                )
                document_result = document_agent.process_document(pdf_path)

            if document_result["status"] != "success":
                st.error(
                    document_result.get(
                        "message", "Document processing failed."
                    )
                )
                st.stop()

            st.session_state.processed_content = document_result["full_text"]
            st.session_state.document_result = document_result
        else:
            document_result = st.session_state.document_result

        c1, c2, c3 = st.columns(3)
        c1.metric("Pages", document_result["total_pages"])
        c2.metric("Characters", f"{document_result['total_characters']:,}")
        c3.metric("Chunks", document_result["total_chunks"])

        st.success(
            "Member 2 completed. Processed content is ready for Member 3."
        )

        with st.expander("View processed text"):
            st.text_area(
                "Processed study material",
                st.session_state.processed_content,
                height=300,
            )

        st.divider()

        # ---------------------------------------------------------------
        # USER CHOICE
        # ---------------------------------------------------------------
        st.header("🎯 What would you like to do?")

        choice = st.radio(
            "Choose one option:",
            ["👨‍🏫 Tutoring", "📝 Take a Quiz"],
            horizontal=True,
        )

        # ---------------------------------------------------------------
        # TUTORING MODE
        # ---------------------------------------------------------------
        if choice == "👨‍🏫 Tutoring":
            st.session_state.quiz_submitted = False

            if st.button("Start Tutoring", type="primary"):
                with st.spinner("Tutor Agent is preparing your lesson..."):
                    service = Member3Service(
                        model=model,
                        temperature=temperature,
                    )
                    tutor_result = service.tutor_agent.process(
                        st.session_state.processed_content
                    )

                if tutor_result.get("status") != "success":
                    st.error(
                        "Tutor Agent failed: "
                        + tutor_result.get("message", "Unknown error")
                    )
                else:
                    st.session_state.member3_result = {
                        "mode": "tutoring",
                        "tutor": tutor_result,
                    }

            result = st.session_state.member3_result

            if result and result.get("mode") == "tutoring":
                tutor = result["tutor"]

                st.success("Tutor Agent completed the lesson.")

                st.subheader("📌 Summary")
                st.write(tutor["summary"])

                st.subheader("🔑 Key Points")
                for point in tutor["key_points"]:
                    st.markdown(f"- {point}")

                st.subheader("💡 Easy Explanations")
                for item in tutor["explanations"]:
                    with st.expander(item["concept"]):
                        st.write(item["explanation"])

                st.subheader("📖 Difficult Terms")
                for item in tutor["difficult_terms"]:
                    st.markdown(
                        f"**{item['term']}** — {item['meaning']}"
                    )

        # ---------------------------------------------------------------
        # QUIZ MODE
        # ---------------------------------------------------------------
        else:
            if st.button("Generate Quiz", type="primary"):
                with st.spinner("Question Agent is creating your quiz..."):
                    service = Member3Service(
                        model=model,
                        temperature=temperature,
                    )
                    question_result = service.question_agent.generate(
                        st.session_state.processed_content
                    )

                if question_result.get("status") != "success":
                    st.error(
                        "Question Agent failed: "
                        + question_result.get("message", "Unknown error")
                    )
                else:
                    st.session_state.member3_result = {
                        "mode": "quiz",
                        "questions": question_result,
                    }
                    st.session_state.quiz_submitted = False

            result = st.session_state.member3_result

            if result and result.get("mode") == "quiz":
                questions = result["questions"]
                mcqs = questions.get("mcqs", [])
                true_false = questions.get("true_false", [])

                if not mcqs and not true_false:
                    st.warning("The Question Agent did not generate quiz questions.")
                    st.stop()

                st.success(
                    "Quiz ready! Choose your answers first. "
                    "Your score and explanations will appear after submission."
                )

                st.subheader("📝 Interactive Quiz")

                question_number = 0

                # ------------------------- MCQs -------------------------
                for i, q in enumerate(mcqs):
                    question_number += 1
                    st.markdown(
                        f"### Question {question_number}\n{q['question']}"
                    )

                    options = q.get("options", [])
                    st.radio(
                        "Select your answer:",
                        options,
                        key=f"mcq_answer_{i}",
                        index=None,
                    )

                # ---------------------- True/False ----------------------
                for i, q in enumerate(true_false):
                    question_number += 1
                    st.markdown(
                        f"### Question {question_number}\n{q['statement']}"
                    )

                    st.radio(
                        "Select your answer:",
                        ["True", "False"],
                        key=f"tf_answer_{i}",
                        index=None,
                    )

                st.divider()

                if st.button("✅ Submit Quiz", type="primary"):
                    st.session_state.quiz_submitted = True

                if st.session_state.quiz_submitted:
                    score = 0
                    total = len(mcqs) + len(true_false)

                    st.subheader("📊 Your Result")

                    # Check MCQs
                    for i, q in enumerate(mcqs):
                        selected = st.session_state.get(
                            f"mcq_answer_{i}"
                        )
                        correct = q["correct_answer"]

                        if selected == correct:
                            score += 1
                            st.success(
                                f"Question {i + 1}: Correct ✓\n\n"
                                f"Why: {q.get('explanation', 'The selected answer matches the answer generated from the study material.')}"
                            )
                        else:
                            if selected is None:
                                selected_text = "No answer selected"
                            else:
                                selected_text = selected

                            st.error(
                                f"Question {i + 1}: Incorrect ✗\n\n"
                                f"Your answer: {selected_text}\n\n"
                                f"Correct answer: {correct}\n\n"
                                f"Why: {q.get('explanation', 'The correct answer is supported by the uploaded study material.')}"
                            )

                    # Check True/False
                    offset = len(mcqs)
                    for i, q in enumerate(true_false):
                        selected = st.session_state.get(
                            f"tf_answer_{i}"
                        )

                        correct_bool = bool(q["answer"])
                        correct_text = "True" if correct_bool else "False"

                        if selected == correct_text:
                            score += 1
                            st.success(
                                f"Question {offset + i + 1}: Correct ✓\n\n"
                                f"Why: {q.get('explanation', 'This answer is supported by the uploaded study material.')}"
                            )
                        else:
                            if selected is None:
                                selected_text = "No answer selected"
                            else:
                                selected_text = selected

                            st.error(
                                f"Question {offset + i + 1}: Incorrect ✗\n\n"
                                f"Your answer: {selected_text}\n\n"
                                f"Correct answer: {correct_text}\n\n"
                                f"Why: {q.get('explanation', 'The correct answer is supported by the uploaded study material.')}"
                            )

                    percentage = (score / total * 100) if total else 0

                    st.divider()
                    st.metric(
                        "Final Score",
                        f"{score}/{total}",
                        f"{percentage:.0f}%",
                    )

                    st.info(
                        "The quiz checks your selected answers against the "
                        "answers generated from the uploaded study material."
                    )

                # Optional written practice after the interactive quiz.
                short_questions = questions.get("short_questions", [])
                long_questions = questions.get("long_questions", [])

                if short_questions or long_questions:
                    st.divider()
                    with st.expander("📚 Written Practice Questions"):
                        st.caption(
                            "These questions are provided for practice. "
                            "They are not part of the automatic score."
                        )

                        for i, q in enumerate(short_questions, 1):
                            st.markdown(
                                f"**Short Question {i}: {q['question']}**"
                            )
                            st.write(
                                "Suggested answer: "
                                + q.get("answer", "")
                            )

                        for i, q in enumerate(long_questions, 1):
                            st.markdown(
                                f"**Long Question {i}: {q['question']}**"
                            )
                            st.write(
                                "Suggested answer: "
                                + q.get("answer", "")
                            )

    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
