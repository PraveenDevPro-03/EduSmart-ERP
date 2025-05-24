


from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('messages/', views.message_inbox, name='message_inbox'),
    path('messages/send/', views.send_message, name='send_message'),
    path('messages/reply/<int:message_id>/', views.reply_message, name='reply_message'),
    path('verify-email/<str:uidb64>/<str:token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:uidb64>/<str:token>/', views.reset_password, name='reset_password'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('toggle-user-status/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('create-sub-admin/', views.create_sub_admin, name='create_sub_admin'),
    path('generate-admin-token/', views.generate_admin_token, name='generate_admin_token'),
    path('conversation/<int:message_id>/', views.conversation_detail, name='conversation_detail'),
]