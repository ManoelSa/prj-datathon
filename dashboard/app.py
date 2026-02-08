import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente (busca recursivamente)
# Atualizado para funcionar dentro da pasta dashboard/
from dotenv import find_dotenv
load_dotenv(find_dotenv())

# Configuração da Página
st.set_page_config(
    page_title="Predição de Risco Acadêmico",
    page_icon="🎓",
    layout="wide"
)

# Constantes
API_URL = os.getenv("API_URL", "https://api-modelo-risco.onrender.com") #http://localhost:8000

# --- Funções Auxiliares ---

def login(username, password):
    """Realiza login na API e retorna o token de acesso."""
    try:
        response = requests.post(
            f"{API_URL}/token",
            data={"username": username, "password": password},
            timeout=5
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            return None
    except requests.RequestException:
        st.error("Erro de conexão com a API.")
        return None

def predict(token, input_data):
    """Envia os dados para a API e retorna a predição."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(
            f"{API_URL}/predict",
            json=input_data,
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.error("Sessão expirada. Faça login novamente.")
            return None
        else:
            st.error(f"Erro na predição: {response.text}")
            return None
    except requests.RequestException as e:
        st.error(f"Erro na requisição: {e}")
        return None

# --- Interface do Usuário ---

st.title("🎓 Sistema de Alerta Preventivo")
st.markdown("---")

# Gerenciamento de Sessão
if "token" not in st.session_state:
    st.session_state.token = None

# Barra Lateral - Login e Status
with st.sidebar:
    st.header("Autenticação")
    
    if st.session_state.token is None:
        with st.form("login_form"):
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            submitted = st.form_submit_button("Entrar")
            
            if submitted:
                token = login(username, password)
                if token:
                    st.session_state.token = token
                    st.success("Login realizado com sucesso!")
                    st.rerun()
                else:
                    st.error("Credenciais inválidas ou erro na API.")
    else:
        st.success("Conectado")
        if st.button("Sair"):
            st.session_state.token = None
            st.rerun()

# Conteúdo Principal
if st.session_state.token:
    st.subheader("Dados do Aluno")
    
    col1, col2 = st.columns(2)
    
    with col1:
        iaa = st.slider("IAA - Autoavaliação da Aprendizagem", 0.0, 10.0, 5.0, 0.1)
        ieg = st.slider("IEG - Engajamento Geral", 0.0, 10.0, 5.0, 0.1)
        ips = st.slider("IPS - Índice Psicossocial", 0.0, 10.0, 5.0, 0.1)
        ida = st.slider("IDA - Dificuldade de Aprendizagem", 0.0, 10.0, 5.0, 0.1)
        ipp = st.slider("IPP - Prática Pedagógica", 0.0, 10.0, 5.0, 0.1)

    with col2:
        ipv = st.slider("IPV - Ponto de Virada", 0.0, 10.0, 5.0, 0.1)
        ian = st.slider("IAN - Adequação de Nível", 0.0, 10.0, 5.0, 0.1)
        inde = st.slider("INDE - Desenvolvimento Educacional", 0.0, 10.0, 5.0, 0.1)
        defasagem = st.number_input("Nível de Defasagem", 0.0, 5.0, 0.0, 1.0)

    st.markdown("---")
    
    if st.button("Analisar Risco", type="primary"):
        input_data = {
            "IAA": iaa, "IEG": ieg, "IPS": ips,
            "IDA": ida, "IPP": ipp, "IPV": ipv,
            "IAN": ian, "INDE": inde, "Defasagem": defasagem
        }
        
        with st.spinner("Processando..."):
            result = predict(st.session_state.token, input_data)
            
        if result:
            prediction = result.get("prediction")
            probability = result.get("probability", 0.0)
            
            st.markdown("### Resultado da Análise")
            
            if prediction == 1:
                st.error(f"⚠️ **Alto Risco de Evasão** (Probabilidade: {probability:.1%})")
                st.warning("Recomendação: Iniciar protocolo de intervenção pedagógica imediata.")
            else:
                st.success(f"✅ **Baixo Risco** (Probabilidade: {probability:.1%})")
                st.info("Recomendação: Manter acompanhamento regular.")
            
            # Detalhes técnicos (expander)
            with st.expander("Detalhes Técnicos"):
                st.json(result)

else:
    st.info("👈 Por favor, faça login na barra lateral para acessar o sistema.")
    st.markdown("""
    ### Sobre o Sistema
    Este dashboard utiliza um modelo de Machine Learning para predizer o risco de evasão escolar com base em indicadores educacionais.
    
    **Conecte-se para começar.**
    """)
