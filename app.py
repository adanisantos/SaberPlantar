import streamlit as st
import google.generativeai as genai
import os

# Inicializa o modelo Gemini e armazena-o em st.session_state para persistência
# Esta é a parte crucial para o erro que você está a ver.
if "gemini_model" not in st.session_state:
    st.session_state["gemini_model"] = genai.GenerativeModel('gemini-2.0-flash') # Modelo de visão para sugestões de vasos

   # --- Configuração da Página Streamlit (DEVE SER A PRIMEIRA CHAMADA DO ST) ---
st.set_page_config(page_title="Chatbot de Plantas", page_icon="🌿", layout="centered")

# --- Configuração da API Gemini ---
# A chave da API é lida da variável de ambiente GOOGLE_API_KEY.
# No Streamlit Community Cloud, esta variável é definida nas configurações de "Secrets".
api_key = os.environ.get('GOOGLE_API_KEY')

# Verifica se a chave da API foi definida. Se não, exibe um erro e para a execução.
if not api_key:
    st.error("Erro: Chave da API do Gemini não encontrada.")
    st.markdown("""
        Por favor, defina a variável de ambiente `GOOGLE_API_KEY`.
        - **No Streamlit Community Cloud:** Adicione `GOOGLE_API_KEY` como um "Secret" nas configurações do seu aplicativo.
        - **Localmente:** No seu terminal, antes de rodar o app: `export GOOGLE_API_KEY='SUA_CHAVE_AQUI'` (Linux/macOS) ou `$env:GOOGLE_API_KEY='SUA_CHAVE_AQUI'` (PowerShell no Windows).
    """)
    st.stop() # Para a execução do Streamlit se a chave não estiver definida

# Configura a API Gemini com a chave obtida.
genai.configure(api_key=api_key)

# --- Inicialização dos Modelos Gemini em st.session_state ---
# Esta é a parte CRUCIAL para o erro que você estava vendo.
# O modelo é inicializado APENAS UMA VEZ por sessão do usuário e armazenado em st.session_state.
# Isso garante que ele esteja sempre disponível em todas as re-execuções do script.
if "gemini_text_model" not in st.session_state:
    st.session_state["gemini_text_model"] = genai.GenerativeModel('gemini-2.0-flash')

def obter_informacao_planta(nome_planta):
    try:
        # Acessa os modelos a partir de st.session_state para garantir que estão inicializados.
        text_model = st.session_state["gemini_text_model"]

        # PROMPT AJUSTADO para incentivar uma resposta mais fluida e menos templated.
        # Use f-strings para inserir o nome_planta diretamente no prompt.
        text_prompt = [
            f"Forneça informações detalhadas e amigáveis sobre os cuidados da planta ou flor chamada '{nome_planta}', como se estivesse a explicar a um iniciante. Inclua informações sobre luz, rega, solo e humidade, se aplicável. Além disso, sugira 3 tipos de vasos que seriam adequados para essa planta, descrevendo brevemente cada um e, se possível, mencionando características que os tornem adequados (ex: material, drenagem)."
        ]
        
        # Gera a resposta do Gemini.
        # Use o método `generate_content` que aceita uma lista de partes (texto ou imagem).
        text_api_response = text_model.generate_content(contents=text_prompt)
        
        # Acessa o texto da resposta.
        return text_api_response.text

    except Exception as e:
        # Retorna a mensagem de erro formatada, incluindo o erro real capturado.
        return f"Desculpe, ocorreu um erro ao buscar informações sobre '{nome_planta}': {e}"

## Interface Principal do Chatbot com Streamlit

st.title("🌿 Chatbot de Plantas com Gemini")
st.markdown("Pergunte-me sobre cuidados com plantas e sugestões de vasos!")

# Inicializa o histórico de mensagens na sessão do Streamlit.
# Cada mensagem agora conterá apenas 'role' e 'content'.
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Olá! Pergunte-me sobre plantas ou flores!"}]

# Exibe as mensagens do histórico na interface do chatbot.
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# Caixa de entrada para o usuário digitar sua pergunta.
if prompt := st.chat_input("Digite o nome de uma planta ou flor..."):
    # Adiciona a pergunta do usuário ao histórico e exibe.
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Obtém a resposta do Gemini (apenas texto) usando a função.
    with st.spinner("Buscando informações..."): # Mostra um indicador de carregamento
        resposta_texto = obter_informacao_planta(prompt) # A função agora retorna apenas um valor

    # Adiciona a resposta de texto do assistente ao histórico e exibe.
    st.session_state["messages"].append({"role": "assistant", "content": resposta_texto})
    st.chat_message("assistant").write(resposta_texto)
