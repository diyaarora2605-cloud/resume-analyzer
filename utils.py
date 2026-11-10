import os
import re
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_api_key() -> str:
    try:
        value=st.secrets.get("GROQ_API_KEY","")
        if value: return str(value).strip()
    except Exception:
        pass
    return os.getenv("GROQ_API_KEY","").strip()

def format_score(value) -> str:
    return f"{int(value)}/100"

def safe_filename(value: str) -> str:
    cleaned=re.sub(r"[^A-Za-z0-9_-]+","_",str(value)).strip("_")
    return (cleaned[:80] or "resume")
