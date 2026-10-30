import os
from langchain_core.prompts import PromptTemplate

PROMPT = PromptTemplate.from_template("""
You are CampusPulse AI, a careful academic-support assistant.
Use only the aggregate metrics and flagged records below. Be supportive and practical.
Never shame students, infer protected traits, diagnose causes, or recommend punishment.
Do not claim a flag proves a student is failing. Explain that a human educator must review suggestions.
Metrics: {summary}
Flagged records: {records}
Question: {question}
Return concise recommendations with 3-5 actionable steps.
""")

def generate_advice(question, summary, flagged_records):
    question = (question or "").strip() or "Summarize the current snapshot and suggest supportive next steps."
    context = PROMPT.format(summary=str(summary), records=str(flagged_records[:20]), question=question)
    if os.getenv("OPENAI_API_KEY"):
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.output_parsers import StrOutputParser
            model = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0.2)
            chain = PROMPT | model | StrOutputParser()
            answer = chain.invoke({"summary": str(summary), "records": str(flagged_records[:20]), "question": question})
            return answer, "LangChain + configured chat model"
        except Exception as exc:
            return _local_answer(question, summary, flagged_records) + f"\n\n*AI provider unavailable; local fallback used. Technical detail: {exc}*", "Local fallback"
    return _local_answer(question, summary, flagged_records), "Local fallback (no API key configured)"

def _local_answer(question, summary, records):
    q = question.lower()
    total = summary.get("total", 0)
    att = summary.get("attendance", 0)
    score = summary.get("score", 0)
    flagged = summary.get("flagged", 0)
    names = ", ".join(str(r.get("name", "Student")) for r in records[:5]) or "No records currently flagged"
    if "attendance" in q:
        focus = f"Average attendance is {att:.1f}%. Review class schedules and attendance patterns, ask students about barriers privately, share missed materials, and follow up weekly."
    elif any(x in q for x in ["score", "marks", "performance", "revision"]):
        focus = f"Average assessment score is {score:.1f}/100. Offer topic-wise revision, low-stakes quizzes, office hours, and peer study sessions, then review progress in two weeks."
    else:
        focus = f"Current snapshot: {total} students, {att:.1f}% average attendance, {score:.1f}/100 average score, and {flagged} support flags."
    return (
        f"### Suggested support plan\n\n{focus}\n\n"
        f"1. **Review signals:** {flagged} record(s) meet the prototype rule (attendance below 75% or score below 40).\n"
        f"2. **Check in privately:** Review records with an educator before contacting anyone. Example names in the current watchlist: {names}.\n"
        "3. **Offer options:** Share catch-up notes, tutoring, revision resources, or a flexible check-in.\n"
        "4. **Track outcomes:** Record a dated follow-up and compare progress after two weeks.\n"
        "5. **Use human judgment:** These are simple indicators, not proof of a cause or a final decision."
    )
