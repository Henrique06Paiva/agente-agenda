import os
import streamlit as st

# Google Calendar Configuration
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Default Calendar ID (Can be overridden by secrets)
DEFAULT_CALENDAR_ID = "0ce24813f4e5f93ab0eefe3c671390f92227541c7a287177f3f7818a01642b05@group.calendar.google.com"
TIMEZONE = "America/Sao_Paulo"

def get_gemini_api_key() -> str:
    """Recupera a chave de API do Gemini a partir do st.secrets ou do ambiente."""
    if "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    return os.environ.get("GEMINI_API_KEY", "")

def get_calendar_id() -> str:
    """Recupera o ID da Agenda da Família a partir do st.secrets ou do valor padrão."""
    if "CALENDAR_ID" in st.secrets:
        return st.secrets["CALENDAR_ID"]
    return DEFAULT_CALENDAR_ID

def get_google_credentials_dict():
    """Recupera as credenciais estruturadas do Google do st.secrets, se disponíveis."""
    if "GOOGLE_CREDENTIALS" in st.secrets:
        return {"installed": dict(st.secrets["GOOGLE_CREDENTIALS"]["installed"])}
    return None
