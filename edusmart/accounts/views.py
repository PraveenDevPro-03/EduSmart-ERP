from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import CustomUserCreationForm, ProfileUpdateForm,SubAdminCreationForm 
from .models import CustomUser, Message, AdminInviteToken
from django.contrib.admin.views.decorators import staff_member_required
from quizzes.models import Quiz, QuizResult
from learning.models import Video
from django.db.models import Avg, Count, Q
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import Paginator
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
from .permissions import main_admin_required, admin_required

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp) + str(user.is_email_verified)

account_activation_token = AccountActivationTokenGenerator()

def chatbot_view(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        clear_history = request.POST.get('clear_history')
        
        if clear_history:
            request.session['chat_history'] = []
            return redirect('accounts:chatbot')
        
        if message:
            chat_history = request.session.get('chat_history', [])
            ai_response = f"Mock response to: {message}"
            chat_history.append({'user_message': message, 'ai_response': ai_response})
            request.session['chat_history'] = chat_history[:50]
            return redirect('accounts:chatbot')
    
    chat_history = request.session.get('chat_history', [])
    return render(request, 'chatbot.html', {'chat_history': chat_history})

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            token = account_activation_token.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            verification_url = request.build_absolute_uri(
                reverse('accounts:verify_email', kwargs={'uidb64': uid, 'token': token})
            )
            subject = 'Verify Your EduSmart ERP Account'
            html_content = render_to_string('accounts/email_verification.html', {
                'user': user,
                'verification_url': verification_url,
            })
            text_content = render_to_string('accounts/email_verification.txt', {
                'user': user,
                'verification_url': verification_url,
            })
            email = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                headers={'Reply-To': settings.DEFAULT_FROM_EMAIL, 'X-Priority': '1'},
            )
            email.attach_alternative(html_content, "text/html")
            try:
                email.send(fail_silently=False)
                messages.success(request, 'Please check your email (including spam/junk) to verify your account.')
            except Exception as e:
                messages.error(request, f'Failed to send verification email: {str(e)}. Please try again later.')
                user.delete()
                return redirect('accounts:signup')
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_email_verified = True
        user.is_active = True
        user.save()
        messages.success(request, 'Your email has been verified! You can now log in.')
        return redirect('accounts:login')
    else:
        messages.error(request, 'The verification link is invalid or has expired.')
        return redirect('accounts:login')

def resend_verification(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email, is_email_verified=False)
            token = account_activation_token.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            verification_url = request.build_absolute_uri(
                reverse('accounts:verify_email', kwargs={'uidb64': uid, 'token': token})
            )
            subject = 'Verify Your EduSmart ERP Account'
            html_content = render_to_string('accounts/email_verification.html', {
                'user': user,
                'verification_url': verification_url,
            })
            text_content = render_to_string('accounts/email_verification.txt', {
                'user': user,
                'verification_url': verification_url,
            })
            email = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                headers={'Reply-To': settings.DEFAULT_FROM_EMAIL, 'X-Priority': '1'},
            )
            email.attach_alternative(html_content, "text/html")
            try:
                email.send(fail_silently=False)
                messages.success(request, 'Verification email resent. Please check your inbox (including spam/junk).')
            except Exception as e:
                messages.error(request, f'Failed to resend verification email: {str(e)}. Please try again later.')
            return redirect('accounts:login')
        except CustomUser.DoesNotExist:
            messages.error(request, 'No unverified user found with this email.')
            return redirect('accounts:login')
    return render(request, 'accounts/resend_verification.html')

def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_email_verified and user.is_active:
                from django.utils import timezone  # Import timezone
                user.last_login = timezone.now()  # Explicitly set last_login
                user.save(update_fields=['last_login'])  # Save to database
                login(request, user)
                messages.success(request, 'Logged in successfully!')
                print(f"User {user.username} logged in at {user.last_login}")  # Debug
                return redirect('accounts:dashboard')
            elif not user.is_email_verified:
                messages.error(request, 'Please verify your email before logging in.')
            else:
                messages.error(request, 'Your account is deactivated. Contact the administrator.')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            token = account_activation_token.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = request.build_absolute_uri(
                reverse('accounts:reset_password', kwargs={'uidb64': uid, 'token': token})
            )
            subject = 'Reset Your EduSmart ERP Password'
            html_content = render_to_string('accounts/password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
            })
            text_content = render_to_string('accounts/password_reset_email.txt', {
                'user': user,
                'reset_url': reset_url,
            })
            email = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                headers={'Reply-To': settings.DEFAULT_FROM_EMAIL, 'X-Priority': '1'},
            )
            email.attach_alternative(html_content, "text/html")
            try:
                email.send(fail_silently=False)
                messages.success(request, 'A password reset link has been sent to your email (check spam/junk).')
            except Exception as e:
                messages.error(request, f'Failed to send password reset email: {str(e)}. Please try again later.')
            return redirect('accounts:login')
        except CustomUser.DoesNotExist:
            messages.error(request, 'No user found with this email address.')
    return render(request, 'accounts/forgot_password.html')

def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            if password1 == password2:
                user.set_password(password1)
                user.save()
                messages.success(request, 'Your password has been reset successfully!')
                return redirect('accounts:login')
            else:
                messages.error(request, 'Passwords do not match.')
        return render(request, 'accounts/reset_password.html')
    else:
        messages.error(request, 'The reset link is invalid or has expired.')
        return redirect('accounts:forgot_password')

@admin_required
def manage_users(request):
    search_query = request.GET.get('search', '')
    user_type_filter = request.GET.get('user_type', '')
    users = CustomUser.objects.all()
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(roll_number__icontains=search_query)
        )
    if user_type_filter:
        users = users.filter(user_type=user_type_filter)

    paginator = Paginator(users.order_by('username'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    user_stats = {}
    for user in page_obj:
        quiz_results = QuizResult.objects.filter(user=user)
        user_stats[user.id] = {
            
            'last_login': user.last_login,
        }

    return render(request, 'accounts/manage_users.html', {
        'page_obj': page_obj,
        'user_stats': user_stats,
        'search_query': search_query,
        'user_type_filter': user_type_filter,
    })

@main_admin_required
def create_sub_admin(request):
    if request.method == 'POST':
        form = SubAdminCreationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.user_type = 'admin'
                user.is_sub_admin = True
                user.is_staff = True
                user.is_email_verified = True
                user.save()
                messages.success(request, f'Sub-admin {user.username} created successfully!')
                return redirect('accounts:manage_users')
            except Exception as e:
                messages.error(request, f'Error creating sub-admin: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SubAdminCreationForm()
    return render(request, 'accounts/create_sub_admin.html', {'form': form})




@admin_required
def edit_user(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('accounts:manage_users')

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {user.username} updated successfully!')
            return redirect('accounts:manage_users')
    else:
        form = ProfileUpdateForm(instance=user, request=request)
    return render(request, 'accounts/edit_user.html', {'form': form, 'editing_user': user})

@admin_required
def toggle_user_status(request, user_id):
    if request.method == 'POST':
        try:
            user = CustomUser.objects.get(id=user_id)
            if user == request.user:
                messages.error(request, 'You cannot deactivate your own account.')
                return redirect('accounts:manage_users')
            user.is_active = not user.is_active
            user.save()
            status = 'activated' if user.is_active else 'deactivated'
            messages.success(request, f'User {user.username} {status} successfully!')
        except CustomUser.DoesNotExist:
            messages.error(request, 'User not found.')
        return redirect('accounts:manage_users')
    return HttpResponseForbidden("Invalid request method.")

@admin_required
def delete_user(request, user_id):
    if request.method == 'POST':
        try:
            user = CustomUser.objects.get(id=user_id)
            if user == request.user:
                messages.error(request, 'You cannot delete your own account.')
                return redirect('accounts:manage_users')
            username = user.username
            user.delete()
            messages.success(request, f'User {username} deleted successfully!')
        except CustomUser.DoesNotExist:
            messages.error(request, 'User not found.')
        return redirect('accounts:manage_users')
    return HttpResponseForbidden("Invalid request method.")

@main_admin_required
def generate_admin_token(request):
    if request.method == 'POST':
        token = get_random_string(32)
        expires_at = timezone.now() + timedelta(days=7)
        AdminInviteToken.objects.create(
            token=token,
            created_by=request.user,
            expires_at=expires_at
        )
        messages.success(request, f'Admin invite token generated: {token}. Share it securely.')
        return render(request, 'accounts/generate_admin_token.html', {'token': token})
    return render(request, 'accounts/generate_admin_token.html')

@login_required
@login_required
def dashboard(request):
    unread_count = Message.objects.filter(receiver=request.user, is_read=False).count()
    if request.user.user_type == 'admin':
        user_count = CustomUser.objects.count()
        quiz_count = Quiz.objects.count()
        video_count = Video.objects.count()
        student_count = CustomUser.objects.filter(user_type='student').count()
        teacher_count = CustomUser.objects.filter(user_type='teacher').count()
        admin_count = CustomUser.objects.filter(user_type='admin').count()
        sub_admin_count = CustomUser.objects.filter(user_type='admin', is_sub_admin=True).count()
        is_main_admin = request.user.user_type == 'admin' and not request.user.is_sub_admin
        user = request.user
        context = {
            'unread_count': unread_count,
            'user_count': user_count,
            'quiz_count': quiz_count,
            'video_count': video_count,
            'student_count': student_count,
            'teacher_count': teacher_count,
            'admin_count': admin_count,
            'sub_admin_count': sub_admin_count,
            'is_main_admin': is_main_admin,
            'last_login': user.last_login,  # Explicitly pass last_login
        }
        if is_main_admin:
            context['active_tokens'] = AdminInviteToken.objects.filter(
                created_by=request.user,
                used=False,
                expires_at__gt=timezone.now()
            ).order_by('-created_at')
        return render(request, 'accounts/admin_dashboard.html', context)
    elif request.user.user_type == 'student':
        quiz_results = QuizResult.objects.filter(user=request.user)
        total_score = quiz_results.aggregate(total_score=Avg('score'))['total_score'] or 0
        quizzes_completed = quiz_results.count()
        videos_watched = Video.objects.filter(id__in=quiz_results.values('quiz__id')).count()
        attempted_quiz_ids = QuizResult.objects.filter(user=request.user).values_list('quiz_id', flat=True)
        available_quizzes = Quiz.objects.filter(created_by__user_type='teacher').exclude(id__in=attempted_quiz_ids)
        return render(request, 'accounts/student_dashboard.html', {
            'unread_count': unread_count,
            'total_score': total_score,
            'quizzes_completed': quizzes_completed,
            'videos_watched': videos_watched,
            'available_quizzes': available_quizzes,
        })
    else:  # Teacher
        quiz_count = Quiz.objects.filter(created_by=request.user).count()
        student_count = CustomUser.objects.filter(user_type='student').count()
        results = QuizResult.objects.filter(quiz__created_by=request.user)
        avg_score = results.aggregate(avg_score=Avg('score'))['avg_score'] or 0
        completion_rate = (results.count() / student_count * 100) if student_count else 0
        videos = Video.objects.filter(uploaded_by=request.user)
        return render(request, 'accounts/teacher_dashboard.html', {
            'unread_count': unread_count,
            'quiz_count': quiz_count,
            'student_count': student_count,
            'avg_score': avg_score,
            'completion_rate': completion_rate,
            'videos': videos,
        })

@login_required
def profile_update(request):
    user_id = request.GET.get('user_id', None)
    if user_id and request.user.user_type == 'admin':
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return HttpResponseForbidden("User not found.")
    else:
        user = request.user

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:manage_users' if request.user.user_type == 'admin' and user_id else 'accounts:dashboard')
    else:
        form = ProfileUpdateForm(instance=user, request=request)
    return render(request, 'accounts/profile.html', {'form': form, 'editing_user': user})

def custom_logout(request):
    logout(request)
    return render(request, 'accounts/logout.html')


@login_required
def reply_message(request, message_id):
    try:
        original_message = Message.objects.get(id=message_id)
        if request.user != original_message.sender and request.user != original_message.receiver:
            messages.error(request, "You are not authorized to reply to this message.")
            return redirect('accounts:message_inbox')
        
        if request.method == 'POST':
            content = request.POST.get('content', '').strip()
            if content:
                receiver = original_message.sender if request.user == original_message.receiver else original_message.receiver
                Message.objects.create(
                    sender=request.user,
                    receiver=receiver,
                    content=content
                )
                messages.success(request, "Reply sent successfully!")
                return redirect('accounts:message_inbox')
            else:
                messages.error(request, "Reply content cannot be empty.")
        
        return render(request, 'accounts/reply_message.html', {'original_message': original_message})
    
    except Message.DoesNotExist:
        messages.error(request, "Message does not exist.")
        return redirect('accounts:message_inbox')




from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from .models import CustomUser, Message
from django.utils import timezone

@login_required
def message_inbox(request):
    # Get all users except the current user for the dropdown
    users = CustomUser.objects.exclude(id=request.user.id).order_by('username')
    # Debug: Print user count
    print(f"Users for dropdown: {users.count()}")
    # Get messages where the user is sender or receiver
    conversations = Message.objects.filter(
        models.Q(sender=request.user) | models.Q(receiver=request.user)
    ).order_by('-timestamp')
    # Mark received messages as read
    unread_count = Message.objects.filter(receiver=request.user, is_read=False).count()
    Message.objects.filter(receiver=request.user, is_read=False).update(is_read=True)
    return render(request, 'accounts/message_inbox.html', {
        'users': users,
        'conversations': conversations,
        'unread_count': unread_count,
        'user': request.user,
    })

@login_required
def send_message(request):
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver')
        content = request.POST.get('content')
        print(f"Form data - receiver: {receiver_id}, content: {content}")  # Debug
        if not receiver_id:
            messages.error(request, "Please select a recipient.")
            return redirect('accounts:message_inbox')
        if not content.strip():
            messages.error(request, "Message content cannot be empty.")
            return redirect('accounts:message_inbox')
        try:
            receiver = CustomUser.objects.get(id=int(receiver_id))
            if receiver == request.user:
                messages.error(request, "You cannot send a message to yourself.")
                return redirect('accounts:message_inbox')
            # Create message
            Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content,
                timestamp=timezone.now(),
                is_read=False
            )
            messages.success(request, f"Message sent to {receiver.username}.")
        except ValueError:
            messages.error(request, "Invalid recipient selected.")
        except CustomUser.DoesNotExist:
            messages.error(request, "Recipient does not exist.")
        except Exception as e:
            messages.error(request, f"Error sending message: {str(e)}")
    return redirect('accounts:message_inbox')

@login_required
def conversation_detail(request, message_id):
    try:
        message = Message.objects.get(id=message_id)
        if message.sender != request.user and message.receiver != request.user:
            messages.error(request, "You don't have permission to view this message.")
            return redirect('accounts:message_inbox')
        # Get all messages between these two users
        conversation = Message.objects.filter(
            models.Q(sender=message.sender, receiver=message.receiver) |
            models.Q(sender=message.receiver, receiver=message.sender)
        ).order_by('timestamp')
        # Mark as read if the user is the receiver
        if message.receiver == request.user and not message.is_read:
            message.is_read = True
            message.save()
        return render(request, 'accounts/conversation_detail.html', {
            'conversation': conversation,
            'other_user': message.sender if message.receiver == request.user else message.receiver,
            'user': request.user,
        })
    except Message.DoesNotExist:
        messages.error(request, "Message not found.")
        return redirect('accounts:message_inbox')