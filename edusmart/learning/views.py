from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Video
from django.db.models import Q  # Import Q directly


from django.contrib import messages
import requests
# from edusmart.settings import AI_API_KEY


@login_required
def upload_video(request):  
    if request.user.user_type != 'teacher':
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        video_id = request.POST.get('video_id')
        description = request.POST.get('description', '')
        
        # Validate inputs
        if not title or not video_id:
            messages.error(request, 'Title and YouTube Video ID are required.')
            return render(request, 'learning/upload_video.html')
        
        # Basic validation for video_id
        if len(video_id) < 11 or len(video_id) > 20:
            messages.error(request, 'Invalid YouTube Video ID.')
            return render(request, 'learning/upload_video.html')
        
        # Save the video
        Video.objects.create(
            title=title,
            video_id=video_id,
            description=description,
            uploaded_by=request.user
        )
        messages.success(request, 'Video uploaded successfully!')
        return redirect('accounts:dashboard')
    
    return render(request, 'learning/upload_video.html')

@login_required
def video_learning(request):
    search_query = request.GET.get('search', '')
    videos = Video.objects.all()
    if request.user.user_type == 'student':
        videos = videos.filter(uploaded_by__user_type='teacher')  # Only teacher-uploaded videos for students
    if search_query:
        videos = videos.filter(
            Q(title__icontains=search_query) |  # Use Q directly
            Q(description__icontains=search_query)
        )
    return render(request, 'learning/video_learning.html', {'videos': videos})


from django.shortcuts import render
from django.contrib import messages
import requests
from edusmart.settings import OPENROUTER_API_KEY

def chatbot(request):
    # Initialize or clear chat history
    if 'chat_history' not in request.session or request.method == 'GET':
        request.session['chat_history'] = []
        request.session.modified = True
        print("Chat history cleared on GET or init")  # Debug

    # EduSmart ERP project context
    project_context = """
    EduSmart ERP is a student ERP portal for managing quizzes, video learning, and performance tracking.
    Features:
    - Teachers create quizzes with subjects (e.g., Math, Science) at /quizzes/create/.
    - Students attempt quizzes at /quizzes/attempt/<quiz_id>/, view performance at /quizzes/performance/, and watch videos at /learning/videos/.
    - Admins manage users and content at /admin/.
    - Quizzes have titles, descriptions, subjects, and questions with JSON options (e.g., ["Option 1", "Option 2", "Option 3", "Option 4"]) and a correct option index (0-3).
    - Quiz results store student scores (0-100%) and completion times.
    - The student dashboard at /dashboard/ shows available quizzes, performance metrics, and quick actions.
    - Teachers view student performance at /quizzes/teacher/performance/.
    - Admins add users at /admin/accounts/customuser/add/.
    """

    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()
        user_type = request.user.user_type if request.user.is_authenticated else 'guest'
        print(f"User message received: {user_message} (User: {request.user.username if request.user.is_authenticated else 'Guest'}, Type: {user_type})")  # Debug
        if user_message:
            try:
                if not OPENROUTER_API_KEY:
                    raise ValueError("OPENROUTER_API_KEY is not set")
                headers = {
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://127.0.0.1:8000",
                    "X-Title": "EduSmart Chatbot"
                }
                system_prompt = f"You are a helpful AI assistant for EduSmart ERP. Use the following context to answer questions about the platform:\n{project_context}\n"
                if user_type == 'student':
                    system_prompt += "Focus on student-related queries, such as quiz attempts, video learning, and performance tracking."
                elif user_type == 'teacher':
                    system_prompt += "Focus on teacher-related queries, such as quiz creation and student performance."
                elif user_type == 'admin':
                    system_prompt += "Focus on admin-related queries, such as user management and content oversight."
                else:
                    system_prompt += "Answer general questions about EduSmart ERP or guide the user to log in for personalized help."

                payload = {
                    "model": "mistralai/mistral-7b-instruct:free",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "max_tokens": 100,  # Reduced for concise output
                    "temperature": 0.7
                }
                print(f"Sending request to OpenRouter API with payload: {payload}")  # Debug
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=10
                )
                response.raise_for_status()
                ai_response = response.json()['choices'][0]['message']['content'].strip()
                print(f"AI response received: {ai_response}")  # Debug

                # Store message in session
                request.session['chat_history'].append({
                    'user_message': user_message,
                    'ai_response': ai_response,
                    'timestamp': str(request.session._get_session_key())
                })
                request.session.modified = True
                print(f"Chat history updated: {request.session['chat_history']}")  # Debug

            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code
                error_message = e.response.text
                if status_code == 401:
                    ai_response = "Authentication error. Please contact support."
                elif status_code == 429:
                    ai_response = "API limit reached. Try again later."
                else:
                    ai_response = "Sorry, I'm having trouble responding."
                print(f"HTTP Error: {status_code} - {error_message}")  # Debug
                request.session['chat_history'].append({
                    'user_message': user_message,
                    'ai_response': ai_response,
                    'timestamp': str(request.session._get_session_key())
                })
                request.session.modified = True
                messages.error(request, ai_response)

            except requests.exceptions.ConnectionError:
                ai_response = "Network error. Check your connection."
                print("Connection Error: Unable to reach OpenRouter API")  # Debug
                request.session['chat_history'].append({
                    'user_message': user_message,
                    'ai_response': ai_response,
                    'timestamp': str(request.session._get_session_key())
                })
                request.session.modified = True
                messages.error(request, ai_response)

            except Exception as e:
                ai_response = "Sorry, I'm having trouble responding."
                print(f"General Error: {str(e)}")  # Debug
                request.session['chat_history'].append({
                    'user_message': user_message,
                    'ai_response': ai_response,
                    'timestamp': str(request.session._get_session_key())
                })
                request.session.modified = True
                messages.error(request, ai_response)

        # Clear chat history if requested
        if 'clear_history' in request.POST:
            request.session['chat_history'] = []
            request.session.modified = True
            print("Chat history cleared via button")  # Debug
            messages.success(request, "Chat history cleared.")

    chat_history = request.session.get('chat_history', [])
    print(f"Rendering template with chat_history: {chat_history}")  # Debug
    return render(request, 'learning/chatbot.html', {
        'chat_history': chat_history
    })

