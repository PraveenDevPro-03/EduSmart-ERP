# from django.urls import path
# from . import views

# urlpatterns = [
#     path('create/', views.create_quiz, name='create_quiz'),
#     path('attempt/<int:quiz_id>/', views.attempt_quiz, name='attempt_quiz'),
#     path('leaderboard/', views.leaderboard, name='leaderboard'),
#     path('student-performance/', views.student_performance, name='student_performance'),
# ]

from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_quiz, name='create_quiz'),
    path('attempt/<int:quiz_id>/', views.attempt_quiz, name='attempt_quiz'),
    path('list/', views.quiz_list, name='quiz_list'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('performance/', views.student_performance, name='student_performance'),
]