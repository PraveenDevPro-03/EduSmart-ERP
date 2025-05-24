from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Quiz, Question, QuizResult
from accounts.models import CustomUser
from django.db.models import Avg, Count
from django.contrib import messages

@login_required
def create_quiz(request):
    if request.user.user_type != 'teacher' and not request.user.is_staff:
        messages.error(request, 'Only teachers can create quizzes.')
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        subject = request.POST.get('subject', '')  # New field
        question_count = int(request.POST.get('question_count', 0))
        if not title or question_count < 1:
            messages.error(request, 'Quiz title and at least one question are required.')
            return render(request, 'quizzes/create_quiz.html')
        
        quiz = Quiz.objects.create(
            title=title,
            description=description,
            subject=subject,
            created_by=request.user
        )
        for i in range(question_count):
            text = request.POST.get(f'questions[{i}][text]')
            options = [
                request.POST.get(f'questions[{i}][options][0]'),
                request.POST.get(f'questions[{i}][options][1]'),
                request.POST.get(f'questions[{i}][options][2]'),
                request.POST.get(f'questions[{i}][options][3]'),
            ]
            correct = request.POST.get(f'questions[{i}][correct]')
            if text and all(options) and correct is not None:
                try:
                    correct_option = int(correct)
                    if not (0 <= correct_option < len(options)):
                        raise ValueError("Invalid correct option index")
                    Question.objects.create(
                        quiz=quiz,
                        text=text,
                        options=options,
                        correct_option=correct_option
                    )
                except (ValueError, TypeError):
                    messages.error(request, f'Invalid data for question {i+1}.')
                    quiz.delete()
                    return render(request, 'quizzes/create_quiz.html')
            else:
                messages.error(request, f'Missing data for question {i+1}.')
                quiz.delete()
                return render(request, 'quizzes/create_quiz.html')
        messages.success(request, 'Quiz created successfully!')
        return redirect('accounts:dashboard')
    return render(request, 'quizzes/create_quiz.html')

@login_required
def attempt_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.user.user_type != 'student':
        messages.error(request, 'Only students can attempt quizzes.')
        return redirect('accounts:dashboard')
    
    if QuizResult.objects.filter(quiz=quiz, user=request.user).exists():
        messages.error(request, 'You have already attempted this quiz.')
        return redirect('accounts:dashboard')
    
    questions = quiz.questions.all()
    question_data = []
    for question in questions:
        options = question.options
        print(f"Question {question.id} text: {question.text}")
        print(f"Question {question.id} options: {options}")
        if not isinstance(options, list) or len(options) < 2 or not all(isinstance(opt, str) for opt in options):
            messages.error(request, f'Invalid options for question: {question.text}')
            return redirect('accounts:dashboard')
        indexed_options = [(str(index), str(option)) for index, option in enumerate(options)]
        question_data.append({
            'question_id': question.id,
            'question_text': str(question.text),
            'indexed_options': indexed_options
        })
    print("Question data:", question_data)
    
    if request.method == 'POST':
        score = 0
        total_questions = questions.count()
        for question in questions:
            selected_option = request.POST.get(f'question_{question.id}')
            if selected_option is not None:
                try:
                    selected_index = int(selected_option)
                    if selected_index == question.correct_option:
                        score += 1
                except ValueError:
                    continue
        percentage = (score / total_questions * 100) if total_questions > 0 else 0
        QuizResult.objects.create(
            quiz=quiz,
            user=request.user,
            score=percentage
        )
        messages.success(request, f'You scored {percentage}%!')
        return redirect('accounts:dashboard')
    
    return render(request, 'quizzes/attempt_quiz.html', {
        'quiz': quiz,
        'question_data': question_data
    })

@login_required
def quiz_list(request):
    if request.user.user_type != 'student':
        messages.error(request, 'Only students can view available quizzes.')
        return redirect('accounts:dashboard')
    
    attempted_quiz_ids = QuizResult.objects.filter(user=request.user).values_list('quiz_id', flat=True)
    quizzes = Quiz.objects.filter(created_by__user_type='teacher').exclude(id__in=attempted_quiz_ids)
    
    subjects = quizzes.values('subject').distinct()
    quiz_data = []
    for subject in subjects:
        subject_name = subject['subject'] or 'Uncategorized'
        subject_quizzes = quizzes.filter(subject=subject_name)
        quiz_data.append({
            'subject': subject_name,
            'quizzes': subject_quizzes
        })
    
    return render(request, 'quizzes/quiz_list.html', {
        'quiz_data': quiz_data
    })

@login_required
def leaderboard(request):
    if request.user.user_type == 'student' and not request.user.is_staff:
        messages.error(request, 'Only teachers and admins can view the leaderboard.')
        return redirect('accounts:dashboard')
    leaderboard = CustomUser.objects.filter(user_type='student').annotate(
        total_score=Avg('quizresult__score'),
        quizzes_completed=Count('quizresult')
    ).order_by('-total_score')[:10]
    overall = QuizResult.objects.aggregate(
        avg_score=Avg('score'),
        completion_rate=Count('id') / CustomUser.objects.filter(user_type='student').count() * 100
    )
    return render(request, 'quizzes/leaderboard.html', {
        'leaderboard': leaderboard,
        'overall': overall
    })

@login_required
def student_performance(request):
    if request.user.user_type != 'student':
        messages.error(request, 'Only students can view their performance.')
        return redirect('accounts:dashboard')
    
    results = QuizResult.objects.filter(user=request.user).order_by('completed_at')
    quizzes_completed = results.count()
    avg_score = results.aggregate(avg_score=Avg('score'))['avg_score'] or 0
    
    # Prepare data for graph
    scores = [float(result.score) for result in results]
    labels = [f"{result.quiz.title} ({result.completed_at.strftime('%b %d, %Y')})" for result in results]
    subjects = [result.quiz.subject or 'Uncategorized' for result in results]
    
    context = {
        'quizzes_completed': quizzes_completed,
        'avg_score': round(avg_score, 2),
        'scores': scores,
        'labels': labels,
        'subjects': subjects,
        'videos_watched': 0,  # Update with actual logic if tracking
        'chatbot_interactions': 0,  # Update with actual logic if tracking
    }
    return render(request, 'quizzes/student_performance.html', context)