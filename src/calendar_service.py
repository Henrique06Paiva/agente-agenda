import datetime
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import streamlit as st

from src.config import SCOPES, get_calendar_id, get_google_credentials_dict, TIMEZONE
from src.ai_service import EventoEstruturado

class CalendarService:
    def __init__(self):
        self.creds = None
        self.calendar_id = get_calendar_id()

    def autenticar(self) -> Credentials:
        """Realiza a autenticação com a API do Google Agenda, gerenciando tokens locais ou segredos do Streamlit."""
        if os.path.exists('token.json'):
            try:
                self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            except Exception:
                # Se o token estiver corrompido, limpa e força reautenticação
                self.creds = None

        # Se não houver credenciais válidas, tenta atualizá-las ou criar novas
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception:
                    self.creds = None
            else:
                self.creds = None
            
            if not self.creds:
                creds_dict = get_google_credentials_dict()
                if creds_dict:
                    flow = InstalledAppFlow.from_client_config(creds_dict, SCOPES)
                    self.creds = flow.run_local_server(port=0)
                else:
                    if os.path.exists('credentials.json'):
                        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                        self.creds = flow.run_local_server(port=0)
                    else:
                        raise FileNotFoundError(
                            "Credenciais do Google não encontradas. Configure o secret 'GOOGLE_CREDENTIALS' ou forneça 'credentials.json'."
                        )

            # Salva o token para a próxima execução local
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())
                
        return self.creds

    def criar_evento(self, evento: EventoEstruturado) -> str:
        """Cria um evento na agenda e retorna o link de visualização (HTML Link)."""
        creds = self.autenticar()
        try:
            service = build('calendar', 'v3', credentials=creds)
            
            # Converte data e hora para string datetime ISO
            start_datetime = f"{evento.data_inicio}T{evento.hora_inicio}:00"
            inicio_dt = datetime.datetime.strptime(start_datetime, "%Y-%m-%dT%H:%M:%S")
            fim_dt = inicio_dt + datetime.timedelta(minutes=evento.duracao_minutos)
            end_datetime = fim_dt.isoformat()
            
            event_body = {
                'summary': evento.summary,
                'description': evento.description,
                'start': {'dateTime': start_datetime, 'timeZone': TIMEZONE},
                'end': {'dateTime': end_datetime, 'timeZone': TIMEZONE},
            }
            
            event = service.events().insert(calendarId=self.calendar_id, body=event_body).execute()
            return event.get('htmlLink')
        except HttpError as error:
            st.error(f"Erro ao interagir com a API do Google Agenda: {error}")
            raise error

    def listar_proximos_eventos(self, max_resultados: int = 7) -> list:
        """Recupera os próximos eventos agendados a partir de agora."""
        creds = self.autenticar()
        try:
            service = build('calendar', 'v3', credentials=creds)
            agora = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indica tempo UTC
            
            events_result = service.events().list(
                calendarId=self.calendar_id,
                timeMin=agora,
                maxResults=max_resultados,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events_result.get('items', [])
        except HttpError as error:
            st.error(f"Erro ao buscar os eventos do Google Agenda: {error}")
            return []
