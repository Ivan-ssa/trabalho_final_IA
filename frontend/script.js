// /frontend/script.js


// Esta é a ÚNICA ativa agora para deploy:
const API_BASE_URL = 'https://trabalho-final-ia.onrender.com';

const API_URL = API_BASE_URL + '/api/chat';


function appendMessage(sender, message) {
    const chatBox = document.getElementById('chat-box');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}`;
    //O { breaks: true } garante que o "enter" vire uma quebra de linha "<br>"
    msgDiv.innerHTML = marked.parse(message, { breaks: true }); 
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

// Elementos
const toggleBtn = document.getElementById('toggle-chat-btn');
const closeBtn = document.getElementById('close-chat-btn');
const chatWidget = document.getElementById('chat-widget');

const themeBtn = document.getElementById('theme-toggle');
        const themeIcon = themeBtn.querySelector('i');
        const body = document.body;

        // 1. Verificar se já existe preferência salva
        const savedTheme = localStorage.getItem('sblock-theme');
        
        // Se tiver salvo 'dark', aplica imediatamente
        if (savedTheme === 'dark') {
            body.classList.add('dark-mode');
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
        }

        // 2. Evento de Clique
        themeBtn.addEventListener('click', () => {
            body.classList.toggle('dark-mode');
            
            // Troca o ícone e salva
            if (body.classList.contains('dark-mode')) {
                themeIcon.classList.remove('fa-moon');
                themeIcon.classList.add('fa-sun');
                localStorage.setItem('sblock-theme', 'dark');
            } else {
                themeIcon.classList.remove('fa-sun');
                themeIcon.classList.add('fa-moon');
                localStorage.setItem('sblock-theme', 'light');
            }
        });
        // Header scroll effect
        window.addEventListener('scroll', function() {
            const header = document.getElementById('header');
            if (window.scrollY > 50) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });

        // Mobile menu toggle
        const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
        const header = document.getElementById('header');
        
        mobileMenuBtn.addEventListener('click', function() {
            header.classList.toggle('mobile-menu-open');
        });

        // Form tabs
        const tabs = document.querySelectorAll('.tab');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', function() {
                tabs.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
            });
        });

        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                
                const targetId = this.getAttribute('href');
                if (targetId === '#') return;
                
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - 100,
                        behavior: 'smooth'
                    });
                    
                    // Close mobile menu if open
                    header.classList.remove('mobile-menu-open');
                }
            });
        });

        // Testimonial slider auto-scroll
        const testimonialSlider = document.querySelector('.testimonial-slider');
        const testimonials = document.querySelectorAll('.testimonial');
        
        if (testimonials.length > 0) {
            let currentIndex = 0;
            const testimonialWidth = testimonials[0].offsetWidth + 30; // width + gap
            
            setInterval(() => {
                currentIndex = (currentIndex + 1) % testimonials.length;
                testimonialSlider.scrollTo({
                    left: currentIndex * testimonialWidth,
                    behavior: 'smooth'
                });
            }, 5000);
        }

        // BlockGuard modal controls
        const blockguardModal = document.getElementById('blockguard-modal');
        const blockguardBtn = document.getElementById('btn-fale-blockguard');
        const blockguardClose = document.getElementById('close-blockguard-modal');

        const toggleBlockguardModal = (show) => {
            if (!blockguardModal) return;
            blockguardModal.classList.toggle('active', show);
            blockguardModal.setAttribute('aria-hidden', String(!show));
            body.style.overflow = show ? 'hidden' : '';
        };

        if (blockguardBtn) {
            blockguardBtn.addEventListener('click', (event) => {
                event.preventDefault();
                toggleBlockguardModal(true);
            });
        }

        if (blockguardClose) {
            blockguardClose.addEventListener('click', () => toggleBlockguardModal(false));
        }

        if (blockguardModal) {
            blockguardModal.addEventListener('click', (event) => {
                if (event.target === blockguardModal) {
                    toggleBlockguardModal(false);
                }
            });
        }

        document.addEventListener('keydown', (event) => {
            if (
                event.key === 'Escape' &&
                blockguardModal &&
                blockguardModal.classList.contains('active')
            ) {
                toggleBlockguardModal(false);
            }
        });

        // Modal chat input helpers
        const chatInput = document.getElementById('user-input');
        const chatSendBtn = document.getElementById('send-btn');

        if (chatSendBtn) {
            chatSendBtn.addEventListener('click', () => {
                sendMessage();
            });
        }

        if (chatInput) {
            chatInput.addEventListener('keypress', (event) => {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    chatSendBtn?.click();
                }
            });
        }