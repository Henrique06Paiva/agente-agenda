import datetime
import os
import streamlit as st
from google import genai
from pydantic import BaseModel
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configurações da página do Streamlit
st.set_page_config(page_title="Agente de Agenda da Família", page_icon="🧙‍♂️", layout="centered")

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Estrutura do Pydantic para a IA
class EventoEstruturado(BaseModel):
    summary: str
    description: str
    data_inicio: str
    hora_inicio: str
    duracao_minutos: int

# Funções do Google Agenda e IA que você já validou
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

def inteligenca_interpretar_texto(texto_usuario: str) -> EventoEstruturado:
    client = genai.Client() # Garanta que a variável GEMINI_API_KEY está configurada
    hoje = datetime.date.today().strftime("%Y-%m-%d")
    dia_semana = datetime.date.today().strftime("%A")
    
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
    return EventoEstruturado.model_validate_json(response.text)

def criar_evento_na_agenda(evento: EventoEstruturado):
    creds = autenticar_agenda()
    try:
        service = build('calendar', 'v3', credentials=creds)
        start_datetime = f"{evento.data_inicio}T{evento.hora_inicio}:00"
        inicio_dt = datetime.datetime.strptime(start_datetime, "%Y-%m-%dT%H:%M:%S")
        fim_dt = inicio_dt + datetime.timedelta(minutes=evento.duracao_minutos)
        end_datetime = fim_dt.isoformat()
        
        event_body = {
            'summary': evento.summary,
            'description': evento.description,
            'start': {'dateTime': start_datetime, 'timeZone': 'America/Sao_Paulo'},
            'end': {'dateTime': end_datetime, 'timeZone': 'America/Sao_Paulo'},
        }
        event = service.events().insert(calendarId='primary', body=event_body).execute()
        return event.get('htmlLink')
    except HttpError as error:
        st.error(f"Erro no Google Calendar: {error}")
        return None

# --- RENDERIZAÇÃO DA INTERFACE WEB ---

st.title("🧙‍♂️ Assistente de Agenda Inteligente")
st.write("Diga o que você tem para fazer e eu organizo a agenda da família para você!")

# Inicializa o histórico de mensagens na sessão se não existir
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! O que você gostaria de agendar hoje? (Ex: 'Reunião do projeto Estocaí quinta às 14h')"}
    ]

# Mostra as mensagens anteriores na tela
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Campo de entrada de texto (Chat Input)
if prompt_usuario := st.chat_input("Digite o compromisso aqui..."):
    # Mostra a mensagem do usuário no chat
    with st.chat_message("user"):
        st.markdown(prompt_usuario)
    st.session_state.messages.append({"role": "user", "content": prompt_usuario})

    # Resposta do agente
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking... 🧠")
        
        try:
            # 1. IA interpreta o texto
            evento = inteligenca_interpretar_texto(prompt_usuario)
            
            # 2. Cria o evento no Google
            link_agenda = criar_evento_na_agenda(evento)
            
            if link_agenda:
                resposta_sucesso = f"✅ **Entendido!** Agendei o compromisso:\n\n" \
                                   f"* **Título:** {evento.summary}\n" \
                                   f"* **Data:** {evento.data_inicio} às {evento.hora_inicio}\n" \
                                   f"* **Duração:** {evento.duracao_minutos} min\n\n" \
                                   f"[Clique aqui para ver na agenda]({link_agenda})"
                message_placeholder.markdown(resposta_sucesso)
                st.session_state.messages.append({"role": "assistant", "content": resposta_sucesso})
            else:
                st.error("Não consegui salvar o evento na agenda.")
                
        except Exception as e:
            resposta_erro = f"Desculpe, tive um problema ao processar esse pedido. Erro: {e}"
            message_placeholder.markdown(resposta_erro)
            st.session_state.messages.append({"role": "assistant", "content": resposta_erro})