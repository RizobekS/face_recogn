from django.urls import path
from .views import *

app_name = 'face'

urlpatterns = [
    path('', full_registration, name='registration'),
    path('face-check-in/', face_check_in, name='face_check_in'),
    path('success/<int:id>/', success_page, name='success-page'),
]