# 🛡️ BlockGuard IA - Assistente Virtual SBlock

> Solução de Inteligência Artificial Generativa (RAG) para atendimento automatizado de seguros, focada no público jovem e 100% digital.

![Status](https://img.shields.io/badge/Status-Funcional-brightgreen) ![Python](https://img.shields.io/badge/Backend-Python%20Flask-blue) ![IA](https://img.shields.io/badge/IA-Google%20Gemini-orange)

## 📋 Sobre o Projeto

A **BlockGuard** é uma assistente virtual desenvolvida para a **SBlock Seguros**. Diferente de chatbots comuns, ela utiliza uma arquitetura híbrida:
1.  **RAG (Retrieval-Augmented Generation):** Lê o PDF da apólice para responder dúvidas contratuais com precisão.
2.  **Analytics (BI):** Processa dados históricos (CSV) para fornecer métricas financeiras e de risco em tempo real.

### Principais Funcionalidades
* 💬 **Chat Inteligente:** Respostas naturais via Google Gemini.
* 🌑 **Dark Mode:** Interface acessível e confortável para uso noturno.
* 📝 **Formatação Rica:** Suporte a Markdown (negrito, listas) para facilitar a leitura.
* 📊 **Análise de Dados:** Consulta valores de franquia e histórico de sinistros.

---

## 🚀 Como rodar o projeto localmente

Siga o passo a passo abaixo para configurar o ambiente na sua máquina.

### Pré-requisitos
* **Python 3.10+** instalado.
* **Git** instalado.
* Uma chave de API do Google (Gemini).

### 1. Clonar o Repositório
Abra o terminal e rode:
```bash
git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
cd trabalho_final_IA

2. Configurar o Backend (Python)
⚠️ Importante: Não pule a etapa do Ambiente Virtual para evitar conflitos.

Entre na pasta do backend:

Bash

cd backend
Crie e ative o ambiente virtual:

No Windows (Powershell/CMD):

PowerShell

python -m venv venv
.\venv\Scripts\activate
No Windows (Git Bash):

Bash

python -m venv venv
source venv/Scripts/activate
No Linux/Mac:

Bash

python3 -m venv venv
source venv/bin/activate
Você saberá que funcionou quando aparecer (venv) no início da linha do terminal.

Instale as dependências:

Bash

pip install -r requirements.txt
3. Configurar as Chaves de Acesso (.env)
O projeto precisa de uma chave de API para funcionar.

Crie um arquivo chamado .env dentro da pasta backend.

Adicione a seguinte linha dentro dele:

Snippet de código

GEMINI_API_KEY=sua_chave_do_google_aqui
Não tem uma chave? Gere gratuitamente em: Google AI Studio

4. Rodar o Servidor
Ainda no terminal do backend (com a venv ativa), inicie a aplicação:

Bash

python app.py
O terminal deve exibir: Running on http://127.0.0.1:5000. Mantenha esse terminal aberto.

5. Acessar o Frontend (Interface)
Navegue até a pasta frontend do projeto.

Abra o arquivo index.html no seu navegador preferido (Chrome, Edge, Firefox).

Pronto! A BlockGuard já pode ser utilizada.

🛠️ Tecnologias Utilizadas
Backend: Python, Flask, LangChain, ChromaDB.

IA: Google Gemini Pro (langchain-google-genai).

Processamento de Arquivos: PyPDF (Leitura de Apólices), Pandas (Análise de CSV).

Frontend: HTML5, CSS3 (Variáveis CSS, Flexbox), JavaScript Vanilla.

Bibliotecas JS: Marked.js (Renderização de Markdown).

🐛 Solução de Problemas Comuns
Erro: ModuleNotFoundError

Causa: Você provavelmente não ativou a venv antes de instalar os requisitos.

Solução: Delete a pasta venv, crie novamente, ative e rode o pip install.

Erro: Google API Key not found

Causa: O arquivo .env não foi criado ou está com o nome errado.

Solução: Verifique se o arquivo se chama exatamente .env (sem .txt no final) e está na pasta backend.

👨‍💻 Autores
André 
Ivan 