from django.urls import path
from . import views

app_name = 'learning'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('learn/<int:enrollment_id>/', views.learn, name='learn'),
    path('learn/<int:enrollment_id>/<int:lesson_id>/', views.learn, name='learn_lesson'),
    path('lesson/<int:lesson_id>/complete/', views.mark_lesson_complete, name='mark_complete'),
]
