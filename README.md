# 🧙‍♂️ Agente de Agenda Inteligente da Família

O **Agente de Agenda Inteligente** é uma aplicação construída com Streamlit que utiliza inteligência artificial de última geração (Gemini 2.5 Flash) para ler textos em linguagem natural fornecidos pelo usuário, interpretar os detalhes do compromisso e agendá-los automaticamente no Google Agenda. O sistema também exibe em tempo real os próximos compromissos da família em um painel elegante.

---

## 🏗️ Arquitetura do Projeto

O projeto foi reestruturado seguindo as melhores práticas de desenvolvimento de software, separando a interface do usuário, as configurações globais e os serviços de backend (IA e Google Calendar).

### Estrutura de Arquivos

```
agente-agenda/
├── .streamlit/
│   └── secrets.toml          # Segredos (Chave Gemini e credenciais Google)
├── src/
│   ├── __init__.py           # Inicializador do pacote python
│   ├── config.py             # Configurações globais e leitura segura de segredos
│   ├── ai_service.py         # Conexão com a API do Gemini e esquema Pydantic
│   └── calendar_service.py   # Conexão, autenticação e listagem de eventos no Google
├── app.py                    # Interface web do usuário (Streamlit)
├── credentials.json          # Arquivo do Google Console para login local
├── token.json                # Token de autorização OAuth gerado automaticamente
├── requirements.txt          # Dependências do projeto
└── README.md                 # Esta documentação do projeto
```

### Componentes Principais

1. **[config.py](file:///c:/Users/Henrique%20Paiva/OneDrive%20-%20AMAZONAS%20INOVARE%20TECNOLOGIA%20LTDA/Projetos%20Amazonas/agente-agenda/src/config.py)**: Centraliza a leitura das chaves e definições de constantes como fuso horário e escopos de acesso do Google API.
2. **[ai_service.py](file:///c:/Users/Henrique%20Paiva/OneDrive%20-%20AMAZONAS%20INOVARE%20TECNOLOGIA%20LTDA/Projetos%20Amazonas/agente-agenda/src/ai_service.py)**: Lida com a API do Gemini. Usa **Structured Outputs** forçando o modelo a responder com base em uma classe Pydantic `EventoEstruturado`, garantindo previsibilidade de dados (título, descrição, data de início, hora de início e duração).
3. **[calendar_service.py](file:///c:/Users/Henrique%20Paiva/OneDrive%20-%20AMAZONAS%20INOVARE%20TECNOLOGIA%20LTDA/Projetos%20Amazonas/agente-agenda/src/calendar_service.py)**: Responsável pelo fluxo de autenticação do Google API OAuth2. Salva o token gerado em um arquivo local `token.json`. Além de criar eventos, contém o recurso para recuperar e mostrar compromissos futuros.
4. **[app.py](file:///c:/Users/Henrique%20Paiva/OneDrive%20-%20AMAZONAS%20INOVARE%20TECNOLOGIA%20LTDA/Projetos%20Amazonas/agente-agenda/app.py)**: Gerencia o visual moderno com CSS customizado, exibição de abas (Chat e Painel de Agenda), sidebar com status de conexão em tempo real (Semáforos 🟢/🔴) e logs de erros tratados.

---

## 🛠️ Configuração e Instalação

### Pré-requisitos

Certifique-se de ter o Python 3.9+ instalado em sua máquina.

1. **Instalar Dependências**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Obter Credenciais do Google Cloud**:
   - Vá para o [Google Cloud Console](https://console.cloud.google.com/).
   - Crie um projeto e ative a **Google Calendar API**.
   - Crie uma tela de permissão OAuth e crie uma credencial do tipo **ID do cliente OAuth (Aplicativo para Desktop)**.
   - Faça o download do arquivo JSON e renomeie-o para `credentials.json` na raiz deste projeto.

3. **Obter Chave do Gemini API**:
   - Obtenha uma chave no [Google AI Studio](https://aistudio.google.com/).

4. **Configurar Variáveis Localmente (`.streamlit/secrets.toml`)**:
   Crie ou edite o arquivo `.streamlit/secrets.toml` com a estrutura abaixo:
   ```toml
   GEMINI_API_KEY = "SUA_API_KEY_AQUI"
   CALENDAR_ID = "ID_DA_SUA_AGENDA_OU_GRUPO_GOOGLE@group.calendar.google.com"

   [GOOGLE_CREDENTIALS]
   # Se rodar em nuvem (Streamlit Cloud), insira o conteúdo do credentials.json estruturado como TOML:
   # Exemplo:
   # [GOOGLE_CREDENTIALS.installed]
   # client_id = "..."
   # project_id = "..."
   # auth_uri = "https://accounts.google.com/o/oauth2/auth"
   # ...
   ```

---

## 🚀 Como Executar

Para iniciar a aplicação localmente:
```bash
streamlit run app.py
```
Isso abrirá automaticamente a interface em seu navegador (geralmente em `http://localhost:8501`).

Na primeira execução, o app solicitará autenticação Google no navegador. Após conceder permissão para gerenciar os eventos de sua agenda, o arquivo `token.json` será gerado automaticamente na raiz do projeto e não precisará ser gerado novamente nas próximas execuções.

---

## 🌿 Padrão de Branchs e Commits (Git Guidelines)

Para manter o repositório organizado e profissional ao subir alterações para o GitHub/GitLab, siga os padrões a seguir:

### 1. Padrão de Nomenclatura de Branches
Dividimos o trabalho usando prefixos simples de acordo com o tipo de alteração que está sendo feita:

| Prefixo | Finalidade | Exemplo |
| :--- | :--- | :--- |
| `feat/` | Implementação de nova funcionalidade | `feat/dashboard-agenda` |
| `fix/` | Correção de algum bug ou erro | `fix/google-oauth-refresh` |
| `refactor/` | Reestruturação de código (sem alteração visual/funcional) | `refactor/modular-architecture` |
| `docs/` | Atualizações ou criações de documentação | `docs/readme-instructions` |
| `style/` | Ajustes visuais, CSS e layouts que não mudam a lógica | `style/premium-css` |

**Exemplo de fluxo para criar uma branch:**
```bash
# Baixar alterações mais recentes da branch principal
git checkout main
git pull

# Criar e acessar a nova branch para desenvolvimento
git checkout -b feat/dashboard-agenda
```

### 2. Padrão de Mensagens de Commit (Conventional Commits)
Suas mensagens de commit devem descrever claramente **o que** foi feito de maneira concisa e estruturada. O padrão básico é:
`tipo(escopo): descrição curta em português`

#### Tipos Permitidos:
- **`feat`**: Uma nova funcionalidade (ex: adição do feed de eventos futuros).
- **`fix`**: Correção de bug (ex: conserto no fuso horário do Google Calendar).
- **`refactor`**: Alteração de código que não corrige bug nem adiciona funcionalidade (ex: dividir app.py em módulos).
- **`docs`**: Alterações apenas na documentação (ex: adição do README).
- **`style`**: Mudanças de estilo que não afetam a lógica (ex: ajuste do gradiente de cor no título).
- **`chore`**: Atualizações de tarefas de build, pacotes ou ferramentas (ex: atualizar requirements.txt).

#### Exemplos Práticos de Commit:
```bash
# Para a criação dos serviços separados
git commit -m "refactor(arch): separa lógica em módulos de serviços (config, ai e calendar)"

# Para a melhoria visual do Streamlit
git commit -m "feat(ui): implementa aba de próximos eventos e cards com visual premium"

# Para a criação da documentação
git commit -m "docs(readme): cria documentação do agente e define guias de git"
```

### 3. Checklist antes de Enviar ao Repositório (Push)
1. Certifique-se de que não há código comentado desnecessário ou `print()` temporário de debug.
2. Certifique-se de que o arquivo `token.json` e as chaves de API **não** estão sendo versionados (eles devem estar inclusos no seu `.gitignore`).
3. Faça o commit seguindo o padrão.
4. Faça o push para a branch remota:
   ```bash
   git push origin feat/dashboard-agenda
   ```
5. Abra o Pull Request (PR) contra a branch `main`.
