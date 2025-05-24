document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;
    const sidebar = document.querySelector('aside');
    const toggleSidebar = document.createElement('button');
    toggleSidebar.innerHTML = '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>';
    toggleSidebar.className = 'toggle-sidebar fixed top-4 left-4 z-50 text-gray-700 hidden';
    document.body.appendChild(toggleSidebar);

    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    body.className = `theme-${savedTheme}`;
    themeToggle.value = savedTheme;

    // Theme toggle
    themeToggle.addEventListener('change', () => {
        const newTheme = themeToggle.value;
        body.className = `theme-${newTheme}`;
        localStorage.setItem('theme', newTheme);
    });

    // Mobile sidebar toggle
    toggleSidebar.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });

    // Form validation
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', (e) => {
            const requiredInputs = form.querySelectorAll('[required]');
            let valid = true;
            requiredInputs.forEach(input => {
                if (!input.value.trim()) {
                    valid = false;
                    input.classList.add('border-red-500');
                } else {
                    input.classList.remove('border-red-500');
                }
            });
            if (!valid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });

    // Dynamic charts for student dashboard
    const ctxDonut = document.getElementById('donutChart');
    if (ctxDonut) {
        fetch('/quizzes/student-performance/')
            .then(response => response.json())
            .then(data => {
                new Chart(ctxDonut, {
                    type: 'doughnut',
                    data: {
                        labels: ['Quizzes Completed', 'Videos Watched', 'Chatbot Interactions'],
                        datasets: [{
                            data: [data.quizzes_completed, data.videos_watched, data.chatbot_interactions],
                            backgroundColor: ['#2563eb', '#10b981', '#f59e0b'],
                            borderColor: ['#fff'],
                            borderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'top',
                                labels: { color: body.classList.contains('theme-dark') || body.classList.contains('theme-blue') ? '#f3f4f6' : '#1f2937' }
                            }
                        }
                    }
                });
            });
    }

    const ctxLine = document.getElementById('lineChart');
    if (ctxLine) {
        fetch('/quizzes/student-performance/')
            .then(response => response.json())
            .then(data => {
                new Chart(ctxLine, {
                    type: 'line',
                    data: {
                        labels: data.months || ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
                        datasets: [{
                            label: 'Quiz Scores',
                            data: data.scores || [70, 65, 85, 90, 95],
                            borderColor: '#2563eb',
                            backgroundColor: 'rgba(37, 99, 235, 0.2)',
                            fill: true,
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                labels: { color: body.classList.contains('theme-dark') || body.classList.contains('theme-blue') ? '#f3f4f6' : '#1f2937' }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: { color: body.classList.contains('theme-dark') || body.classList.contains('theme-blue') ? '#f3f4f6' : '#1f2937' }
                            },
                            x: {
                                ticks: { color: body.classList.contains('theme-dark') || body.classList.contains('theme-blue') ? '#f3f4f6' : '#1f2937' }
                            }
                        }
                    }
                });
            });
    }
});






document.addEventListener('DOMContentLoaded', () => {
    // Chatbot Popup Toggle
    const chatIcon = document.getElementById('chat-icon');
    const chatPopup = document.getElementById('chat-popup');
    const closeChat = document.getElementById('close-chat');
    const chatSound = new Audio('/static/audio/chime.mp3'); // Load sound

    if (chatIcon && chatPopup && closeChat) {
        console.log('Chat elements found:', { chatIcon, chatPopup, closeChat });
        chatIcon.addEventListener('click', () => {
            console.log('Chat icon clicked');
            // Play sound
            chatSound.play().catch(error => {
                console.error('Sound playback failed:', error);
            });
            chatPopup.classList.toggle('hidden');
            chatPopup.classList.toggle('translate-x-full');
            chatPopup.classList.toggle('scale-95');
            chatPopup.classList.toggle('opacity-0');
        });

        closeChat.addEventListener('click', () => {
            console.log('Close chat clicked');
            chatPopup.classList.add('hidden');
            chatPopup.classList.add('translate-x-full');
            chatPopup.classList.add('scale-95');
            chatPopup.classList.add('opacity-0');
        });
    } else {
        console.error('Chat elements missing:', { chatIcon, chatPopup, closeChat });
    }

    // Theme Toggle
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('change', (e) => {
            document.body.classList.remove('theme-light', 'theme-dark', 'theme-blue');
            document.body.classList.add(`theme-${e.target.value}`);
            document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
        });
    }
});