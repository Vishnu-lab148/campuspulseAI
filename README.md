# CampusPulse AI Pro
### IBM Db2 + LangChain | Modern dark academic-support dashboard

CampusPulse AI is a student-success analytics prototype. It combines a dashboard, transparent early-support flags, trend visualizations, CSV/PDF exports, and an optional LangChain-powered assistant.

> **Honest status:** The code is packaged for local setup. Live IBM Db2 access and external AI calls are not claimed as tested. They depend on your credentials, network, database schema, and optional API key.

## Features
- Modern dark Streamlit dashboard
- Demo data mode (no credentials needed)
- IBM Db2 integration through `ibm_db`
- KPI cards, interactive Plotly charts, course/attendance filters
- Searchable student directory and explainable support flags
- Progress trends (synthetic demo trends; optional Db2 aggregate history table)
- LangChain prompt template with local fallback if no API key is configured
- Optional chat-model response via `langchain-openai`
- CSV export and PDF summary export
- Prototype login roles for faculty/admin
- Admin-only environment status and Db2 connection test
- SQL schema and seed files

## Windows setup in VS Code
1. Download and extract the ZIP.
2. In VS Code, choose **File → Open Folder** and select `CampusPulse_AI_Pro`.
3. Open **Terminal → New Terminal**.
4. Create a virtual environment:
   ```powershell
   python -m venv .venv
   ```
5. Activate it:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, use Command Prompt terminal and run:
   ```cmd
   .venv\Scripts\activate.bat
   ```
   Or continue using `python -m pip` without activating.
6. Install dependencies:
   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```
7. Run the app:
   ```powershell
   python -m streamlit run app.py
   ```
8. Open the local URL printed in terminal, usually `http://localhost:8501`.
9. Demo login: username `faculty`, password `campus123`. Admin demo: `admin`, password `admin123`.

If package installation fails, copy the full error text. `ibm_db` can have environment-specific installation requirements on Windows; the demo mode still requires the dependencies in `requirements.txt`, including the Db2 driver package as currently listed.

## IBM Db2 setup
1. Obtain your own IBM Db2 database/service and connection details.
2. Copy `.env.example` to `.env` in the project root and fill in the values.
3. Do not share or commit `.env`. The app uses `python-dotenv` to load local environment variables.
4. Open your Db2 SQL console and run `schema.sql`, then `seed.sql`.
5. For trend history, also run `schema_history.sql`, then `seed_history.sql`.
6. Restart the app, select **IBM Db2** in the sidebar, sign in as admin, and use **Settings → Test IBM Db2 connection**.
7. Confirm the table names and permissions in your Db2 instance. The app's live student query expects `CAMPUSPULSE_STUDENTS`; trend history expects `CAMPUSPULSE_HISTORY`.

The connection string currently requests SSL (`SECURITY=SSL`). Adjust only according to the connection requirements documented for your Db2 service.

## Optional AI setup
- Add a valid API key to `.env` as `OPENAI_API_KEY=...` to enable the optional `langchain-openai` model call.
- Keep it blank to use the local fallback.
- Never put API keys into GitHub, screenshots, or public demos.
- LLM provider responses are not verified in this package; test with your own authorized credentials.

## What the support flag means
The demo rule flags a record when attendance is below 75% OR assessment score is below 40. It is an illustrative threshold, not a validated predictive model. It does not establish why a student may be struggling. Educators must review records and speak with students before acting.

## Demo flow (3 minutes)
1. Sign in with the faculty demo account.
2. Show KPI cards and the attendance-versus-score chart.
3. Filter by course and attendance.
4. Search for a sample student and explain why a record is flagged.
5. Open Progress trends; explain that demo trends are synthetic.
6. Ask the AI assistant for an attendance plan; show local fallback or optional model mode.
7. Export a CSV and PDF.
8. Explain how live mode connects to Db2 and show the connection test only if configured.
9. Close with privacy, human review, and future improvements.

## Submission checklist from the event image
- [ ] Register on Luma and retain confirmation email.
- [ ] Join the official WhatsApp community and check pinned updates.
- [ ] Submit individually (screenshot states no teams).
- [ ] Build using IBM Db2 + one framework (this project uses LangChain).
- [ ] Open a GitHub pull request using the event's official repository/template.
- [ ] Submit the official Google Form and post on LinkedIn.
- [ ] Verify exact deadline and links with the organizer; links are not included in the screenshot provided.

## Production hardening before real deployment
- Replace prototype passwords with institutional SSO and secure session handling.
- Add per-role database permissions, audit logs, and data retention controls.
- Restrict access to student-level exports.
- Review privacy obligations and obtain institutional authorization.
- Validate thresholds and intervention efficacy with educators.
- Add automated tests and deployment secrets management.

## Stack
Python · Streamlit · IBM Db2 · LangChain · Plotly · Pandas · ReportLab
