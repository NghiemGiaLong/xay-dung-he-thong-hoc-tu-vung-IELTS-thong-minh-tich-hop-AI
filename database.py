import pyodbc

# --- KẾT NỐI DATABASE (SQL SERVER) ---
def get_connection():
    conn_str = (
        r'DRIVER={ODBC Driver 17 for SQL Server};'
        r'SERVER=(localdb)\MSSQLLocalDB;'
        r'DATABASE=IELTS_AI_DB;'
        r'Trusted_Connection=yes;'
    )
    return pyodbc.connect(conn_str)