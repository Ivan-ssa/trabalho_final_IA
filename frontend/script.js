// /frontend/script.js

// 🚨 CORREÇÃO: Usamos API_BASE_URL para o link do Codespaces (Porta 5000)
const API_BASE_URL = 'http://localhost:5000'; 

// A API_URL final aponta para a rota específica do Flask
const API_URL = API_BASE_URL + '/api/chat';


function appendMessage(sender, message) {
    const chatBox = document.getElementById('chat-box');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}`;
    // Permite quebra de linha no HTML
    msgDiv.innerHTML = message.replace(/\n/g, '<br>'); 
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight; // Scroll automático
}

async function sendMessage() {
    const userInput = document.getElementById('user-input');
    const mensagem = userInput.value.trim();

    if (mensagem === "") return;

    appendMessage('user', mensagem);
    userInput.value = '';

    try {
        const response = await fetch(API_URL, { // API_URL agora está correto!
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ mensagem: mensagem }),
        });

        if (!response.ok) {
            // Se a API retornar um erro HTTP (400, 500), mostra no chat
            const errorText = await response.text();
            throw new Error(`Erro HTTP: ${response.status} - ${errorText}`);
        }

        const data = await response.json();
        
        // Exibe a resposta do servidor Python
        appendMessage('bot', data.resposta);

    } catch (error) {
        console.error('Erro ao conectar com o Backend:', error);
        appendMessage('bot', '❌ Desculpe, o servidor de IA não está respondendo. Verifique se o app.py está rodando sem erros.');
    }
}