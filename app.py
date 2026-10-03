import json
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
    "Upload study material to test the Member 2 → Member 3 workflow. "
    "Member 2 processes the PDF, then your two specialized agents "
    "generate learning content and questions."
)

with st.sidebar:
    st.header("⚙️ Settings")

    model = st.text_input(
        "Groq Model",
        value=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
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

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as tmp:
        tmp.write(uploaded_file.getvalue())
        pdf_path = tmp.name

    try:
        with st.spinner("Member 2: processing the PDF..."):
            document_agent = DocumentProcessingAgent(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
            document_result = document_agent.process_document(pdf_path)

        if document_result["status"] != "success":
            st.error(document_result.get("message", "Document processing failed."))
            st.stop()

        c1, c2, c3 = st.columns(3)
        c1.metric("Pages", document_result["total_pages"])
        c2.metric("Characters", f"{document_result['total_characters']:,}")
        c3.metric("Chunks", document_result["total_chunks"])

        st.success("Member 2 completed. Passing processed content to Member 3.")

        with st.expander("View processed text"):
            st.text_area(
                "Processed study material",
                document_result["full_text"],
                height=300,
            )

        with st.spinner("Member 3: Tutor Agent + Question Agent working..."):
            service = Member3Service(
                model=model,
                temperature=temperature,
            )
            result = service.run(document_result["full_text"])

        if result["status"] != "success":
            st.error(
                f"Member 3 failed at {result.get('stage', 'unknown stage')}: "
                f"{result.get(result.get('stage', ''), {}).get('message', 'Unknown error')}"
            )
            st.stop()

        tutor = result["tutor"]
        questions = result["questions"]

        st.divider()
        st.header("👨‍🏫 Tutor Agent")

        st.subheader("Summary")
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
            st.markdown(f"**{item['term']}** — {item['meaning']}")

        st.divider()
        st.header("❓ Question Agent")

        tab1, tab2, tab3, tab4 = st.tabs(
            ["MCQs", "Short Questions", "Long Questions", "True/False"]
        )

        with tab1:
            for i, q in enumerate(questions["mcqs"], 1):
                st.markdown(f"**MCQ {i}. {q['question']}**")
                for option in q["options"]:
                    st.markdown(f"- {option}")
                st.success(f"Answer: {q['correct_answer']}")
                st.caption(q["explanation"])

        with tab2:
            for i, q in enumerate(questions["short_questions"], 1):
                st.markdown(f"**{i}. {q['question']}**")
                st.write(f"Answer: {q['answer']}")

        with tab3:
            for i, q in enumerate(questions["long_questions"], 1):
                st.markdown(f"**{i}. {q['question']}**")
                st.write(f"Answer: {q['answer']}")

        with tab4:
            for i, q in enumerate(questions["true_false"], 1):
                answer = "True" if q["answer"] else "False"
                st.markdown(f"**{i}. {q['statement']}**")
                st.write(f"Answer: {answer}")
                st.caption(q["explanation"])

        st.divider()
        st.subheader("🔗 Handoff to Member 4 — Quiz Agent")

        quiz_payload = {
            "status": "success",
            "questions": questions,
        }

        st.json(quiz_payload)

        st.download_button(
            "💾 Download Question Payload",
            data=json.dumps(quiz_payload, indent=2, ensure_ascii=False),
            file_name="member3_question_payload.json",
            mime="application/json",
        )

    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
