import datetime
import os
from google import genai
from pydantic import BaseModel
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# 1. Definir a estrutura que a IA DEVE retornar
class EventoEstruturado(BaseModel):
    summary: str       # Título do evento
    description: str   # Descrição ou notas
    data_inicio: str   # Formato YYYY-MM-DD
    hora_inicio: str   # Formato HH:MM
    duracao_minutos: int

# 2. Função de Autenticação (A mesma que você testou)
def autenticar_agenda():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

# 3. Cérebro do Agente: Transforma texto livre em dados estruturados
def inteligenca_interpretar_texto(texto_usuario: str) -> EventoEstruturado:
    # IMPORTANTE: Inicialize com sua chave ou garanta que GEMINI_API_KEY está no ambiente
    client = genai.Client()
    
    # Passamos a data de hoje exata para a IA saber o que significa "próxima quarta" ou "amanhã"
    hoje = datetime.date.today().strftime("%Y-%m-%d")
    dia_semana = datetime.date.today().strftime("%A") # Ex: Monday
    
    prompt = f"""
    Você é um assistente executivo de alto nível. Seu trabalho é ler a mensagem do usuário e extrair os dados para criar um evento na agenda.
    Hoje é dia {hoje} ({dia_semana}).
    
    Mensagem do usuário: "{texto_usuario}"
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=dict(
            response_mime_type="application/json",
            response_schema=EventoEstruturado,
        ),
    )
    
    # Retorna o objeto Pydantic preenchido pela IA
    return EventoEstruturado.model_validate_json(response.text)

# 4. Ação: Pega os dados da IA e joga na API do Google
def criar_evento_na_agenda(evento: EventoEstruturado):
    creds = autenticar_agenda()
    
    try:
        service = build('calendar', 'v3', credentials=creds)
        
        # Combinar data e hora no formato ISO que o Google exige
        start_datetime = f"{evento.data_inicio}T{evento.hora_inicio}:00"
        
        # Calcular o horário de término baseado na duração
        inicio_dt = datetime.datetime.strptime(start_datetime, "%Y-%m-%dT%H:%M:%S")
        fim_dt = inicio_dt + datetime.timedelta(minutes=evento.duracao_minutos)
        end_datetime = fim_dt.isoformat()
        
        # Montar o payload do Google Calendar
        event_body = {
            'summary': evento.summary,
            'description': evento.description,
            'start': {
                'dateTime': start_datetime,
                'timeZone': 'America/Sao_Paulo', # Ajuste para o seu fuso
            },
            'end': {
                'dateTime': end_datetime,
                'timeZone': 'America/Sao_Paulo',
            },
        }
        
        # Enviar para a agenda principal ('primary')
        event = service.events().insert(calendarId='primary', body=event_body).execute()
        print(f"✅ Evento criado com sucesso! Link: {event.get('htmlLink')}")
        
    except HttpError as error:
        print(f"Erro ao interagir com o Google Calendar: {error}")

# 5. Execução de Teste do Agente
if __name__ == '__main__':
    # Certifique-se de definir a variável de ambiente antes de rodar, ou coloque o token direto no client.
    # No terminal: export GEMINI_API_KEY="sua_chave"
    
    comando = input("O que você quer agendar? ")
    print("Agente pensando...")
    
    evento_compreendido = inteligenca_interpretar_texto(comando)
    
    print("\n--- Dados que a IA entendeu ---")
    print(f"Título: {evento_compreendido.summary}")
    print(f"Data: {evento_compreendido.data_inicio} às {evento_compreendido.hora_inicio}")
    print(f"Duração: {evento_compreendido.duracao_minutos} minutos")
    print("--------------------------------\n")
    
    print("Salvando no Google Agenda...")
    criar_evento_na_agenda(evento_compreendido)