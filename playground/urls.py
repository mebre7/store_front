from django.urls import path
from . import views

# URL Conf
urlpatterns = [
    path('hello/', views.say_hello, name='say_hello')
]