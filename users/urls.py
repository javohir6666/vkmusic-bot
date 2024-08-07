from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
]
