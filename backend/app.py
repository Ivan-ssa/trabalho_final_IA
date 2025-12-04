# /backend/app.py
# Servidor Flask que orquestra RAG (PDF), BI (CSV) e Roteamento (Gemini)

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS 
from dotenv import load_dotenv
import os
import pandas as pd
import json

# Importações da IA (LangChain, Pydantic, Chroma)
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader 
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from pydantic import BaseModel, Field

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

app = Flask(__name__)
CORS(app) 

# --- VARIÁVEIS GLOBAIS DE CONFIGURAÇÃO ---
PDF_FILENAME = "./data/Manual Técnico de Dados - SBlock.pdf" 
VECTOR_DB_PATH = "./sblock_db"
LLM_MODEL = "gemini-1.5-flash" # Ajustado para um modelo estavel, se o 2.5 falhar use este.

# Variáveis globais para os componentes de IA/Dados
METRICAS_SBLOCK = {}
DB_SBLOCK = None
LLM_RAG = None
LLM_ROTEADOR = None
LLM_COM_SCHEMA = None
EMBEDDINGS = None

# DEFINIÇÃO DO SYSTEM PROMPT (A CARA DO AGENTE) 
SBLOCK_PERSONA = """
Você é 'Agente SBlock', o assistente virtual 24/7 de Seguros Digitais.

Sua Missão:
1. Foco Total: Apenas interaja com o usuário em temas relacionados a seguros, cotações, sinistros, regras de negócio e dados internos da SBlock.
2. Personalidade: Seu tom é profissional, moderno, **simples, transparente e ágil**. Use formatação Markdown (negrito, listas) para clareza e seja objetivo.
3. Regras de Ouro:
    - Se a intenção for 'SAUDACAO', responda de forma amigável e pergunte como pode ajudar.
    - Se a intenção for 'FAQ', use estritamente a Base de Conhecimento (RAG).
    - Se a informação não estiver na base ou não for relevante ao negócio (ex: 'conte uma piada'), diga de forma transparente que sua função se restringe a suporte da SBlock.
"""


# --- MÓDULO DE DADOS (BI) - LÊ TODOS OS CSVs ---
def carregar_e_calcular_metricas_bi():
    apolices_path = "./data/sblock_apolices.csv"
    sinistros_path = "./data/sblock_sinistros.csv"
    segurados_path = "./data/sblock_segurados.csv"
    vendas_path = "./data/sblock_vendas.csv" 
    
    print("Iniciando Módulo BI (Carregamento de Dados)...")

    try:
        # Lendo os CSVs (sep=;, decimal=,)
        apolices = pd.read_csv(apolices_path, sep=';', decimal=',')
        sinistros = pd.read_csv(sinistros_path, sep=';', decimal=',')
        segurados = pd.read_csv(segurados_path, sep=';', decimal=',')
        vendas = pd.read_csv(vendas_path, sep=';', decimal=',') 
        
        # --- PROCESSAMENTO ---
        apolices = apolices.sort_values(by='data', ascending=False)
        sinistros = sinistros.sort_values(by='data', ascending=False)
        vendas = vendas.sort_values(by='data', ascending=False)

        # 🚨 EXTRAÇÃO ADICIONAL: Valor Médio de Sinistro (para responder a "quanto paga?")
        valor_medio_sinistro_vida = sinistros['valor_medio_sinistro_vida'].iloc[0]
        valor_medio_sinistro_auto = sinistros['valor_medio_sinistro_auto'].iloc[0]

        score_risco_por_segmento = segurados.groupby(['estado', 'tipo_seguro'])['score_risco'].mean().to_dict()

        metricas = {
            "ultima_data_bi": apolices['data'].iloc[0],
            "premio_medio_vida": apolices['premio_medio_vida'].iloc[0],
            "premio_medio_auto": apolices['premio_medio_auto'].iloc[0],
            "tempo_medio_vida": sinistros['tempo_medio_resolucao_vida_dias'].iloc[0],
            "tempo_medio_auto": sinistros['tempo_medio_resolucao_auto_dias'].iloc[0],
            "taxa_aprovacao_auto": sinistros['taxa_aprovacao_auto'].iloc[0],
            "desconto_multi": 0.15,
            "score_risco_por_segmento": score_risco_por_segmento,
            "conversao_site": vendas['conversao_site'].iloc[0],
            "cac_app": vendas['cac_app'].iloc[0],
            "valor_medio_sinistro_vida": valor_medio_sinistro_vida, # NOVO
            "valor_medio_sinistro_auto": valor_medio_sinistro_auto  # NOVO
        }
        print("✅ Módulo BI: Métricas carregadas e segmentação de risco pronta.")
        return metricas

    except Exception as e:
        print(f"❌ Erro ao carregar dados BI. Usando fallback. Erro: {e}")
        return {
            "ultima_data_bi": "Padrão", "premio_medio_vida": 85.00, "premio_medio_auto": 180.00, 
            "tempo_medio_vida": 15.0, "tempo_medio_auto": 8.0, "taxa_aprovacao_auto": 90.0, 
            "desconto_multi": 0.15, "score_risco_por_segmento": {},
            "conversao_site": 8.5, "cac_app": 50.0,
            "valor_medio_sinistro_vida": 35000.00, # Fallback
            "valor_medio_sinistro_auto": 7000.00   # Fallback
        }

# --- MÓDULO RAG ---
def criar_ou_carregar_base_de_conhecimento():
    """Cria ou carrega a base de vetores (embeddings) a partir do PDF REAL."""
    if not os.path.exists("./data"):
        os.makedirs("./data")
        
    if os.path.exists(VECTOR_DB_PATH):
        print("Base de Conhecimento RAG encontrada. Carregando...")
        return Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=EMBEDDINGS)

    if not os.path.exists(PDF_FILENAME):
         raise FileNotFoundError(f"Erro: Arquivo PDF nao encontrado em '{PDF_FILENAME}'. Certifique-se de que o arquivo original está na pasta /backend/data/")

    print("Base de Conhecimento RAG nao encontrada. Criando a partir do PDF...")

    loader = PyPDFLoader(PDF_FILENAME) 
    documents = loader.load() 

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)

    db = Chroma.from_documents(chunks, EMBEDDINGS, persist_directory=VECTOR_DB_PATH)
    print("✅ Base de Conhecimento RAG criada com sucesso. (Lendo PDF real)")
    return db

def responder_pergunta_rag(db, pergunta_usuario: str):
    """Usa o RAG para buscar contexto no PDF e gerar a resposta, e tenta responder sobre KPIs de vendas."""
    
    # --- LOGICA DE VERIFICACAO PARA KPIS DE VENDA/MARKETING (BI) ---
    pergunta_lower = pergunta_usuario.lower()
    
    if "conversao" in pergunta_lower and "site" in pergunta_lower:
        conversao = METRICAS_SBLOCK.get("conversao_site", "informacao nao encontrada")
        return f"Nossa taxa de conversão do site, baseada em nossos dados mais recentes, é de **{conversao:.2f}%**. O foco na simplicidade digital está funcionando!"

    if "cac" in pergunta_lower and "app" in pergunta_lower:
        cac = METRICAS_SBLOCK.get("cac_app", "informacao nao encontrada")
        return f"O Custo de Aquisição por Cliente (CAC) via App é de **R$ {cac:.2f}**. Esse valor reflete nossa agilidade e eficiência no marketing."


    # --- LOGICA PADRÃO RAG (Busca no PDF + Simplificação) ---
    retriever = db.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(pergunta_usuario) 
    
    contexto = "\n\n".join([doc.page_content for doc in docs])

    # CORREÇÃO DE ESTILO E TOM 
    prompt_template = f"""
    Voce é o Agente SBlock. Sua missão é reescrever a resposta.
    
    **INSTRUÇÕES DE ESTILO:**
    1. **Tom:** Use linguagem simples, direta e moderna, ideal para o público jovem.
    2. **Clareza:** Evite jargões técnicos excessivos (atuariais, de compliance).
    3. **Encerramento:** Reforce que esta é uma informação de **autoatendimento 24/7** no final da sua resposta.
    
    Responda a pergunta do usuario **APENAS** com base no contexto TÉCNICO fornecido.
    
    CONTEXTO TÉCNICO DA SBLOCK (A ser reescrito e simplificado):
    ---
    {contexto}
    ---
    PERGUNTA DO USUARIO: {pergunta_usuario}
    """
    response = LLM_RAG.invoke(prompt_template)
    return response.content

# --- MÓDULOS DE NEGÓCIO (BI) ---
def responder_saudacao():
    """Responde a saudações de forma amigável."""
    return "Olá! Sou o **Agente SBlock**, seu assistente virtual de seguros. Posso te ajudar com cotações, sinistros ou regras de negócio. Como posso te auxiliar hoje?"

def simular_cotacao(tipo_seguro: str, mensagem_usuario: str):
    """Módulo 2: Combina metricas de Prêmio Mensal e Valor Médio de Sinistro."""
    
    # 1. Dados de Cotação
    premio_base = METRICAS_SBLOCK["premio_medio_auto"] if tipo_seguro == 'COTACAO_AUTO' else METRICAS_SBLOCK["premio_medio_vida"]
    data_ref = METRICAS_SBLOCK["ultima_data_bi"]
    desconto_multi = METRICAS_SBLOCK["desconto_multi"]
    
    desconto = premio_base * desconto_multi
    premio_final = premio_base - desconto

    # 2. Dados de Sinistro
    valor_sinistro = METRICAS_SBLOCK["valor_medio_sinistro_auto"] if tipo_seguro == 'COTACAO_AUTO' else METRICAS_SBLOCK["valor_medio_sinistro_vida"]
    
    # 3. Formatação
    valor_sinistro_formatado = f"R$ {valor_sinistro:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    detalhe_risco = ""
    if METRICAS_SBLOCK["score_risco_por_segmento"]:
         detalhe_risco = "Oferecemos precificação dinâmica e moderna com base no seu perfil de risco."

    resposta = (
        f"E aí! Com base em nossos dados de **{data_ref}**, aqui estão as informações completas de custo e valor de sinistro:\n\n"
        f"💰 **CUSTO MENSAL (Prêmio Médio {tipo_seguro.replace('COTACAO_', '').upper()}):** R$ {premio_base:.2f}\n"
        f"🛡️ **VALOR MÉDIO HISTÓRICO DE SINISTRO (Payout):** {valor_sinistro_formatado}\n"
        f"     *(Lembrete: O valor final da sua cobertura é customizável e você escolhe na hora da contratação.)*\n\n"
        f"{detalhe_risco}\n"
        f"👉 Você garante **{int(desconto_multi * 100)}% de desconto** se contratar ambos (Vida e Auto), levando o valor para **R$ {premio_final:.2f}**."
    )
    return resposta

def iniciar_sinistro(tipo_sinistro: str, mensagem_usuario: str):
    """Módulo 3: Fornece instrucoes e expectativas de tempo baseadas em BI."""
    
    if tipo_sinistro == 'SINISTRO_AUTO':
        tempo_medio = METRICAS_SBLOCK["tempo_medio_auto"]
        taxa_aprovacao = METRICAS_SBLOCK["taxa_aprovacao_auto"]
        instrucoes = "Garantir segurança, registrar B.O., enviar fotos pelo app. A agilidade é 100% digital."
    else: 
        tempo_medio = METRICAS_SBLOCK["tempo_medio_vida"]
        taxa_aprovacao = 90.0
        instrucoes = "Coletar documentos de óbito/invalidez. Nossa equipe de vida dará o suporte total."

    # Adicionando valor médio do sinistro à resposta
    valor_sinistro = METRICAS_SBLOCK["valor_medio_sinistro_auto"] if tipo_sinistro == 'SINISTRO_AUTO' else METRICAS_SBLOCK["valor_medio_sinistro_vida"]
    valor_sinistro_formatado = f"R$ {valor_sinistro:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


    data_ref = METRICAS_SBLOCK["ultima_data_bi"]

    resposta = (
        f"🚨 **PRIORIDADE MÁXIMA:** Seu sinistro de {tipo_sinistro.replace('SINISTRO_', '').upper()} foi registrado.\n"
        f"**Valor Médio Histórico de Payout:** {valor_sinistro_formatado} (Dado de {data_ref}).\n"
        f"Instruções imediatas: **{instrucoes}**.\n"
        f"Nosso tempo médio de resolução é de **{tempo_medio:.1f} dias**, com uma taxa de aprovação de **{taxa_aprovacao:.1f}%**. Transparência total!"
    )
    return resposta

# Definição do Schema para Roteamento
class IntencaoDoUsuario(BaseModel):
    intencao: str = Field(
        ...,
        description="A intencao principal da mensagem do usuario. Escolha uma das seguintes: 'FAQ', 'COTACAO_AUTO', 'COTACAO_VIDA', 'SINISTRO_AUTO', 'SINISTRO_VIDA', 'SAUDACAO', 'NAO_CLASSIFICADA'. Use 'COTACAO_VIDA' ou 'COTACAO_AUTO' para perguntas como 'qual o valor?', 'quanto custa?', 'cotações' ou 'quero seguro de [tipo]'." 
    )

def rotear_mensagem(pergunta_usuario: str):
    """Classifica a intencao e direciona a chamada para o modulo correto."""
    
    try:
        # Classificacao do LLM 
        classificacao: IntencaoDoUsuario = LLM_COM_SCHEMA.invoke(pergunta_usuario)
        intencao = classificacao.intencao

        # LOGICA DE ROTEAMENTO
        if intencao == 'SAUDACAO': 
            resposta = responder_saudacao()
        elif intencao == 'FAQ':
            resposta = responder_pergunta_rag(DB_SBLOCK, pergunta_usuario)
        elif intencao in ['COTACAO_AUTO', 'COTACAO_VIDA']:
            resposta = simular_cotacao(intencao, pergunta_usuario)
        elif intencao in ['SINISTRO_AUTO', 'SINISTRO_VIDA']:
            resposta = iniciar_sinistro(intencao, pergunta_usuario)
        else:
            # Fallback: Tenta o RAG
            resposta = responder_pergunta_rag(DB_SBLOCK, pergunta_usuario)
            if "nao esta disponivel" in resposta:
                 # Resposta de fallback final, alinhada com a persona
                 resposta = "Desculpe, não consegui identificar sua intenção e a informação não está na nossa base técnica. Posso te ajudar com cotações, sinistros ou regras da SBlock."

        return resposta, intencao

    except Exception as e:
        print(f"❌ ERRO GRAVE no Roteamento/LLM: {e}")
        return f"Desculpe, ocorreu um erro interno ({type(e).__name__}). Verifique o log do servidor.", "ERRO_INTERNO"


# --- ROTAS DO FLASK (API E FRONTEND) ---

@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('../frontend', filename)


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    pergunta_usuario = data.get('mensagem', '')

    if not pergunta_usuario:
        return jsonify({"resposta": "Mensagem vazia."}), 400

    resposta, intencao = rotear_mensagem(pergunta_usuario)
    print(f"Intencao: {intencao} | Resposta: {resposta[:50]}...")
    
    return jsonify({"resposta": resposta})


# --- INICIALIZAÇÃO DO SERVIDOR ---
def inicializar_aplicacao():
    """Funcao para configurar todos os componentes de IA e Dados antes de iniciar o Flask."""
    global METRICAS_SBLOCK, DB_SBLOCK, EMBEDDINGS, LLM_RAG, LLM_ROTEADOR, LLM_COM_SCHEMA

    # 1. Carrega Metricas de BI
    METRICAS_SBLOCK = carregar_e_calcular_metricas_bi()

    if not API_KEY:
        raise ValueError("A chave GEMINI_API_KEY nao foi encontrada no arquivo .env.")

    EMBEDDINGS = GoogleGenerativeAIEmbeddings(model="text-embedding-004", google_api_key=API_KEY)
    
    # 2. INICIALIZAÇÃO DO LLM COM O SYSTEM PROMPT (PERSONA)
    # 💡 CORREÇÃO: Trocamos para um modelo mais estável se o 2.5 não estiver acessível
    LLM_ROTEADOR = ChatGoogleGenerativeAI(model=LLM_MODEL, google_api_key=API_KEY, system_instruction=SBLOCK_PERSONA)
    LLM_RAG = ChatGoogleGenerativeAI(model=LLM_MODEL, google_api_key=API_KEY, system_instruction=SBLOCK_PERSONA)
    
    # 3. Cria o Roteador Estruturado
    LLM_COM_SCHEMA = LLM_ROTEADOR.with_structured_output(IntencaoDoUsuario)

    # 4. Cria ou Carrega a Base de Dados RAG
    DB_SBLOCK = criar_ou_carregar_base_de_conhecimento()
    
    print("🤖 Servidor de Chatbot IA pronto para uso!")


# 🔥 CORREÇÃO CRÍTICA PARA O RENDER/GUNICORN 🔥
# O Gunicorn importa o arquivo e NÃO roda o bloco "if main".
# Por isso, precisamos chamar a inicialização aqui fora explicitamente.
try:
    print("🚀 Inicializando aplicação via Gunicorn/Render...")
    inicializar_aplicacao()
except Exception as e:
    print(f"⚠️ Erro na inicialização global: {e}")


if __name__ == '__main__':
    # Este bloco só roda se você der "python app.py" no PC.
    # No Render, ele é ignorado, mas como chamamos a função acima, tudo funciona!
    app.run(host='0.0.0.0', port=5000)