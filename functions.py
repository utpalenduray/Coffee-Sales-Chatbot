from logzero import logger
import sqlite3
from langchain_core.messages import SystemMessage, RemoveMessage
from systemPrompt import ASSISTANT_PROMPT
import re

def connect_sql_lite_db(db_path):
    """Establish connection to SQLite database"""
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        return connection, cursor
    except Exception as e:
        logger.error(f"Failed to connect to SQLite: {e}")
        raise Exception(f"Database connection error: {e}")

def clean_sql_query(query):
    query = re.sub(r'```sql|```', '', query).strip()
    query = query.replace("\r", " ").replace("\n", " ")
    query = re.sub(r'\s+', ' ', query).strip()
    query = re.sub(r"\bLIKE\s+'%([^%]+)%'", r"LIKE '%\1%'", query)
    query = re.sub(r";\s*$", "", query)
    return query

