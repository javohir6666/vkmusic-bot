from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('dashboard/', views.dashboard, name='dasboard'),
    path('download/<int:link_id>/', views.download, name='download'),
]
