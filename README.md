# ResumeIQ — AI-Powered Resume Analyzer

**Your Resume. Your Next Opportunity.**

ResumeIQ is a Streamlit SaaS-style resume analysis application. It extracts text from PDF/DOCX resumes, compares the content with a supplied job description using Groq, identifies skills gaps, proposes fact-preserving rewrites, prepares interview questions and exports a PDF report.

## Features

- PDF and DOCX resume upload (5 MB maximum)
- Resume text extraction with clear scanned-PDF/unreadable-file handling
- Groq-powered job-specific analysis and JSON response validation
- Overall, ATS readability, job match and six supporting assessment scores
- Skills present, missing skills, priorities and keyword recommendations
- Resume summary, experience and project rewrite suggestions
- 25 interview questions with answer guidance
- Downloadable PDF report
- Session-based workflow, reset control and no app-level permanent resume storage

> Scores are ResumeIQ's advisory assessment, not an actual ATS vendor score. AI rewrites must be checked for accuracy before use.

## Project structure

```text
resumeiq/
├── app.py
├── analyzer.py
├── resume_parser.py
├── ai_engine.py
├── report_generator.py
├── utils.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
└── .streamlit/
    └── secrets.toml.example
```

## Requirements

- Python 3.11+
- A Groq API key
- Internet access for Groq API calls

## Run locally (Windows PowerShell)

1. Download and extract the project ZIP.
2. Open the `resumeiq` folder in VS Code.
3. Create and activate a virtual environment:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
```

4. Install packages:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

5. Create a `.env` file by copying `.env.example`, then add your key:

```env
GROQ_API_KEY=gsk_your_real_key_here
```

6. Start the app:

```powershell
streamlit run app.py
```

Do not paste your real API key into source code or commit `.env`.

## Deploy to Streamlit Community Cloud

1. Extract the ZIP and open the `resumeiq` project folder in VS Code.
2. Create a GitHub repository (for example, `resumeiq`).
3. Commit and push the complete project:

```bash
git init
git add .
git commit -m "Build ResumeIQ AI resume analyzer"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/resumeiq.git
git push -u origin main
```

4. Sign in at [Streamlit Community Cloud](https://share.streamlit.io/).
5. Select **Create app**, connect GitHub and choose your repository and `main` branch.
6. Set the main file path to `app.py`.
7. Open **Advanced settings / Secrets** and add:

```toml
GROQ_API_KEY = "gsk_your_real_key_here"
```

8. Deploy. Streamlit installs packages from `requirements.txt`.

## Groq model

The default model is `openai/gpt-oss-120b`, selected because Groq currently lists it as a production model and supports strict/best-effort structured output modes. ResumeIQ requests JSON-object output and validates the returned structure before rendering. Model availability and account limits can change; check the [Groq model catalogue](https://console.groq.com/docs/models) if you need to change `MODEL` in `ai_engine.py`.

## Privacy and limitations

- The application does not write uploaded resumes to disk or a database.
- Resume text is held in Streamlit session state for the active session and sent to Groq to perform the requested analysis. Review Groq's terms and privacy documentation before processing sensitive personal data.
- Session state is temporary, but this is not a formal data-retention guarantee. Avoid uploading documents you are not authorised to process.
- Scanned/image-only PDFs need OCR before upload.
- AI output can be inaccurate. Verify every score explanation, skill classification and rewrite.
- The app is a candidate-support tool, not a hiring decision system or ATS compatibility guarantee.

## Screenshots

Add screenshots here after launching the app. Suggested captures:
- `screenshots/dashboard.png`
- `screenshots/analysis.png`
- `screenshots/skills-gap.png`

## Troubleshooting

- **Missing API key:** check `.env` locally or Streamlit Cloud Secrets. Restart the app after changing secrets.
- **401 from Groq:** verify the key is active and copied without extra quotes/spaces.
- **Rate limit:** wait and retry; limits depend on your Groq account.
- **Scanned PDF:** OCR the document and upload a searchable PDF.
- **Dependency issue:** use Python 3.11 and reinstall with `pip install -r requirements.txt`.
