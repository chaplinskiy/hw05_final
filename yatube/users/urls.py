from django.urls import path
from users import views

urlpatterns = [
    # path() для страницы регистрации нового пользователя
    # её полный адрес будет auth/signup/, но префикс auth/ обрабатывается
    # в головном urls.py
    path('signup/', views.SignUp.as_view(), name='signup')
]
