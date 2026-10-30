import pandas as pd

def support_flags(df):
    if df.empty:
        return df.copy()
    return df[(pd.to_numeric(df["attendance"], errors="coerce") < 75) |
              (pd.to_numeric(df["score"], errors="coerce") < 40)].copy()

def calculate_summary(df, flags=None):
    if df.empty:
        return {"total":0, "attendance":0.0, "score":0.0, "flagged":0}
    flags = support_flags(df) if flags is None else flags
    return {
        "total": int(len(df)),
        "attendance": float(pd.to_numeric(df["attendance"], errors="coerce").fillna(0).mean()),
        "score": float(pd.to_numeric(df["score"], errors="coerce").fillna(0).mean()),
        "flagged": int(len(flags)),
    }

def apply_filters(df, courses, min_att, max_att):
    out = df.copy()
    if courses:
        out = out[out["course"].astype(str).isin(courses)]
    out = out[(out["attendance"] >= min_att) & (out["attendance"] <= max_att)]
    return out

def make_trend_data(history, current_students):
    if history is not None and not history.empty and {"record_date","attendance","score"}.issubset(history.columns):
        return history.copy()
    if current_students.empty:
        return pd.DataFrame()
    # If no dated history is available, make a demo-only illustrative aggregate series.
    # It is not a prediction and is not presented as real individual history.
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=6, freq="W")
    avg_att = float(current_students["attendance"].mean())
    avg_score = float(current_students["score"].mean())
    return pd.DataFrame({
        "record_date": dates,
        "attendance": [max(0, min(100, avg_att - 5 + i * 1.0)) for i in range(6)],
        "score": [max(0, min(100, avg_score - 4 + i * .8)) for i in range(6)]
    })
