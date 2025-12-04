# 🛡️ BlockGuard IA – Assistente Virtual SBlock

Solução de Inteligência Artificial Generativa (RAG) para atendimento automatizado de seguros, focada no público jovem e 100% digital.

---

## 🔰 Tecnologias Utilizadas

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-AI-4285F4?style=for-the-badge&logo=google&logoColor=white)
![RAG](https://img.shields.io/badge/RAG-Retrieval%20Augmented%20Generation-6A1B9A?style=for-the-badge)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analytics-150458?style=for-the-badge&logo=pandas)

## 🗂️ Infra & Ferramentas
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-Deploy-000000?style=for-the-badge&logo=vercel)
![VSCode](https://img.shields.io/badge/VSCode-Editor-007ACC?style=for-the-badge&logo=visual-studio-code&logoColor=white)

## 📊 Processamento de Dados
![CSV Processing](https://img.shields.io/badge/CSV-Analytics%20BI-FFB300?style=for-the-badge&logo=readdotcsv&logoColor=white)
![PDF Parsing](https://img.shields.io/badge/PDF-RAG%20Parsing-E53935?style=for-the-badge&logo=adobeacrobatreader&logoColor=white)

## 🚀 Status do Projeto
![Status](https://img.shields.io/badge/Status-In%20Development-yellow?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

📋 Sobre o Projeto

A BlockGuard é uma assistente virtual desenvolvida para a SBlock Seguros.
Diferente de chatbots comuns, ela utiliza uma arquitetura híbrida:

RAG (Retrieval-Augmented Generation): Lê PDFs da apólice para respostas contratuais precisas.

Analytics (BI): Processa dados CSV para gerar métricas financeiras e de risco em tempo real.

⭐ Principais Funcionalidades

💬 Chat Inteligente usando Google Gemini

🌑 Dark Mode moderno e confortável

📝 Suporte a Markdown nas respostas

📊 Análise de Dados (franquias, históricos de sinistros)

📂 Leitura de PDFs com PyPDF

🚀 Como rodar o projeto localmente
✔️ Pré-requisitos

Python 3.10+

Git instalado

Chave de API do Google Gemini

📥 1. Clonar o Repositório
git clone https://github.com/seu-usuario/seu-repositorio.git
cd trabalho_final_IA

⚙️ 2. Configurar o Backend (Python)

⚠️ Importante: Não pule a criação da venv para evitar conflitos!

Entrar no backend:
cd backend

Criar e ativar o ambiente virtual:
Windows (PowerShell / CMD)
python -m venv venv
.\venv\Scripts\activate

Windows (Git Bash)
python -m venv venv
source venv/Scripts/activate

Linux / Mac
python3 -m venv venv
source venv/bin/activate


Você saberá que funcionou quando aparecer (venv) no início da linha.

Instalar dependências
pip install -r requirements.txt

🔐 3. Configurar a Chave de Acesso (.env)

Crie um arquivo chamado .env dentro da pasta backend e adicione:

GEMINI_API_KEY=sua_chave_do_google_aqui


Se ainda não tem uma chave → Google AI Studio.

▶️ 4. Rodar o Servidor Backend
python app.py


Se tudo estiver OK, aparecerá:

Running on http://127.0.0.1:5000


Mantenha essa janela aberta.

🖥️ 5. Acessar o Frontend

Vá até a pasta frontend

Abra o arquivo index.html no navegador (Chrome, Edge, Firefox)

Pronto! 🎉
A BlockGuard estará funcionando localmente.

---

🐛 Solução de Problemas Comuns
❌ ModuleNotFoundError

Causa: A venv não foi ativada antes do pip install.
Solução:

Apague a pasta venv

Crie novamente

Ative

Rode pip install -r requirements.txt

❌ Google API Key not found

Causa: O .env está faltando ou com nome errado.
Solução:

Verifique se o nome é exatamente .env

Confira se está na pasta backend

👨‍💻 Autores

André

Ivan

