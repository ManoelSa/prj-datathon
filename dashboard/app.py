import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv
from scipy.stats import ks_2samp

from dotenv import find_dotenv
load_dotenv(find_dotenv())

# Configuração da Página
st.set_page_config(
    page_title="SAPE",
    page_icon="🎓",
    layout="wide"
)

# Constantes
API_URL = os.getenv("API_URL", "http://localhost:8000" )

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

st.sidebar.title("Navegação")
page = st.sidebar.radio("Ir para", ["Predição Individual", "Monitoramento de Drift", "Performance do Sistema"])

st.title("🎓 SAPE - Sistema de Alerta Preventivo Escolar")
st.markdown("---")

# Gerenciamento de Sessão
if "token" not in st.session_state:
    st.session_state.token = None

# Barra Lateral - Login e Status
with st.sidebar:
    st.markdown("---")
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

    # Configuração de Sensibilidade
    st.markdown("---")
    st.header("Configurações do Modelo")
    threshold = st.slider(
        "Sensibilidade de Risco (Threshold)", 
        min_value=0.0, 
        max_value=1.0, 
        value=0.5, 
        step=0.05,
        help="Ajuste o limiar de decisão. Valores menores tornam o modelo mais sensível (mais alertas). Valores maiores tornam o modelo mais conservador."
    )

# --- Página: Predição Individual ---
if page == "Predição Individual":
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
            
            st.markdown("#### Dados de Fase e Idade")
            c_idade, c_fase = st.columns(2)
            
            with c_idade:
                idade = st.number_input("Idade do Aluno", min_value=6, max_value=50, value=14, step=1)
                
            with c_fase:
                fase_opcoes = {
                    0: "Alfa (1º e 2º ano)",
                    1: "Fase 1 (3º e 4º ano)",
                    2: "Fase 2 (5º e 6º ano)",
                    3: "Fase 3 (7º e 8º ano)",
                    4: "Fase 4 (9º ano)",
                    5: "Fase 5 (1º EM)",
                    6: "Fase 6 (2º EM)",
                    7: "Fase 7 (3º EM)",
                    8: "Fase 8 (Universitário)"
                }
                # User seleciona o texto, mas o valor é a chave (int)
                fase_label = st.selectbox("Fase Atual", options=list(fase_opcoes.values()), index=4)
                # Reverse lookup para pegar o ID da fase (0-8)
                fase_real = next(k for k, v in fase_opcoes.items() if v == fase_label)

            # Lógica de Cálculo (Espelho do Backend)
            AGE_FASE_MAP = {
                6: 0, 7: 0, 8: 0, 9: 1, 10: 2, 11: 2, 12: 3, 13: 3, 14: 4, 
                15: 5, 16: 6, 17: 7, 18: 8, 19: 8, 20: 8, 21: 8, 22: 8, 23: 8, 24: 8
            }
            
            target_ideal = AGE_FASE_MAP.get(idade, 8 if idade > 18 else 0)
            defasagem_calc = fase_real - target_ideal
            
            # Feedback visual do cálculo
            if defasagem_calc < 0:
                st.warning(f"⚠️ Defasagem Calculada: {defasagem_calc} (Atraso de {-defasagem_calc} fases)")
            elif defasagem_calc > 0:
                st.info(f"🚀 Defasagem Calculada: {defasagem_calc} (Adiantado em {defasagem_calc} fases)")
            else:
                st.success(f"✅ Defasagem Calculada: {defasagem_calc} (Em dia com a idade)")

        st.markdown("---")
        
        if st.button("Analisar Risco", type="primary"):
            input_data = {
                "IAA": iaa, "IEG": ieg, "IPS": ips,
                "IDA": ida, "IPP": ipp, "IPV": ipv,
                "IAN": ian, "INDE": inde, "Defasagem": float(defasagem_calc),
                "threshold": threshold
            }
            
            with st.spinner("Processando..."):
                result = predict(st.session_state.token, input_data)
                
            if result:
                prediction = result.get("prediction")
                probability = result.get("probability", 0.0)
                status = result.get("status")
                
                st.markdown("### Resultado da Análise")
                
                # Layout de colunas para métricas (Texto/Print na Tela)
                col_metric1, col_metric2, col_metric3 = st.columns(3)

                with col_metric1:
                    # Mostra a probabilidade real
                    st.metric(
                        label="Probabilidade Calculada", 
                        value=f"{probability:.1%}"
                    )
                
                with col_metric2:
                    # Mostra o critério usado pelo usuário
                    st.metric(
                        label="Seu Limite (Threshold)", 
                        value=f"{threshold:.1%}"
                    )

                with col_metric3:
                    # Mostra a diferença (Delta) para explicar a decisão
                    delta = probability - threshold
                    st.metric(
                        label="Margem de Decisão", 
                        value=f"{delta:.1%}",
                        delta_color="inverse" # Vermelho se positivo (acima do limite), Verde se negativo
                    )

                st.markdown("---")
                if status == "Alto Risco":
                    st.error(f"⚠️ **ALTO RISCO CONFIRMADO**")
                    st.write(f"A probabilidade ({probability:.1%}) está **ACIMA** do limite de sensibilidade que você definiu ({threshold:.1%}).")
                    st.warning("👉 Recomendação: Iniciar protocolo de intervenção pedagógica imediata.")
                else:
                    st.success(f"✅ **BAIXO RISCO (MONITORADO)**")
                    st.write(f"A probabilidade ({probability:.1%}) está **ABAIXO** do limite de sensibilidade que você definiu ({threshold:.1%}).")
                    st.info("👉 Recomendação: Manter acompanhamento regular.")
                
                # Detalhes técnicos (expander)
                with st.expander("Detalhes Técnicos (JSON)"):
                    st.json(result)

    else:
        st.info("👈 Por favor, faça login na barra lateral para acessar o sistema.")
        st.markdown("""
        ### Sobre o SAPE
        O **SAPE** (Sistema de Alerta Preventivo Escolar) utiliza **Inteligência Artificial** para identificar precocemente o risco de evasão escolar.

        Através da análise de dados **socioemocionais e acadêmicos**, a ferramenta apoia a gestão na tomada de decisão pedagógica assertiva.

        **Conecte-se para começar.**
        """)

# --- Página: Monitoramento de Drift ---
elif page == "Monitoramento de Drift":
    st.header("📉 Monitoramento de Data Drift")
    st.markdown("Comparação entre a distribuição dos dados de **Treino (Referência)** e os dados **Atuais (Produção)**.")

    # 1. Carregar Reference Data (Estático, do pacote)
    try:
        DATA_PATH = "data/reference_data.csv"
        if os.path.exists(DATA_PATH):
            df_ref = pd.read_csv(DATA_PATH)
        else:
            st.error(f"Arquivo de referência '{DATA_PATH}' não encontrado. Execute o script de extração primeiro.")
            st.stop()
            
    except Exception as e:
        st.error(f"Erro ao carregar dados de referência: {e}")
        st.stop()
        
    # 2. Carregar Production Data (Dinâmico, da API)
    if st.session_state.token:
        # Opção para o usuário controlar o volume de dados
        limit_options = {100: "Últimos 100", 500: "Últimos 500", 1000: "Últimos 1000", 0: "Todos (Sem Limite)"}
        selected_limit = st.selectbox(
            "Selecione o volume de dados para análise:", 
            options=list(limit_options.keys()), 
            format_func=lambda x: limit_options[x],
            index=2 # Default: 1000
        )
        
        try:
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            # Passa o limit como query param
            response = requests.get(f"{API_URL}/history", headers=headers, params={"limit": selected_limit}, timeout=10)
            
            if response.status_code == 200:
                history_data = response.json()
                if history_data:
                    df_curr = pd.DataFrame(history_data)
                    st.success(f"Carregados {len(df_curr)} registros de produção.")
                else:
                    st.warning("Ainda não há dados de produção suficientes (histórico vazio).")
                    df_curr = pd.DataFrame()
            else:
                st.error(f"Erro ao buscar histórico da API: {response.text}")
                df_curr = pd.DataFrame()
                
        except Exception as e:
            st.error(f"Erro de conexão ao buscar histórico: {e}")
            df_curr = pd.DataFrame()
    else:
        st.info("⚠️ Faça login para visualizar os dados de produção.")
        df_curr = pd.DataFrame()

    # 3. Análise de Drift (Se houver dados)
    if not df_curr.empty:
        # Garante que as colunas existem
        valid_cols = [c for c in df_ref.columns if c in df_curr.columns]
        
        if not valid_cols:
            st.error("As colunas do histórico não correspondem aos dados de referência.")
        else:
            feature = st.selectbox("Selecione o Indicador para Análise", valid_cols)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"### Distribuição: {feature}")
                
                # Prepara dados para o gráfico, tratando None/NaN misturado com números.
                ref_series = pd.to_numeric(df_ref[feature], errors='coerce').dropna().reset_index(drop=True)
                curr_series = pd.to_numeric(df_curr[feature], errors='coerce').dropna().reset_index(drop=True)
                
                # Só plota se tiver dados válidos e comparáveis
                if not ref_series.empty and not curr_series.empty:
                    # Alinha os indexes para o gráfico não quebrar
                    min_len = min(len(ref_series), len(curr_series))
                    if min_len > 0:
                        chart_data = pd.DataFrame({
                            "Referência (Treino)": ref_series.iloc[:min_len],
                            "Atual (Produção)": curr_series.iloc[:min_len]
                        })
                        st.line_chart(chart_data)
                    else:
                        st.warning("Dados insuficientes para plotar comparação.")
                else:
                    st.warning(f"A coluna '{feature}' contém apenas valores nulos ou inválidos.")
                
            with col2:
                st.write("### Estatísticas Descritivas")
                st.write("**Referência**")
                st.write(df_ref[feature].describe())
                st.write("**Atual**")
                st.write(df_curr[feature].describe())
                
            # Alerta de Drift via Teste KS (Kolmogorov-Smirnov)           
            # Remove nulos e converte para numérico se necessário
            sample_ref = pd.to_numeric(df_ref[feature], errors='coerce').dropna()
            sample_curr = pd.to_numeric(df_curr[feature], errors='coerce').dropna()
            
            if len(sample_curr) < 5:
                st.warning("Amostra de produção muito pequena para teste estatístico confiável.")
            else:
                ks_statistic, p_value = ks_2samp(sample_ref, sample_curr)
                
                st.markdown("### Análise Estatística de Drift (Teste KS)")
                st.write(f"**Estatística KS**: {ks_statistic:.4f}")
                st.write(f"**P-valor**: {p_value:.4f}")
                
                # Interpretação
                if p_value < 0.05:
                    st.error(f"🚨 **Drift Detectado!** (p-valor < 0.05)")
                    st.markdown("""
                    A distribuição dos dados atuais difere significativamente dos dados de treino.
                    **Ação Recomendada**: O modelo pode estar desatualizado. Re-treinar urgentemente.
                    """)
                else:
                    st.success(f"✅ **Distribuição Estável** (p-valor >= 0.05)")
                    st.info("Não há evidência estatística suficiente para afirmar que os dados mudaram.")

# --- Página: Performance do Sistema ---
elif page == "Performance do Sistema":
    st.header("🚀 Performance do Sistema")
    st.markdown("Monitoramento de latência e volume de requisições da API.")

    if st.session_state.token:
        try:
            # Busca todo o histórico para análise de performance
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            with st.spinner("Carregando logs de performance..."):
                response = requests.get(f"{API_URL}/history", headers=headers, params={"limit": 0}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    df = pd.DataFrame(data)
                    
                    # Garante tipos corretos
                    if "timestamp" in df.columns:
                        df["timestamp"] = pd.to_datetime(df["timestamp"])
                    if "latency_ms" not in df.columns:
                        st.warning("⚠️ Dados de latência não encontrados nos logs antigos. Novos registros aparecerão aqui.")
                        df["latency_ms"] = 0.0 # Fallback para não quebrar
                    
                    # KPIs Principais
                    total_req = len(df)
                    avg_latency = df["latency_ms"].mean() if not df.empty else 0
                    p95_latency = df["latency_ms"].quantile(0.95) if not df.empty else 0
                    std_latency = df["latency_ms"].std() if not df.empty and len(df) > 1 else 0

                    
                    # Layout de Métricas
                    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                    kpi1.metric("Total de Requisições", total_req)
                    kpi2.metric("Latência Média", f"{avg_latency:.2f} ms")
                    kpi3.metric("Desvio Padrão", f"{std_latency:.2f} ms")
                    kpi4.metric("Latência P95", f"{p95_latency:.2f} ms", help="95% das requisições são mais rápidas que isso.")
                    
                    st.markdown("---")
                    
                    # Gráficos de Série Temporal
                    chart_col1, chart_col2 = st.columns(2)
                    
                    with chart_col1:
                        st.subheader("⏱️ Latência por Requisição")
                        if not df.empty and "latency_ms" in df.columns:
                            st.line_chart(df.set_index("timestamp")["latency_ms"])
                        else:
                            st.info("Sem dados para plotar.")

                    with chart_col2:
                        st.subheader("📊 Volume (Requisições/Minuto)")
                        if not df.empty and "timestamp" in df.columns:
                            # Resample para contar registros por minuto
                            df_throughput = df.set_index("timestamp").resample("min").size()
                            st.bar_chart(df_throughput)
                        else:
                            st.info("Sem dados para plotar.")
                            
                    # Tabela de Dados Recentes
                    with st.expander("Ver Logs Recentes"):
                        st.dataframe(df.head(50))
                else:
                    st.info("Nenhum log de performance encontrado.")
            else:
                st.error(f"Erro ao buscar logs: {response.text}")
                
        except Exception as e:
            st.error(f"Erro ao processar dados de performance: {e}")
    else:
         st.info("⚠️ Faça login para visualizar o monitoramento.")