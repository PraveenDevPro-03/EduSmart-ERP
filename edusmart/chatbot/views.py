from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from .models import ChatMessage
from django.contrib import messages

try:
    chatbot = ChatBot(
        'EduSmartBot',
        storage_adapter='chatterbot.storage.SQLStorageAdapter',
        database_uri='sqlite:///database.sqlite3'
    )
    trainer = ListTrainer(chatbot)
    trainer.train([
        "What is EduSmart ERP?", "EduSmart ERP is a university-level platform for quizzes, video learning, and academic management.",
        "How do I take a quiz?", "Go to the Quizzes section, select a quiz, and answer the questions provided.",
        "Where can I find videos?", "Visit the Video Learning section to browse educational videos uploaded by teachers.",
    ])
except Exception as e:
    print(f"Chatbot initialization failed: {e}")
    chatbot = None

@login_required
def chatbot_view(request):
    if not chatbot:
        messages.error(request, "Chatbot is unavailable due to setup issues. Please contact the administrator.")
        return render(request, 'chatbot/chatbot.html', {'messages': [], 'sample_questions': []})

    if request.method == 'POST':
        message = request.POST.get('message')
        try:
            response = str(chatbot.get_response(message))
            ChatMessage.objects.create(
                user=request.user,
                message=message,
                response=response
            )
        except Exception as e:
            response = "Sorry, I couldn't process your request. Try again later."
            messages.error(request, f"Chatbot error: {e}")
        messages = ChatMessage.objects.filter(user=request.user).order_by('timestamp')
        return render(request, 'chatbot/chatbot.html', {'messages': messages, 'new_response': response})

    messages = ChatMessage.objects.filter(user=request.user).order_by('timestamp')
    sample_questions = [
        "What is EduSmart ERP?",
        "How do I take a quiz?",
        "Where can I find videos?"
    ]
    return render(request, 'chatbot/chatbot.html', {'messages': messages, 'sample_questions': sample_questions})