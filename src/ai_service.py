import datetime
from google import genai
from pydantic import BaseModel, Field
from src.config import get_gemini_api_key

class EventoEstruturado(BaseModel):
    summary: str = Field(description="Título ou resumo curto e claro do evento.")
    description: str = Field(description="Descrição ou observações detalhadas do evento.")
    data_inicio: str = Field(description="Data de início do evento no formato YYYY-MM-DD.")
    hora_inicio: str = Field(description="Hora de início do evento no formato HH:MM (24h).")
    duracao_minutos: int = Field(description="Duração estimada do evento em minutos.")

class AIService:
    def __init__(self):
        self.api_key = get_gemini_api_key()
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY não foi encontrada nas configurações.")
        self.client = genai.Client(api_key=self.api_key)

    def interpretar_compromisso(self, texto_usuario: str) -> EventoEstruturado:
        """Usa o Gemini 2.5 Flash para extrair dados estruturados de compromisso a partir do texto do usuário."""
        hoje = datetime.date.today().strftime("%Y-%m-%d")
        dia_semana = datetime.date.today().strftime("%A")
        
        # Mapeamento simples de dia da semana em inglês para português para ajudar o modelo
        dias_traduzidos = {
            "Monday": "Segunda-feira",
            "Tuesday": "Terça-feira",
            "Wednesday": "Quarta-feira",
            "Thursday": "Quinta-feira",
            "Friday": "Sexta-feira",
            "Saturday": "Sábado",
            "Sunday": "Domingo"
        }
        dia_semana_pt = dias_traduzidos.get(dia_semana, dia_semana)

        prompt = f"""
        Você é um assistente executivo de alto nível da família. Seu trabalho é analisar a mensagem do usuário e extrair os detalhes do evento para inserção no Google Agenda.
        
        Contexto Atual:
        - Hoje é dia: {hoje} ({dia_semana_pt})
        
        Instruções importantes:
        - Deduza as datas com base no dia de hoje ({hoje}). Por exemplo, se hoje é segunda e o usuário fala 'quinta às 14h', calcule a data correta da próxima quinta-feira.
        - Caso a duração não seja explicitada, adote um padrão razoável (por exemplo, 60 minutos para reuniões/consultas, 120 minutos para festas, etc.).
        - Se a mensagem contiver informações adicionais importantes, adicione-as no campo 'description'.
        
        Mensagem do usuário: "{texto_usuario}"
        """
        
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=dict(
                response_mime_type="application/json",
                response_schema=EventoEstruturado,
            ),
        )
        
        return EventoEstruturado.model_validate_json(response.text)
