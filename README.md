# StudyLens AI — Member 3

## Role

Member 3 is responsible for two specialized agents:

1. **Tutor/Understanding Agent**
   - Summary
   - Key points
   - Easy explanations
   - Difficult terms

2. **Question Agent**
   - MCQs
   - Short questions
   - Long questions
   - True/False

The agents use the same Groq API client but have separate responsibilities and separate prompts.

## Architecture

```text
PDF
 ↓
Member 2 — DocumentProcessingAgent
 ↓
clean processed text
 ↓
Member 3 — Tutor Agent
 ↓
learning content

same processed text
 ↓
Member 3 — Question Agent
 ↓
structured questions
 ↓
Member 4 — Quiz Agent
```

## Files

- `document_agent.py` — Member 2's document-processing component
- `llm_client.py` — shared Groq client
- `tutor_agent.py` — Member 3 Tutor Agent
- `question_agent.py` — Member 3 Question Agent
- `member3_service.py` — clean interface for the Orchestrator
- `member3_test.py` — command-line integration test
- `app.py` — standalone Streamlit demo/deployment app
- `requirements.txt` — dependencies
- `.env.example` — local environment-variable template

## Local setup

### 1. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install packages

```bash
pip install -r requirements.txt
```

### 3. Add your Groq API key

For local development, create `.env`:

```env
GROQ_API_KEY=your_real_groq_key
GROQ_MODEL=llama-3.3-70b-versatile
```

The code can also receive the key from the environment.

### 4. Run the Streamlit app

```bash
streamlit run app.py
```

## Test from the command line

```bash
python member3_test.py "your_file.pdf"
```

## Team integration

Member 1 can import:

```python
from member3_service import Member3Service

member3 = Member3Service()

result = member3.run(document_result["full_text"])
```

Then pass:

```python
result["questions"]
```

to Member 4's Quiz Agent.

## Important

Do not commit `.env` or your real Groq API key to GitHub.

For Streamlit deployment, put the key in the app's Secrets settings:

```toml
GROQ_API_KEY = "your_real_groq_key"
GROQ_MODEL = "llama-3.3-70b-versatile"
```
