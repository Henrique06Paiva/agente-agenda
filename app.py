import datetime
import os
import streamlit as st

# Importações locais do nosso novo design modular
from src.config import get_gemini_api_key, get_calendar_id, TIMEZONE
from src.ai_service import AIService
from src.calendar_service import CalendarService

# Configurações da página do Streamlit
st.set_page_config(
    page_title="Agente de Agenda Inteligente",
    page_icon="🧙‍♂️",
    layout="wide", # Layout wide para melhor aproveitamento do painel
    initial_sidebar_state="expanded"
)

# Estilização CSS customizada para visual premium (Dark/Light adaptativo)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap');

/* Ajustar fonte geral da página */
html, body, [class*="css"], .stMarkdown {
    font-family: 'Outfit', sans-serif;
}

/* Título com degradê brilhante */
.title-gradient {
    background: linear-gradient(135deg, #a78bfa, #818cf8, #4f46e5);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: 0rem;
    padding-bottom: 0.2rem;
}

/* Card moderno para os eventos */
.event-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(128, 128, 128, 0.2);
    border-radius: 14px;
    padding: 20px;
    margin: 15px 0;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}
.event-card:hover {
    transform: translateY(-2px);
    border-color: rgba(99, 102, 241, 0.6);
    box-shadow: 0 15px 35px rgba(99, 102, 241, 0.1);
}

.event-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #818cf8;
    margin-bottom: 10px;
}

.event-detail-item {
    font-size: 0.95rem;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.badge-success {
    background: rgba(16, 185, 129, 0.15);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.3);
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    display: inline-block;
    margin-top: 10px;
}

/* Botões de Link no estilo da identidade do app */
.btn-calendar {
    display: inline-block;
    background: linear-gradient(135deg, #6366f1, #4f46e5);
    color: white !important;
    text-decoration: none;
    padding: 8px 16px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.88rem;
    margin-top: 12px;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25);
    transition: all 0.2s ease;
}
.btn-calendar:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(79, 70, 229, 0.45);
    background: linear-gradient(135deg, #4f46e5, #4338ca);
}

/* Badge de conexão na barra lateral */
.status-badge {
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 12px;
    border: 1px solid rgba(128, 128, 128, 0.15);
}
.status-ok {
    background: rgba(52, 211, 153, 0.1);
    color: #34d399;
}
.status-warn {
    background: rgba(248, 113, 113, 0.1);
    color: #f87171;
}
</style>
""", unsafe_allow_html=True)

# Helper para formatar a data que vem da API do Google Agenda
def formatar_data_evento(event_time_dict):
    if not event_time_dict:
        return "N/A"
    if 'dateTime' in event_time_dict:
        dt_str = event_time_dict['dateTime']
        try:
            # Tenta converter datetime ISO para exibição legível
            dt = datetime.datetime.fromisoformat(dt_str)
            return dt.strftime("%d/%m/%Y às %H:%M")
        except Exception:
            return dt_str
    elif 'date' in event_time_dict:
        dt_str = event_time_dict['date']
        try:
            dt = datetime.date.fromisoformat(dt_str)
            return dt.strftime("%d/%m/%Y")
        except Exception:
            return dt_str
    return "N/A"

# Inicialização de Serviços
try:
    ai_service = AIService()
    gemini_ativo = True
except Exception as e:
    gemini_ativo = False
    gemini_erro_msg = str(e)

calendar_service = CalendarService()

# --- BARRA LATERAL: Configurações e Status ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; margin-bottom: 20px;'>🧙‍♂️ Painel de Controle</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    # 1. Status do Google Calendar
    calendar_conectado = False
    try:
        creds = calendar_service.autenticar()
        if creds and creds.valid:
            calendar_conectado = True
    except Exception:
        pass
    
    st.markdown("### Conexões e Serviços")
    if calendar_conectado:
        st.markdown('<div class="status-badge status-ok">🟢 Google Agenda: Conectado</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-badge status-warn">🔴 Google Agenda: Desconectado</div>', unsafe_allow_html=True)

    if gemini_ativo:
        st.markdown('<div class="status-badge status-ok">🟢 Gemini API: Ativo</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-badge status-warn">🔴 Gemini API: Erro de API Key</div>', unsafe_allow_html=True)
        if not gemini_ativo:
            st.caption(f"Detalhe: {gemini_erro_msg}")
            
    st.markdown("---")
    
    # 2. Configurações da Agenda
    st.markdown("### Configurações Ativas")
    st.text_input("ID da Agenda", value=get_calendar_id(), disabled=True, help="Para alterar o ID da Agenda, configure 'CALENDAR_ID' no secrets.toml.")
    st.text_input("Fuso Horário", value=TIMEZONE, disabled=True)
    
    st.markdown("---")
    
    # 3. Ferramentas de Manutenção
    st.markdown("### Utilitários")
    if st.button("Limpar Token (Desconectar Google)", help="Remove o arquivo token.json local e força novo login na próxima interação."):
        if os.path.exists("token.json"):
            os.remove("token.json")
            st.success("Token removido! Recarregando página...")
            st.rerun()
        else:
            st.info("Nenhum token local foi encontrado.")

# --- CORPO PRINCIPAL ---
col1, col2 = st.columns([1, 12])
with col2:
    st.markdown('<h1 class="title-gradient">Assistente de Agenda Inteligente</h1>', unsafe_allow_html=True)
    st.markdown("Interaja por chat com o agente para agendar compromissos ou visualize os eventos da família em tempo real.")

# Criação de Abas
tab_chat, tab_agenda = st.tabs(["💬 Conversar com Agente", "📅 Visualizar Agenda da Família"])

# --- TAB 1: Chat de Interação com o Agente ---
with tab_chat:
    # Inicializa o histórico de mensagens na sessão se não existir
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant", 
                "content": "Olá! Sou o seu assistente de agenda familiar. O que você gostaria de planejar hoje? \n\n*Exemplo: 'Reunião de negócios quinta-feira às 15:00 com duração de 1 hora.'*"
            }
        ]

    # Mostra as mensagens anteriores na tela
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)

    # Input do Usuário
    if prompt_usuario := st.chat_input("Digite aqui o seu compromisso..."):
        # Mostra a mensagem do usuário
        with st.chat_message("user"):
            st.markdown(prompt_usuario)
        st.session_state.messages.append({"role": "user", "content": prompt_usuario})

        # Resposta do assistente
        with st.chat_message("assistant"):
            if not gemini_ativo:
                erro_msg = "🚨 **Erro:** O serviço do Gemini não está ativo. Por favor, configure a chave 'GEMINI_API_KEY' no seu painel de segredos."
                st.markdown(erro_msg)
                st.session_state.messages.append({"role": "assistant", "content": erro_msg})
            elif not calendar_conectado:
                erro_msg = "🚨 **Erro:** A conexão com o Google Agenda falhou ou não foi autorizada. Verifique as credenciais."
                st.markdown(erro_msg)
                st.session_state.messages.append({"role": "assistant", "content": erro_msg})
            else:
                with st.spinner("Analisando detalhes e agendando compromisso... 🧠"):
                    try:
                        # 1. IA interpreta o texto
                        evento = ai_service.interpretar_compromisso(prompt_usuario)
                        
                        # 2. Cria o evento no Google Calendar
                        link_agenda = calendar_service.criar_evento(evento)
                        
                        if link_agenda:
                            # Renderiza o cartão premium de sucesso
                            card_html = f"""
                            <div class="event-card">
                                <div class="event-title">📅 {evento.summary}</div>
                                <div class="event-detail-item">⏱️ <b>Data/Hora:</b> {evento.data_inicio} às {evento.hora_inicio}</div>
                                <div class="event-detail-item">⏳ <b>Duração:</b> {evento.duracao_minutos} minutos</div>
                                <div class="event-detail-item">📝 <b>Notas:</b> {evento.description or 'Sem notas adicionais.'}</div>
                                <div class="badge-success">Evento Agendado com Sucesso</div><br>
                                <a class="btn-calendar" href="{link_agenda}" target="_blank">Visualizar no Google Agenda</a>
                            </div>
                            """
                            st.markdown(card_html, unsafe_allow_html=True)
                            st.session_state.messages.append({"role": "assistant", "content": card_html})
                        else:
                            st.error("Não consegui cadastrar o evento na agenda. Verifique os detalhes.")
                            
                    except Exception as e:
                        resposta_erro = f"Desculpe, tive um problema ao salvar esse evento. Detalhe técnico: `{str(e)}`"
                        st.markdown(resposta_erro)
                        st.session_state.messages.append({"role": "assistant", "content": resposta_erro})

# --- TAB 2: Visualização dos Próximos Eventos ---
with tab_agenda:
    st.markdown("### 📅 Próximos Compromissos Agendados")
    st.write("Abaixo estão listados os próximos eventos na Agenda da Família.")

    # Botão para atualizar a lista manualmente
    col_ref, _ = st.columns([2, 10])
    with col_ref:
        refresh_btn = st.button("🔄 Atualizar Agenda")

    if not calendar_conectado:
        st.warning("Autentique sua conta Google para visualizar os próximos compromissos.")
    else:
        with st.spinner("Buscando compromissos futuros..."):
            eventos = calendar_service.listar_proximos_eventos(max_resultados=8)
            
            if not eventos:
                st.info("Nenhum compromisso agendado para os próximos dias.")
            else:
                # Exibição dos eventos futuros em colunas e cards bonitos
                for ev in eventos:
                    resumo = ev.get('summary', 'Compromisso Sem Título')
                    desc = ev.get('description', 'Sem descrição')
                    inicio = formatar_data_evento(ev.get('start'))
                    fim = formatar_data_evento(ev.get('end'))
                    link = ev.get('htmlLink', '#')
                    
                    st.markdown(f"""
                    <div class="event-card">
                        <div class="event-title">🗓️ {resumo}</div>
                        <div class="event-detail-item">⏰ <b>De:</b> {inicio}</div>
                        <div class="event-detail-item">⏰ <b>Até:</b> {fim}</div>
                        <div class="event-detail-item">📝 <b>Notas:</b> {desc}</div>
                        <a class="btn-calendar" href="{link}" target="_blank">Visualizar no Calendário</a>
                    </div>
                    """, unsafe_allow_html=True)