import os
from datetime import date
import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv

from db_layer import load_students, load_history, db2_connection_test
from analytics import calculate_summary, apply_filters, support_flags, make_trend_data
from ai_assistant import generate_advice
from reports import build_pdf_report

load_dotenv()
st.set_page_config(page_title="CampusPulse AI", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

# Dark, polished visual system
st.markdown("""
<style>
:root { color-scheme: dark; }
.stApp { background: radial-gradient(circle at 15% 0%, #17233a 0, #0b1020 38%, #080c16 100%); }
.block-container { padding-top: 1.4rem; max-width: 1500px; }
[data-testid="stSidebar"] { background: #0b1220; border-right: 1px solid #25324a; }
.hero { padding: 1.3rem 1.5rem; border: 1px solid #2b3b57; border-radius: 18px;
        background: linear-gradient(120deg, rgba(29,78,216,.24), rgba(13,148,136,.12)); margin-bottom: 1rem; }
.hero h1 { margin: 0; font-size: 2rem; letter-spacing: -.04em; }
.hero p { color: #a8b8d4; margin: .45rem 0 0 0; }
.kpi { border: 1px solid #27364f; border-radius: 16px; padding: 1rem 1.1rem;
       background: linear-gradient(145deg, rgba(22,34,56,.92), rgba(12,19,33,.92)); min-height: 115px; }
.kpi-label { color: #9db0ce; font-size: .86rem; }
.kpi-value { color: #f3f7ff; font-size: 1.8rem; font-weight: 750; margin-top: .2rem; }
.kpi-note { color: #7dd3c7; font-size: .78rem; margin-top: .25rem; }
.section-title { font-size: 1.1rem; font-weight: 700; margin: .3rem 0 .7rem 0; }
div[data-testid="stMetric"] { background: #101a2b; padding: 12px 14px; border: 1px solid #293954; border-radius: 14px; }
.stButton > button { border-radius: 10px; border: 1px solid #365078; }
</style>
""", unsafe_allow_html=True)

DEMO_USERS = {
    "faculty": {"password": "campus123", "role": "Faculty"},
    "admin": {"password": "admin123", "role": "Administrator"},
}

def login_gate():
    if st.session_state.get("authenticated"):
        return
    st.markdown('<div class="hero"><h1><span style="color:#96d334">CampusPulse AI</span></h1><p>Student success intelligence • Db2 + LangChain</p></div>', unsafe_allow_html=True)
    st.info("Demo sign-in is only a prototype convenience. Replace it with institutional SSO before production.")
    with st.form("login_form"):
        username = st.text_input("Demo username", value="faculty")
        password = st.text_input("Password", type="password", value="campus123")
        submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)
    st.caption("Demo accounts: faculty / campus123 · admin / admin123")
    if submitted:
        record = DEMO_USERS.get(username.strip().lower())
        if record and password == record["password"]:
            st.session_state.authenticated = True
            st.session_state.role = record["role"]
            st.session_state.username = username.strip().lower()
            st.rerun()
        else:
            st.error("Incorrect demo username or password.")
    st.stop()

login_gate()

with st.sidebar:
    st.markdown("## ◈ CampusPulse")
    st.caption("AI student support console")
    source = st.selectbox("Data source", ["Demo data", "IBM Db2"], help="Demo data works without credentials.")
    st.markdown("---")
    st.markdown(f"**Signed in as:** {st.session_state.get('role', 'Faculty')}")
    if st.button("Sign out", use_container_width=True):
        for key in ["authenticated", "role", "username"]:
            st.session_state.pop(key, None)
        st.rerun()
    st.markdown("---")
    st.caption("Build: Pro prototype · v2.0")

use_db2 = source == "IBM Db2"
try:
    students_df = load_students(use_db2)
    history_df = load_history(use_db2)
    source_status = "IBM Db2 selected" if use_db2 else "Synthetic demo dataset"
    source_color = "#3496d3" if use_db2 else "#93c5fd"
except Exception as exc:
    st.error(f"Could not load data from the selected source: {exc}")
    st.warning("For Db2 mode, check your environment variables, database schema, network access, and SSL settings. Switch to Demo data to keep exploring.")
    st.stop()

st.markdown(f"""
<div class="hero">
  <h1><span style="color:#96d334">CampusPulse AI</span></h1>
  <p>Make academic signals actionable. Explore performance, spot support needs, and plan evidence-informed interventions.</p>
  <p style="margin-top:.75rem"><span style="color:{source_color}">●</span> {source_status} &nbsp; · &nbsp; Updated {date.today().strftime("%d %b %Y")}</p>
</div>
""", unsafe_allow_html=True)

if students_df.empty:
    st.warning("No student records found. Add records using schema.sql and seed.sql, or switch to Demo data.")
    st.stop()

# Normalize expected columns
required_cols = ["student_id", "name", "course", "attendance", "score"]
missing = [c for c in required_cols if c not in students_df.columns]
if missing:
    st.error("Dataset is missing required fields: " + ", ".join(missing))
    st.stop()

students_df["attendance"] = pd.to_numeric(students_df["attendance"], errors="coerce").fillna(0)
students_df["score"] = pd.to_numeric(students_df["score"], errors="coerce").fillna(0)
flagged_df = support_flags(students_df)
summary = calculate_summary(students_df, flagged_df)

# Filters
with st.expander("🔎 Filter dashboard", expanded=True):
    f1, f2, f3 = st.columns([1, 1, 1])
    courses = sorted(students_df["course"].dropna().astype(str).unique().tolist())
    selected_courses = f1.multiselect("Course", courses, default=courses)
    min_att = f2.slider("Minimum attendance (%)", 0, 100, 0)
    max_att = f3.slider("Maximum attendance (%)", 0, 100, 100)
filtered_df = apply_filters(students_df, selected_courses, min_att, max_att)
filtered_flags = support_flags(filtered_df)
filtered_summary = calculate_summary(filtered_df, filtered_flags)

kcols = st.columns(4)
kpis = [
    ("TOTAL STUDENTS", f"{filtered_summary['total']:,}", "In current filters"),
    ("AVG ATTENDANCE", f"{filtered_summary['attendance']:.1f}%", "Attendance indicator"),
    ("AVG ASSESSMENT", f"{filtered_summary['score']:.1f}/100", "Assessment average"),
    ("NEED A CHECK-IN", f"{filtered_summary['flagged']:,}", "Rule-based support flags"),
]
for col, (label, value, note) in zip(kcols, kpis):
    col.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-note">{note}</div></div>', unsafe_allow_html=True)

tab_overview, tab_students, tab_trends, tab_ai, tab_reports, tab_admin = st.tabs(
    ["Overview", "Students", "Progress trends", "AI assistant", "Reports", "Settings"]
)

with tab_overview:
    left, right = st.columns([1.35, 1])
    with left:
        st.markdown('<div class="section-title">Attendance vs assessment</div>', unsafe_allow_html=True)
        chart_df = filtered_df.copy()
        fig = px.scatter(
            chart_df, x="attendance", y="score", color="course", hover_name="name",
            hover_data=["student_id"], labels={"attendance":"Attendance (%)","score":"Assessment score"},
            template="plotly_dark"
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=390, legend_title_text="Course")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown('<div class="section-title">Support overview</div>', unsafe_allow_html=True)
        counts = pd.DataFrame({"Status": ["Review recommended", "No current flag"], "Students": [
            len(filtered_flags), max(0, len(filtered_df)-len(filtered_flags))
        ]})
        fig2 = px.pie(counts, names="Status", values="Students", hole=.68, template="plotly_dark",
                      color_discrete_sequence=["#f59e0b", "#14b8a6"])
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=320, legend_title_text="")
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("Flags are transparent indicators for supportive human review, not a diagnosis or an automated decision.")
    st.markdown("#### Recommended next actions")
    a1, a2, a3 = st.columns(3)
    a1.info("**Check in privately**\n\nAsk students what support would help before drawing conclusions.")
    a2.info("**Offer focused revision**\n\nUse short quizzes and topic-wise catch-up sessions.")
    a3.info("**Review progress**\n\nCompare trends after two weeks and adjust the support plan.")

with tab_students:
    st.markdown("#### Student directory")
    search = st.text_input("Search by name or student ID", placeholder="e.g. S1002 or Diya")
    view_df = filtered_df.copy()
    if search.strip():
        mask = view_df["name"].astype(str).str.contains(search, case=False, na=False) | view_df["student_id"].astype(str).str.contains(search, case=False, na=False)
        view_df = view_df[mask]
    view_df["support_reason"] = view_df.apply(
        lambda r: "Low attendance" if r["attendance"] < 75 and r["score"] >= 40
        else "Low score" if r["score"] < 40 and r["attendance"] >= 75
        else "Low attendance + low score" if r["attendance"] < 75 and r["score"] < 40
        else "No current flag", axis=1
    )
    st.dataframe(view_df, use_container_width=True, hide_index=True)
    st.caption("Prototype flag rule: attendance below 75% OR assessment score below 40/100. Validate thresholds with educators before real use.")

with tab_trends:
    st.markdown("#### Progress over time")
    trend_df = make_trend_data(history_df, filtered_df)
    if trend_df.empty:
        st.info("No dated history records are available. The demo includes a synthetic trend series; for Db2 mode, add rows to CAMPUSPULSE_HISTORY using seed_history.sql.")
    else:
        metric = st.radio("Trend metric", ["Attendance", "Assessment score"], horizontal=True)
        ycol = "attendance" if metric == "Attendance" else "score"
        trend_agg = trend_df.groupby("record_date", as_index=False)[ycol].mean()
        trend_agg["record_date"] = pd.to_datetime(trend_agg["record_date"])
        fig3 = px.line(trend_agg, x="record_date", y=ycol, markers=True, template="plotly_dark",
                       labels={ycol: metric, "record_date": "Date"}, title=f"Average {metric.lower()} over time")
        fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=360)
        st.plotly_chart(fig3, use_container_width=True)
        st.dataframe(trend_agg, use_container_width=True, hide_index=True)

with tab_ai:
    st.markdown("#### Ask CampusPulse")
    st.write("Get practical suggestions grounded in the current filtered metrics. AI mode uses LangChain and requires an API key; otherwise a local fallback is used.")
    examples = ["How can we improve attendance?", "Which students may need support and why?", "Suggest a two-week revision plan."]
    prompt_choice = st.selectbox("Example question", ["Write my own…"] + examples)
    question = st.text_area("Your question", value="" if prompt_choice == "Write my own…" else prompt_choice, height=90)
    if st.button("Generate recommendations", type="primary", key="ask_ai"):
        with st.spinner("Preparing recommendations..."):
            result, mode_label = generate_advice(question, filtered_summary, filtered_flags.to_dict(orient="records"))
        st.markdown(f"**Response mode:** `{mode_label}`")
        st.markdown(result)
        st.caption("Do not enter sensitive personal information. AI output is advisory and should be reviewed by a human.")
    with st.expander("What powers this feature?"):
        st.write("A LangChain PromptTemplate structures the question and aggregate context. If OPENAI_API_KEY is set, the app can call a configured chat model. Otherwise, a deterministic local response is returned.")

with tab_reports:
    st.markdown("#### Export current view")
    report_df = filtered_df.copy()
    csv_bytes = report_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇ Download CSV", data=csv_bytes, file_name="campuspulse_students.csv", mime="text/csv", use_container_width=True)
    try:
        pdf_bytes = build_pdf_report(filtered_summary, report_df, filtered_flags)
        st.download_button("⬇ Download PDF summary", data=pdf_bytes, file_name="campuspulse_summary.pdf", mime="application/pdf", use_container_width=True)
    except Exception as exc:
        st.warning(f"PDF export is not available yet: {exc}")
    st.caption("Export only data you are authorized to access. Use synthetic data for public demos.")

with tab_admin:
    st.markdown("#### Connection and prototype settings")
    st.write(f"**Current source:** {source_status}")
    st.write(f"**Current role:** {st.session_state.get('role', 'Faculty')}")
    if st.session_state.get("role") == "Administrator":
        st.markdown("**Environment variable status**")
        for key in ["DB2_HOST", "DB2_PORT", "DB2_DATABASE", "DB2_USERNAME", "DB2_PASSWORD", "OPENAI_API_KEY"]:
            st.write(f"{'Configured' if os.getenv(key) else 'Not configured'} — `{key}`")
        if st.button("Test IBM Db2 connection"):
            ok, message = db2_connection_test()
            (st.success if ok else st.error)(message)
    else:
        st.info("Administrator-only diagnostics are hidden from the faculty demo role.")
    st.markdown("#### Responsible-use notes")
    st.write("- Demo login is not production authentication. Use institutional SSO in deployment.")
    st.write("- Student support flags are explainable indicators and must be reviewed by educators.")
    st.write("- Apply least-privilege database access and privacy/retention policies.")
    st.write("- Never commit `.env`, API keys, or real student records to GitHub.")

st.markdown("---")
st.caption("CampusPulse AI · Prototype for academic support · Sample data is synthetic · Human review required")
