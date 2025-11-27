# /backend/app.py

from flask import Flask, request, jsonify, send_from_directory # send_from_directory para servir o HTML/CSS/JS
from flask_cors import CORS 
from dotenv import load_dotenv
import os
import pandas as pd
import json

# Importações da IA (LangChain, Pydantic, Chroma)
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter # <--- CORREÇÃO: Nome da classe
from pydantic import BaseModel, Field

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

app = Flask(__name__)
CORS(app) # Habilita CORS

# --- VARIÁVEIS GLOBAIS DE CONFIGURAÇÃO ---
PDF_FILENAME = "./data/Manual Técnico de Dados - SBlock.pdf"
VECTOR_DB_PATH = "./sblock_db"
LLM_MODEL = "gemini-2.5-flash"

# Variáveis globais para os componentes de IA/Dados
METRICAS_SBLOCK = {}
DB_SBLOCK = None
LLM_RAG = None
LLM_ROTEADOR = None
LLM_COM_SCHEMA = None
EMBEDDINGS = None


# --- MÓDULO DE DADOS (BI) ---
def carregar_e_calcular_metricas_bi():
    apolices_path = "./data/sblock_apolices.csv"
    sinistros_path = "./data/sblock_sinistros.csv"
    print("Iniciando Módulo BI...")

    try:
        # Lendo os CSVs (sep=;, decimal=,)
        apolices = pd.read_csv(apolices_path, sep=';', decimal=',')
        sinistros = pd.read_csv(sinistros_path, sep=';', decimal=',')
        
        # Extrai a métrica mais recente
        apolices = apolices.sort_values(by='data', ascending=False)
        sinistros = sinistros.sort_values(by='data', ascending=False)
        
        metricas = {
            "ultima_data_bi": apolices['data'].iloc[0],
            "premio_medio_vida": apolices['premio_medio_vida'].iloc[0],
            "premio_medio_auto": apolices['premio_medio_auto'].iloc[0],
            "tempo_medio_vida": sinistros['tempo_medio_resolucao_vida_dias'].iloc[0],
            "tempo_medio_auto": sinistros['tempo_medio_resolucao_auto_dias'].iloc[0],
            "taxa_aprovacao_auto": sinistros['taxa_aprovacao_auto'].iloc[0],
            "desconto_multi": 0.15 
        }
        print("✅ Módulo BI: Métricas carregadas.")
        return metricas

    except Exception as e:
        print(f"❌ Erro ao carregar dados BI. Usando fallback. Erro: {e}")
        # Fallback de segurança (valores do manual)
        return {
            "ultima_data_bi": "Padrão",
            "premio_medio_vida": 85.00,
            "premio_medio_auto": 180.00,
            "tempo_medio_vida": 15.0,
            "tempo_medio_auto": 8.0,
            "taxa_aprovacao_auto": 90.0,
            "desconto_multi": 0.15 
        }

# --- MÓDULO RAG ---
def criar_ou_carregar_base_de_conhecimento():
    """Cria ou carrega a base de vetores (embeddings) a partir do PDF."""
    if not os.path.exists("./data"):
        os.makedirs("./data")
        
    # Lógica para criar arquivo dummy se necessário (para garantir o RAG)
    if not os.path.exists(PDF_FILENAME):
        conteudo_manual = """
        # Manual Técnico de Dados - SBlock
        A SBlock é uma insurtech brasileira...
        ### Regras de Negócio e Produtos:
        * **Desconto Multi-produto:** 15% de desconto para quem contrata Vida e Auto.
        * **Tempo Médio de Cotação:** 2 minutos.
        ### Processo de Sinistro:
        * **Instruções Sinistro Auto:** Garantir segurança, registrar B.O., enviar fotos pelo app.
        """
        with open(PDF_FILENAME, "w") as f:
            f.write(conteudo_manual)
        print("Arquivo Manual Técnico dummy criado para inicialização.")
        
    if os.path.exists(VECTOR_DB_PATH):
        print("Base de Conhecimento RAG encontrada. Carregando...")
        return Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=EMBEDDINGS)

    print("Base de Conhecimento RAG não encontrada. Criando...")
    loader = TextLoader(PDF_FILENAME) 
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)

    db = Chroma.from_documents(chunks, EMBEDDINGS, persist_directory=VECTOR_DB_PATH)
    print("✅ Base de Conhecimento RAG criada com sucesso.")
    return db

def responder_pergunta_rag(db, pergunta_usuario: str):
    """Usa o RAG para buscar contexto no PDF e gerar a resposta."""
    retriever = db.as_retriever(search_kwargs={"k": 3})
    
    # Usando .invoke()
    docs = retriever.invoke(pergunta_usuario) 
    
    contexto = "\n\n".join([doc.page_content for doc in docs])

    prompt_template = f"""
    Você é um atendente 24/7 da SBlock. Responda à pergunta do usuário **APENAS** com base no contexto interno da SBlock fornecido.
    Se a resposta não estiver no contexto, diga gentilmente que essa informação não está disponível na base de conhecimento.

    CONTEXTO DA SBLOCK:
    ---
    {contexto}
    ---
    PERGUNTA DO USUÁRIO: {pergunta_usuario}
    """
    response = LLM_RAG.invoke(prompt_template)
    return response.content

# --- MÓDULOS DE NEGÓCIO (BI) ---
def simular_cotacao(tipo_seguro: str, mensagem_usuario: str):
    """Módulo 2: Usa métricas de BI para simular cotação."""
    premio_base = METRICAS_SBLOCK["premio_medio_auto"] if tipo_seguro == 'COTACAO_AUTO' else METRICAS_SBLOCK["premio_medio_vida"]
    data_ref = METRICAS_SBLOCK["ultima_data_bi"]
    desconto_multi = METRICAS_SBLOCK["desconto_multi"]
    
    desconto = premio_base * desconto_multi
    premio_final = premio_base - desconto

    resposta = (
        f"Obrigado! Com base em nossos dados de **{data_ref}**, o prêmio médio mensal para um "
        f"**{tipo_seguro.replace('COTACAO_', '').upper()}** é de **R$ {premio_base:.2f}**.\n"
        f"👉 Lembre-se: Você tem direito a **{int(desconto_multi * 100)}% de desconto** (economizando R$ {desconto:.2f}) se contratar ambos (Vida e Auto), "
        f"levando o valor para **R$ {premio_final:.2f}**."
    )
    return resposta

def iniciar_sinistro(tipo_sinistro: str, mensagem_usuario: str):
    """Módulo 3: Fornece instruções e expectativas de tempo baseadas em BI."""
    
    if tipo_sinistro == 'SINISTRO_AUTO':
        tempo_medio = METRICAS_SBLOCK["tempo_medio_auto"]
        taxa_aprovacao = METRICAS_SBLOCK["taxa_aprovacao_auto"]
        instrucoes = "Garantir segurança, registrar B.O., enviar fotos pelo app."
    else: 
        tempo_medio = METRICAS_SBLOCK["tempo_medio_vida"]
        taxa_aprovacao = 90.0
        instrucoes = "Coletar documentos de óbito/invalidez."

    data_ref = METRICAS_SBLOCK["ultima_data_bi"]

    resposta = (
        f"🚨 **PRIORIDADE MÁXIMA:** Seu sinistro de {tipo_sinistro.replace('SINISTRO_', '').upper()} foi registrado. "
        f"Instruções imediatas: **{instrucoes}**.\n"
        f"Com base nos dados de {data_ref}, nosso tempo médio de resolução é de **{tempo_medio:.1f} dias**, com uma taxa de aprovação de **{taxa_aprovacao:.1f}%**."
    )
    return resposta

# Definição do Schema para Roteamento
class IntencaoDoUsuario(BaseModel):
    intencao: str = Field(
        ...,
        description="A intenção principal da mensagem do usuário. Escolha uma das seguintes: 'FAQ', 'COTACAO_AUTO', 'COTACAO_VIDA', 'SINISTRO_AUTO', 'SINISTRO_VIDA', 'NAO_CLASSIFICADA'."
    )

def rotear_mensagem(pergunta_usuario: str):
    """Classifica a intenção e direciona a chamada para o módulo correto."""
    
    try:
        # Classificação do LLM 
        classificacao: IntencaoDoUsuario = LLM_COM_SCHEMA.invoke(pergunta_usuario)
        intencao = classificacao.intencao

        # LÓGICA DE ROTEAMENTO
        if intencao == 'FAQ':
            resposta = responder_pergunta_rag(DB_SBLOCK, pergunta_usuario)
        elif intencao in ['COTACAO_AUTO', 'COTACAO_VIDA']:
            resposta = simular_cotacao(intencao, pergunta_usuario)
        elif intencao in ['SINISTRO_AUTO', 'SINISTRO_VIDA']:
            resposta = iniciar_sinistro(intencao, pergunta_usuario)
        else:
            # Fallback: Tenta o RAG
            resposta = responder_pergunta_rag(DB_SBLOCK, pergunta_usuario)
            if "não está disponível" in resposta:
                 resposta = "Desculpe, não entendi sua intenção e não encontrei a informação na base. Tente perguntar sobre cotação, sinistro ou regras da SBlock."

        return resposta, intencao

    except Exception as e:
        print(f"❌ ERRO GRAVE no Roteamento/LLM: {e}")
        return f"Desculpe, ocorreu um erro interno ({type(e).__name__}). Verifique o log do servidor.", "ERRO_INTERNO"


# --- ROTAS DO FLASK (API E FRONTEND) ---

# ROTA 1: Rota para servir o index.html (a página inicial do chat)
@app.route('/')
def serve_index():
    # O caminho para o index.html a partir de /backend/ é ../frontend
    return send_from_directory('../frontend', 'index.html')

# ROTA 2: Rota para servir arquivos estáticos (CSS e JS)
@app.route('/<path:filename>')
def serve_static(filename):
    # Serve arquivos como style.css e script.js
    return send_from_directory('../frontend', filename)


# ROTA 3: Rota da API do Chat (o motor da IA)
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    pergunta_usuario = data.get('mensagem', '')

    if not pergunta_usuario:
        return jsonify({"resposta": "Mensagem vazia."}), 400

    resposta, intencao = rotear_mensagem(pergunta_usuario)
    print(f"Intenção: {intencao} | Resposta: {resposta[:50]}...")
    
    return jsonify({"resposta": resposta})


# --- INICIALIZAÇÃO DO SERVIDOR ---
def inicializar_aplicacao():
    """Função para configurar todos os componentes de IA e Dados antes de iniciar o Flask."""
    global METRICAS_SBLOCK, DB_SBLOCK, EMBEDDINGS, LLM_RAG, LLM_ROTEADOR, LLM_COM_SCHEMA

    # 1. Carrega Métricas de BI
    METRICAS_SBLOCK = carregar_e_calcular_metricas_bi()

    # 2. Inicializa LLM/Embeddings
    if not API_KEY:
        raise ValueError("A chave GEMINI_API_KEY não foi encontrada no arquivo .env.")

    EMBEDDINGS = GoogleGenerativeAIEmbeddings(model="text-embedding-004", google_api_key=API_KEY)
    LLM_ROTEADOR = ChatGoogleGenerativeAI(model=LLM_MODEL, google_api_key=API_KEY)
    LLM_RAG = ChatGoogleGenerativeAI(model=LLM_MODEL, google_api_key=API_KEY)
    
    # 3. Cria o Roteador Estruturado
    LLM_COM_SCHEMA = LLM_ROTEADOR.with_structured_output(IntencaoDoUsuario)

    # 4. Cria ou Carrega a Base de Dados RAG
    DB_SBLOCK = criar_ou_carregar_base_de_conhecimento()
    
    print("🤖 Servidor de Chatbot IA pronto para uso!")


if __name__ == '__main__':
    inicializar_aplicacao()
    # Roda o servidor Flask na porta 5000 (ideal para Codespaces)
    app.run(host='0.0.0.0', port=5000)