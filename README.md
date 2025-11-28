# ====================================================================
# GUIA DE EXECUÇÃO: CHATBOT HÍBRIDO SBLOCK
# Ambiente: Terminal Git Bash (Windows)
# ====================================================================

# 1. CLONAGEM E NAVEGAÇÃO
# --------------------------------------------------------------------

# Clone o repositório
git clone https://github.com/Ivan-ssa/trabalho_final_IA.git

# Navegue para o diretório do backend
cd trabalho_final_IA/backend

# 2. CONFIGURAÇÃO DO AMBIENTE VIRTUAL E DEPENDÊNCIAS
# --------------------------------------------------------------------

# Cria e Ativa o Ambiente Virtual (venv)
python -m venv venv
source venv/Scripts/activate 

# Se você estiver em Linux/Mac, o comando é: source venv/bin/activate

# Instala todas as dependências (certifique-se de que Flask-CORS está no requirements.txt)
pip install -r requirements.txt

# 3. CONFIGURAÇÃO DA CHAVE DE API
# --------------------------------------------------------------------

# Edite o arquivo .env (que está na pasta /backend/) e insira a nova chave ativa:
# GEMINI_API_KEY="SUA_CHAVE_DE_API_ATIVA_AQUI"


# 4. EXECUÇÃO DO BACKEND (Terminal 1)
# --------------------------------------------------------------------

# Execute o servidor Flask (Porta 5000)
# Deixe este terminal rodando. Ele carrega a IA, o RAG e os dados CSV.
echo "--- INICIANDO BACKEND (Porta 5000) ---"
python app.py

# 5. EXECUÇÃO DO FRONTEND (Terminal 2)
# --------------------------------------------------------------------

# Abra um NOVO terminal ou aba do Git Bash.
# Ative o venv novamente neste novo terminal: source venv/Scripts/activate

# Navegue para a pasta do frontend
cd ../frontend

# Inicie o servidor HTTP simples (Porta 8000)
# OBS: O servidor Flask já serve a página na 5000, mas esta é uma alternativa de acesso.
echo "--- INICIANDO FRONTEND (Porta 8000) ---"
python -m http.server 8000

# 6. TESTE FINAL
# --------------------------------------------------------------------

# ACESSE O CHAT NO NAVEGADOR (use a porta do servidor Flask):
# http://localhost:5000
