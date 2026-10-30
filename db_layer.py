import os
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

DEMO_STUDENTS = [
    {"student_id":"S1001","name":"Aarav","course":"BCA","attendance":92,"score":81},
    {"student_id":"S1002","name":"Diya","course":"BCA","attendance":68,"score":58},
    {"student_id":"S1003","name":"Kabir","course":"BCA","attendance":74,"score":36},
    {"student_id":"S1004","name":"Meera","course":"BCA","attendance":88,"score":73},
    {"student_id":"S1005","name":"Ishaan","course":"BCA","attendance":61,"score":42},
    {"student_id":"S1006","name":"Anaya","course":"BCA","attendance":95,"score":89},
    {"student_id":"S1007","name":"Reyansh","course":"BCA","attendance":79,"score":48},
    {"student_id":"S1008","name":"Sara","course":"BCA","attendance":70,"score":33},
]

def get_connection():
    try:
        import ibm_db
    except ImportError as exc:
        raise RuntimeError("ibm_db is not installed. Run: python -m pip install -r requirements.txt") from exc
    required = ["DB2_HOST", "DB2_PORT", "DB2_DATABASE", "DB2_USERNAME", "DB2_PASSWORD"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise RuntimeError("Missing environment variables: " + ", ".join(missing))
    dsn = (
        f"DATABASE={os.environ['DB2_DATABASE']};"
        f"HOSTNAME={os.environ['DB2_HOST']};"
        f"PORT={os.environ['DB2_PORT']};PROTOCOL=TCPIP;"
        f"UID={os.environ['DB2_USERNAME']};PWD={os.environ['DB2_PASSWORD']};SECURITY=SSL;"
    )
    return ibm_db.connect(dsn, "", "")

def db2_connection_test():
    try:
        import ibm_db
        conn = get_connection()
        ibm_db.close(conn)
        return True, "Connection opened and closed successfully. This confirms credentials/network only, not that the schema or app queries are valid."
    except Exception as exc:
        return False, f"Db2 connection failed: {exc}"

def _query(sql):
    import ibm_db
    conn = get_connection()
    try:
        stmt = ibm_db.exec_immediate(conn, sql)
        rows = []
        row = ibm_db.fetch_assoc(stmt)
        while row:
            rows.append({str(k).lower(): v for k, v in row.items()})
            row = ibm_db.fetch_assoc(stmt)
        return rows
    finally:
        ibm_db.close(conn)

def load_students(use_db2=False):
    if not use_db2:
        return pd.DataFrame(DEMO_STUDENTS)
    rows = _query("SELECT STUDENT_ID, NAME, COURSE, ATTENDANCE, SCORE FROM CAMPUSPULSE_STUDENTS ORDER BY NAME")
    return pd.DataFrame(rows, columns=["student_id","name","course","attendance","score"]) if rows else pd.DataFrame(columns=["student_id","name","course","attendance","score"])

def load_history(use_db2=False):
    if not use_db2:
        # Clearly synthetic history generated for the demo; not real historical student records.
        dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=8, freq="W")
        rows = []
        for i, d in enumerate(dates):
            rows.append({"record_date": d.date(), "attendance": 68 + i * 2.0, "score": 48 + i * 2.7})
        return pd.DataFrame(rows)
    try:
        rows = _query("SELECT RECORD_DATE, AVG_ATTENDANCE AS ATTENDANCE, AVG_SCORE AS SCORE FROM CAMPUSPULSE_HISTORY ORDER BY RECORD_DATE")
        return pd.DataFrame(rows)
    except Exception:
        # Keep main dashboard available if optional history table has not been created.
        return pd.DataFrame()

