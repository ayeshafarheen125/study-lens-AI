# StudyLens AI — Member 3 (Groq + Streamlit)

Member 3 contains two specialized agents:

- **Tutor Agent:** summary, key points, easy explanations, difficult terms.
- **Question Agent:** MCQs, short questions, long questions, and True/False.

## Interactive workflow

After uploading a PDF, the user chooses:

1. **Tutoring** — runs the Tutor Agent and displays the learning material.
2. **Take a Quiz** — runs the Question Agent and gives an interactive quiz.

In Quiz mode:

- The user selects answers instead of seeing the answers immediately.
- MCQs and True/False questions are automatically checked after submission.
- The app shows the user's answer, correct answer, and why.
- A final score and percentage are displayed.
- Short and long questions are available as written practice and are not included in the automatic score.

There is no Member 4 handoff/download section in this standalone Member 3 app. The generated agent files can be shared separately with the rest of the team.

## Files

```text
app.py
document_agent.py
llm_client.py
tutor_agent.py
question_agent.py
member3_service.py
member3_test.py
requirements.txt
.env.example
.gitignore
README.md
```

## Local setup

```bash
pip install -r requirements.txt
```

Create `.env` from `.env.example`:

```env
GROQ_API_KEY=your_real_groq_key
GROQ_MODEL=openai/gpt-oss-120b
```

Then run:

```bash
streamlit run app.py
```

## Streamlit Community Cloud

In **App settings → Secrets**, add:

```toml
GROQ_API_KEY = "your_real_groq_key"
GROQ_MODEL = "openai/gpt-oss-120b"
```

Never commit the real `.env` file or API key to GitHub.
